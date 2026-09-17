import whisper


class WhisperService:

    def __init__(self, model_name="base"):

        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):

        result = self.model.transcribe(
            audio_path,
            language="es",
            fp16=False
        )

        return result["text"].strip()