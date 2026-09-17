import re
from collections import Counter
import unicodedata
from urllib.parse import quote_plus
from app.mcp.client import MCPClient


class RAGRetriever:
    STOPWORDS = set("el la los las un una unos unas de del al a en con por para y o que su sus este esta como cuando cada tambien ademas debe deben debera puede pueda poder permitir es se mi nuestro nuestra necesitamos necesito quiero queremos tener hacer hola buenos dias gracias sistema software aplicacion plataforma proyecto gestion gestionar".split())
    SOFTWARE_WORDS = {"software", "sistema", "sistemas", "aplicacion", "plataforma", "gestion", "modulo", "registro", "administracion", "system", "systems", "application", "management"}
    # Search synonyms only; never used to create requirements.
    SYNONYMS = {"biblioteca": "library", "bibliotecas": "library", "libros": "books", "prestamos": "loans", "catalogo": "catalog", "inventario": "inventory", "ventas": "sales", "reservas": "reservations", "pacientes": "patients", "estudiantes": "students"}

    def __init__(self):
        self.mcp = MCPClient()

    def retrieve(self, requirement, source_excerpt="", interview_context="", max_results=10):
        domain = self._domain_keywords(interview_context or source_excerpt)
        function = self._requirement_keywords(requirement)
        return self._retrieve(domain, function, max_results)

    def retrieve_project(self, project, max_results=10):
        interviews = " ".join(item.get("transcription") or "" for item in project.get("interviews", []))
        description = project.get("description") or ""
        name = project.get("name") or ""
        domain = self._domain_keywords(f"{description}. {name}. {interviews}")
        concepts = Counter()
        for requirement in project.get("requirements", []):
            concepts.update(self._requirement_keywords(requirement.get("description", "")))
        return self._retrieve(domain, [word for word, count in concepts.most_common(12)], max_results)

    def _retrieve(self, domain, function, max_results):
        specific = " ".join(dict.fromkeys(domain[:3] + function[:5] + ["software"]))
        general = " ".join(dict.fromkeys(domain[:3] + ["sistema", "software"]))
        queries = [specific] + ([general] if domain else [])
        english = [self.SYNONYMS[word] for word in domain if word in self.SYNONYMS]
        if english:
            queries.append(" ".join(dict.fromkeys(english + ["management", "system"])))
        queries = list(dict.fromkeys(queries))
        results, warnings, providers = [], [], []
        for query in queries:
            response = self.mcp.search_academic(query=query, max_results=max_results)
            results.extend(response.get("results") or [])
            warnings.extend(response.get("warnings") or [])
            providers.extend(response.get("providers") or [])
        return {
            "query": " | ".join(queries), "queries": queries, "domain": domain,
            "sources": self._filter_sources(results, domain, function),
            "references": self._filter_sources(results, domain, function, require_abstract=False),
            "providers": list(dict.fromkeys(providers)), "warnings": list(dict.fromkeys(warnings)),
            "scholar_url": "https://scholar.google.com/scholar?q=" + quote_plus(general if domain else specific),
        }

    def _domain_keywords(self, interview):
        beginning = " ".join(re.split(r"(?<=[.!?])\s+", str(interview or ""))[:4])
        words = self._tokens(beginning)
        match = re.search(r"(?:sistema|software|aplicacion|plataforma)\s+(?:de\s+gestion\s+)?(?:de|para)\s+(.+)", self._normalize(beginning))
        if match:
            words = self._tokens(match.group(1)) + words
        return list(dict.fromkeys(word for word in words if word not in self.STOPWORDS and len(word) >= 4 and not self._is_infinitive(word)))[:3]

    def _requirement_keywords(self, requirement):
        return list(dict.fromkeys(word for word in self._tokens(requirement) if word not in self.STOPWORDS and len(word) >= 4))

    def _roots(self, words):
        expanded = list(words) + [self.SYNONYMS[w] for w in words if w in self.SYNONYMS]
        return {self._stem(w) for w in expanded}

    def _filter_sources(self, results, domain, function, require_abstract=True):
        domain_roots, function_roots = self._roots(domain), self._roots(function)
        software_roots = self._roots(self.SOFTWARE_WORDS)
        ranked = {}
        for item in results or []:
            if item.get("provider") not in {"Crossref"}:
                continue
            if not item.get("title") or not item.get("url", "").startswith("https://"):
                continue
            if require_abstract and (not item.get("snippet") or item.get("evidence_type") != "abstract"):
                continue
            content = self._roots(self._tokens(f"{item['title']} {item.get('snippet', '')}"))
            software_match = len(software_roots & content)
            domain_match = len(domain_roots & content)
            function_match = len(function_roots & content)
            # Accept studies of the complete system, without requiring the exact RF.
            if not software_match or not (domain_match or function_match):
                continue
            score = function_match * 6 + domain_match * 4 + software_match * 3
            key = (item.get("doi") or item["url"]).lower()
            candidate = dict(item, score=score)
            if key not in ranked or score > ranked[key]["score"]:
                ranked[key] = candidate
        return sorted(ranked.values(), key=lambda item: item["score"], reverse=True)[:5]

    def _is_infinitive(self, word):
        return len(word) >= 5 and word.endswith(("ar", "er", "ir"))

    def _tokens(self, text):
        return re.findall(r"[a-z0-9]+", self._normalize(text))

    def _stem(self, word):
        if word.endswith("es") and len(word) > 6:
            return word[:-2]
        if word.endswith("s") and len(word) > 5:
            return word[:-1]
        return word

    def _normalize(self, text):
        text = unicodedata.normalize("NFD", str(text or "").lower())
        return re.sub(r"\s+", " ", "".join(c for c in text if unicodedata.category(c) != "Mn")).strip()

