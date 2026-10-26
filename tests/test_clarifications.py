import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import create_app, db
from app.models import Project, Interview, Requirement, RequirementClarification
from app.agents.requirements_agent import RequirementsAgent
from app.services.requirement_specification import FIELDS

def quality(sufficient=True):
    return {k: {'sufficient': sufficient, 'reason': 'Acción y resultado definidos.' if sufficient else 'Precisar el resultado de la función.'} for k in ('clarity', 'verifiability')}

def all_fields(values):
    return {**{k: [] for k in FIELDS}, 'priority': {'value': 'no_especificada', 'sources': []}, 'actor': {'value': '', 'sources': []}, 'quality': quality(), **values}


class ClarificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(root/'test.db'),
            'UPLOAD_FOLDER': str(root/'uploads'), 'GENERATED_FOLDER': str(root/'generated')})
        self.ctx = self.app.app_context(); self.ctx.push()
        p = Project(name='Tienda'); db.session.add(p); db.session.flush()
        i = Interview(project_id=p.id, transcription='El sistema deberá registrar ventas.')
        db.session.add(i); db.session.flush()
        for code in ['RF-001', 'RF-002']:
            db.session.add(Requirement(project_id=p.id, interview_id=i.id, code=code,
                description='El sistema deberá registrar ventas.', source_excerpt=i.transcription,
                specification=json.dumps({'schema_version': 3, 'fields': {'main_flow': [i.transcription]}})))
        db.session.commit()
        self.interview_id=i.id; self.project_id=p.id
        self.ids=[r.id for r in Requirement.query.order_by(Requirement.id).all()]
        self.client=self.app.test_client()

    def tearDown(self):
        db.session.remove(); db.engine.dispose(); self.ctx.pop(); self.temp.cleanup()

    def upload(self, rid=None, text='Al confirmar, la venta queda guardada.', value=None):
        with patch('app.services.whisper_service.WhisperService') as whisper, patch(
                'app.services.ollama_service.OllamaService.generate_json', return_value=all_fields(value or {'outputs': [1]})):
            whisper.return_value.transcribe.return_value=text
            return self.client.post(f'/requirements/{rid or self.ids[0]}/clarifications',
                data={'audio':(io.BytesIO(b'audio'),'aclaracion.wav')}, content_type='multipart/form-data')

    def test_updates_only_target_and_keeps_original_and_identity(self):
        before=db.session.get(Requirement,self.ids[1]).specification
        self.assertEqual(self.upload().status_code,302)
        i=db.session.get(Interview,self.interview_id)
        self.assertEqual(i.original_transcription,'El sistema deberá registrar ventas.')
        self.assertIn('Aclaración 1 — RF-001',i.transcription)
        self.assertEqual(db.session.get(Requirement,self.ids[1]).specification,before)
        r=db.session.get(Requirement,self.ids[0])
        self.assertEqual(r.code,'RF-001')
        self.assertEqual(next(x for x in r.specification_rows if x['key']=='outputs')['values'],['Al confirmar, la venta queda guardada.'])
        self.assertTrue(next(x for x in r.specification_rows if x['key']=='main_flow')['values'])
        self.assertEqual(RequirementClarification.query.one().status,'applied')
        html=self.client.get(f'/interviews/{i.id}').get_data(as_text=True)
        self.assertIn('Versión 1',html)
        self.assertIn('Aclaración 1',html)
        html=self.client.get(f'/interviews/{i.id}/requirements').get_data(as_text=True)
        self.assertIn('Transcribir y actualizar este RF',html)
        self.assertNotIn('type="checkbox"',html)
        self.assertNotIn('id="project-context"',html)
        self.assertIn('la venta queda guardada',html)

    def test_multiple_requirements_share_consolidated_transcript(self):
        self.upload()
        self.upload(self.ids[1],text='Se muestra la confirmación de la venta.')
        i=db.session.get(Interview,self.interview_id)
        self.assertIn('Aclaración 1 — RF-001',i.transcription)
        self.assertIn('Aclaración 2 — RF-002',i.transcription)
        self.assertEqual(i.transcription.count('Entrevista original'),1)
        self.assertEqual(Requirement.query.count(),2)
        with self.assertRaisesRegex(ValueError,'aclaraciones'):
            RequirementsAgent().process(i.id)

    def test_llm_failure_keeps_audio_text_and_old_rf_then_retry(self):
        before=db.session.get(Requirement,self.ids[0]).specification
        self.upload(value={'outputs':[999]})
        item=RequirementClarification.query.one()
        self.assertEqual(item.status,'pending')
        self.assertTrue(Path(self.app.config['UPLOAD_FOLDER'],item.audio_path).exists())
        self.assertEqual(db.session.get(Requirement,self.ids[0]).specification,before)
        with patch('app.services.ollama_service.OllamaService.generate_json',return_value=all_fields({'outputs':[1]})):
            self.client.post(f'/clarifications/{item.id}/retry')
        self.assertEqual(item.status,'applied')
        self.client.post(f'/clarifications/{item.id}/retry')
        self.assertEqual(RequirementClarification.query.count(),1)

    def test_empty_transcription_leaves_no_orphan_audio(self):
        self.upload(text='')
        self.assertEqual(RequirementClarification.query.count(),0)
        self.assertEqual(list(Path(self.app.config['UPLOAD_FOLDER']).iterdir()),[])
        self.assertIsNone(db.session.get(Interview,self.interview_id).original_transcription)

    def test_invalid_extension_or_fields_rejected(self):
        for data in ({'audio':(io.BytesIO(b'x'),'a.exe')}, {'audio':(io.BytesIO(b'x'),'no_extension')}):
            self.client.post(f'/requirements/{self.ids[0]}/clarifications',data=data)
        self.assertEqual(RequirementClarification.query.count(),0)

    def test_project_delete_removes_clarification_audio_and_records(self):
        self.upload()
        path=Path(self.app.config['UPLOAD_FOLDER'],RequirementClarification.query.one().audio_path)
        self.client.post(f'/projects/{self.project_id}/delete')
        self.assertFalse(path.exists())
        self.assertEqual(RequirementClarification.query.count(),0)

    def test_clarification_is_in_srs_and_retranscription_is_blocked(self):
        from app.agents.srs_agent import SRSAgent
        from app.agents.transcription_agent import TranscriptionAgent
        self.upload()
        i=db.session.get(Interview,self.interview_id)
        r=db.session.get(Requirement,self.ids[0])
        item={k:getattr(r,k) for k in ['code','description','specification','interview_id','source_excerpt']}
        content=SRSAgent()._build_document({'name':'Tienda','interviews':[{'id':i.id,'transcription':i.transcription}]},[item],{})
        self.assertIn('Al confirmar, la venta queda guardada.',content)
        with patch('app.agents.transcription_agent.WhisperService'):
            with self.assertRaisesRegex(ValueError,'versión original'):
                TranscriptionAgent().process(i.id)

    def test_migration_adds_snapshot_without_modifying_original(self):
        from sqlalchemy import create_engine, text, inspect
        from app.schema_migrations import upgrade_requirement_specification
        engine=create_engine('sqlite://')
        with engine.begin() as con:
            con.exec_driver_sql('CREATE TABLE requirement (id INTEGER PRIMARY KEY)')
            con.exec_driver_sql('CREATE TABLE interview (id INTEGER PRIMARY KEY, transcription TEXT)')
            con.exec_driver_sql("INSERT INTO interview VALUES (1, 'Original')")
        upgrade_requirement_specification(engine)
        upgrade_requirement_specification(engine)
        with engine.connect() as con:
            self.assertEqual(con.execute(text('SELECT transcription, original_transcription FROM interview')).one(),('Original',None))
        engine.dispose()

    def test_context_has_separate_page_and_generation_redirect(self):
        page=self.client.get(f'/projects/{self.project_id}/context')
        self.assertEqual(page.status_code,200)
        self.assertIn('Generar contexto académico',page.get_data(as_text=True))
        with patch('app.routes.EnrichmentAgent') as agent:
            response=self.client.post(f'/projects/{self.project_id}/enrich')
            agent.return_value.process_project.assert_called_once_with(self.project_id)
        self.assertTrue(response.location.endswith(f'/projects/{self.project_id}/context'))

    def test_priority_only_clarification_updates_priority_with_evidence(self):
        self.upload(text='Esta función es indispensable.', value={'priority': {'value':'esencial','sources':[1]}})
        req=db.session.get(Requirement,self.ids[0])
        self.assertEqual(req.priority,'esencial')
        self.assertIn('Esta función es indispensable.',req.priority_reason)
        self.assertEqual(RequirementClarification.query.one().status,'applied')
        self.assertEqual(json.loads(RequirementClarification.query.one().fields),['priority'])
        self.assertEqual(db.session.get(Requirement,self.ids[1]).priority,'no_especificada')

    def test_unmentioned_priority_is_preserved(self):
        req=db.session.get(Requirement,self.ids[0]); req.priority='opcional'; req.priority_reason='Anterior'
        db.session.commit()
        self.upload()
        self.assertEqual(req.priority,'opcional')
        self.assertEqual(req.priority_reason,'Anterior')

    def test_explicit_priority_can_be_corrected(self):
        req=db.session.get(Requirement,self.ids[0]); req.priority='esencial'; db.session.commit()
        self.upload(text='Esta función es opcional.',value={'priority':{'value':'opcional','sources':[1]}})
        self.assertEqual(req.priority,'opcional')

    def test_priority_without_evidence_does_not_modify_requirement(self):
        before=db.session.get(Requirement,self.ids[0]).specification
        self.upload(value={'priority':{'value':'esencial','sources':[]}})
        req=db.session.get(Requirement,self.ids[0])
        self.assertEqual(req.priority,'no_especificada')
        self.assertEqual(req.specification,before)
        self.assertEqual(RequirementClarification.query.one().status,'pending')

    def test_actor_only_update_is_supported_and_has_evidence(self):
        self.upload(text='La función la utiliza el bibliotecario.', value={'actor':{'value':'bibliotecario','sources':[1]}})
        req=db.session.get(Requirement,self.ids[0])
        self.assertEqual(req.actor,'bibliotecario')
        self.assertNotIn('Actor',req.pending_fields)
        self.assertIn('Prioridad',req.pending_fields)
        self.upload()
        self.assertEqual(req.actor,'bibliotecario')

    def test_invented_actor_does_not_replace_existing(self):
        req=db.session.get(Requirement,self.ids[0]); req.actor='Dueño'; db.session.commit()
        self.upload(text='La función la utiliza el bibliotecario.',value={'actor':{'value':'Administrador','sources':[1]}})
        self.assertEqual(req.actor,'Dueño')
        self.assertEqual(RequirementClarification.query.one().status,'pending')

    def test_actor_case_articles_and_accents_do_not_block_retry(self):
        text = 'Somos el dueño y el ayudante. La venta queda guardada.'
        # First attempt has a genuinely unsupported role; the saved audio can
        # be retried with supported names written differently from the quote.
        self.upload(text=text, value={'actor': {'value': 'Administrador', 'sources':[1]}, 'outputs':[2]})
        item = RequirementClarification.query.one()
        self.assertEqual(item.status, 'pending')
        with patch('app.services.ollama_service.OllamaService.generate_json', return_value=
                   all_fields({'actor': {'value':'Dueno y Ayudante','sources':[1]}, 'outputs':[2]})):
            self.client.post(f'/clarifications/{item.id}/retry')
        req = db.session.get(Requirement, self.ids[0])
        self.assertEqual(item.status, 'applied')
        self.assertEqual(req.actor, 'Dueno y Ayudante')
        self.assertIn('La venta queda guardada.', next(r for r in req.specification_rows if r['key']=='outputs')['values'])
        self.assertEqual(RequirementClarification.query.count(), 1)

    def test_actor_matching_requires_complete_role_names(self):
        from app.services.clarification_service import actor_matches_evidence
        self.assertTrue(actor_matches_evidence('Dueño, ayudante', ['Somos el dueño y el ayudante.']))
        self.assertFalse(actor_matches_evidence('Administrador y ayudante', ['Somos el dueño y el ayudante.']))
        self.assertFalse(actor_matches_evidence('Administrador', ['Los administradores registran ventas.']))
        self.assertFalse(actor_matches_evidence('el', ['Somos el dueño.']))

    def test_missing_fields_visible_and_complete_state_is_not_validation(self):
        req=db.session.get(Requirement,self.ids[0])
        self.assertIn('Actor',req.pending_fields)
        html=self.client.get(f'/interviews/{self.interview_id}/requirements').get_data(as_text=True)
        self.assertIn('campos por aclarar',html)
        self.assertIn('rf-component-pending',html)
        self.assertIn('Añadir aclaración por audio',html)
        req.actor='Vendedor'; req.priority='esencial'
        req.specification=json.dumps({'schema_version':5,'fields':{k:[req.source_excerpt] for k in FIELDS}, 'quality':quality()})
        db.session.commit()
        self.assertEqual(req.pending_fields,[])


    def test_orchestrator_reuses_clarified_rf_without_retranscribing(self):
        from app.orchestrator.orchestrator import Orchestrator
        self.upload()
        before=[(r.id,r.specification) for r in Requirement.query.order_by(Requirement.id)]
        with patch('app.orchestrator.orchestrator.TranscriptionAgent') as transcription, patch(
                'app.orchestrator.orchestrator.RequirementsAgent') as analysis, patch(
                'app.orchestrator.orchestrator.EnrichmentAgent') as enrichment, patch(
                'app.orchestrator.orchestrator.SRSAgent') as srs:
            srs.return_value.process.return_value={'document_id':42}
            result=Orchestrator().process_interview(self.interview_id)
            self.assertTrue(result['success'])
            transcription.assert_not_called()
            analysis.return_value.process.assert_not_called()
            enrichment.return_value.process_project.assert_called_once_with(self.project_id)
            srs.return_value.process.assert_called_once_with(self.project_id)
        self.assertEqual([(r.id,r.specification) for r in Requirement.query.order_by(Requirement.id)],before)

    def test_orchestrator_without_clarifications_runs_all_agents(self):
        from app.orchestrator.orchestrator import Orchestrator
        with patch('app.orchestrator.orchestrator.TranscriptionAgent') as transcription, patch(
                'app.orchestrator.orchestrator.RequirementsAgent') as analysis, patch(
                'app.orchestrator.orchestrator.EnrichmentAgent'), patch(
                'app.orchestrator.orchestrator.SRSAgent') as srs:
            analysis.return_value.process.return_value=[]
            srs.return_value.process.return_value={'document_id':42}
            self.assertTrue(Orchestrator().process_interview(self.interview_id)['success'])
            transcription.return_value.process.assert_called_once_with(self.interview_id)
            analysis.return_value.process.assert_called_once_with(self.interview_id)


    def test_quality_is_visible_above_fields_without_separate_review(self):
        html = self.client.get(f'/interviews/{self.interview_id}/requirements').get_data(as_text=True)
        self.assertIn('Claridad (sin ambigüedad)', html)
        self.assertIn('Verificabilidad', html)
        self.assertLess(html.index('Atributos del requisito'), html.index('Detalles esenciales'))
        self.assertNotIn('Comprobar ficha con IA', html)
        self.assertEqual(self.client.post(f'/requirements/{self.ids[0]}/review').status_code, 404)
        req = db.session.get(Requirement, self.ids[0])
        self.assertIn('Verificabilidad', req.pending_fields)
        self.assertIn('Guía para preparar la entrevista', html)
        self.assertNotIn('Responder en el audio de este RF', html)
        self.assertEqual(html.count('name="audio"'), 2)
        self.assertTrue(any('resultado exacto' in q for q in req.interview_guidance['verifiability']))

    def test_audio_completes_quality_in_same_call_and_keeps_transcript_elsewhere(self):
        req = db.session.get(Requirement, self.ids[0])
        req.actor = 'Vendedor'; req.priority = 'esencial'
        text = 'Al confirmar, la venta queda guardada. SOLO EN EL HISTORIAL.'
        with patch('app.services.whisper_service.WhisperService') as whisper, patch(
                'app.services.ollama_service.OllamaService.generate_json', return_value=
                all_fields({k: [1] for k in FIELDS})) as model:
            whisper.return_value.transcribe.return_value = text
            self.client.post(f'/requirements/{req.id}/clarifications',
                data={'audio': (io.BytesIO(b'audio'), 'a.wav')}, content_type='multipart/form-data')
        model.assert_called_once()
        self.assertEqual(req.pending_fields, [])
        self.assertFalse(req.ambiguity_detected)
        self.assertTrue(req.verifiable)
        self.assertFalse(any(req.interview_guidance.values()))
        self.assertEqual(RequirementClarification.query.one().status, 'applied')
        html = self.client.get(f'/interviews/{self.interview_id}/requirements').get_data(as_text=True)
        self.assertNotIn('SOLO EN EL HISTORIAL', html)
        self.assertIn('SOLO EN EL HISTORIAL', self.client.get(f'/interviews/{self.interview_id}').get_data(as_text=True))

    def test_quality_does_not_pass_without_required_content(self):
        self.upload(value={'outputs':[1], 'quality':quality()})
        req = db.session.get(Requirement, self.ids[0])
        self.assertFalse(req.verifiable)
        self.assertIn('Verificabilidad', req.pending_fields)
        self.assertIn('Criterios de aceptación', req.verification_reason)

    def test_audio_updates_quality_and_discards_old_review_workflow(self):
        req = db.session.get(Requirement, self.ids[0])
        spec = json.loads(req.specification)
        spec['automatic_review'] = {'status': 'needs_clarification', 'acceptance_issues':['Vieja exigencia']}
        req.specification = json.dumps(spec); db.session.commit()
        self.upload(value={'outputs':[1], 'quality': quality(False)})
        self.assertNotIn('automatic_review', json.loads(req.specification))
        self.assertIn('Claridad (sin ambigüedad)', req.pending_fields)
        self.assertIn('Precisar el resultado', req.ambiguity_reason)

    def test_initial_extraction_includes_quality_without_extra_call(self):
        from unittest.mock import Mock
        from app.services.requirement_specification import extract_specification
        from app.services.requirement_quality import sync_quality
        req = db.session.get(Requirement, self.ids[0])
        model = Mock()
        model.generate_json.return_value = {**{k: [] for k in FIELDS}, 'main_flow':[1], 'quality':quality()}
        spec = extract_specification(model, {'description':req.description, 'source_excerpt':req.source_excerpt}, req.source_excerpt)
        req.specification = json.dumps(spec)
        sync_quality(req)
        model.generate_json.assert_called_once()
        self.assertIn('quality', model.generate_json.call_args.args[1]['required'])
        self.assertFalse(req.verifiable)  # No acceptance evidence yet.
        self.assertIn('Verificabilidad', req.pending_fields)

    def test_quality_normalizes_types_and_does_not_discard_long_explanation(self):
        from app.services.requirement_quality import quality_values
        fields = {k:['Evidencia'] for k in FIELDS}
        raw = {k:{'sufficient':'true','reason':'La acción y su resultado son observables. '*12}
               for k in ('clarity','verifiability')}
        values = quality_values(raw, fields)
        self.assertTrue(all(v['sufficient'] for v in values.values()))
        raw['clarity']['sufficient'] = 'false'
        self.assertFalse(quality_values(raw, fields)['clarity']['sufficient'])

    def test_quality_recovery_across_projects_and_partial_information(self):
        from unittest.mock import Mock
        from app.services.requirement_quality import sync_quality
        for domain, role, function in [('Consultorio','Recepcionista','reservar una cita'),
                                       ('Taller','Mecánico','registrar una reparación'),
                                       ('Escuela','Docente','consultar calificaciones')]:
            with self.subTest(domain=domain):
                project = Project(name=domain); db.session.add(project); db.session.flush()
                quote = f'El sistema deberá {function}. El resultado queda disponible para {role}.'
                interview = Interview(project_id=project.id, transcription=quote)
                db.session.add(interview); db.session.flush()
                req = Requirement(project_id=project.id,interview_id=interview.id,code='RF-001',
                    actor=role,priority='esencial',description=f'El sistema deberá {function}.',
                    source_excerpt=quote,specification=json.dumps({'schema_version':5,
                    'fields':{k:[quote] for k in FIELDS},'quality':{}}))
                db.session.add(req)
                model = Mock()
                model.generate_json.return_value = {'clarity':True,'verifiability':True,
                    'clarity_reason':'La acción está definida.', 'verifiability_reason':'El resultado es observable.'}
                sync_quality(req,llm=model)
                self.assertEqual(req.pending_fields,[])
                model.generate_json.assert_called_once()
                spec = json.loads(req.specification); spec['fields']['outputs']=[]
                req.specification=json.dumps(spec)
                sync_quality(req,llm=model)
                self.assertIn('Resultado esperado',req.pending_fields)
                self.assertIn('Verificabilidad',req.pending_fields)
                self.assertFalse(req.verifiable)

    def test_applied_audio_retries_quality_without_overwriting_fields_or_other_rf(self):
        from unittest.mock import Mock
        from app.services.clarification_service import apply_clarification
        self.upload()
        req=db.session.get(Requirement,self.ids[0])
        before=json.loads(req.specification)['fields']
        other=db.session.get(Requirement,self.ids[1]).specification
        spec=json.loads(req.specification)
        spec['quality']={k:{'sufficient':False,'reason':'La información disponible no permitió determinar este atributo; acláralo junto con la función.'} for k in ('clarity','verifiability')}
        req.specification=json.dumps(spec); db.session.commit()
        model=Mock()
        model.generate_json.return_value={'clarity':True,'clarity_reason':'La función está definida.',
            'verifiability':False,'verifiability_reason':'Faltan ejemplos de aceptación.'}
        apply_clarification(RequirementClarification.query.one(),llm=model)
        self.assertTrue(req.quality_attributes['clarity']['sufficient'])
        self.assertFalse(req.verifiable)
        self.assertEqual(json.loads(req.specification)['fields'],before)
        self.assertEqual(db.session.get(Requirement,self.ids[1]).specification,other)
        self.assertEqual(RequirementClarification.query.count(),1)

    def test_quality_service_error_is_not_reported_as_missing_interview_information(self):
        from unittest.mock import Mock
        from app.services.requirement_quality import sync_quality
        req=db.session.get(Requirement,self.ids[0])
        req.specification=json.dumps({'schema_version':5,'fields':{k:[req.source_excerpt] for k in FIELDS}})
        model=Mock(); model.generate_json.side_effect=TimeoutError()
        sync_quality(req,llm=model)
        self.assertEqual(req.quality_attributes['clarity']['status'],'unavailable')
        self.assertFalse(req.verifiable)
        model.generate_json.assert_called_once()
