import logging
import io
from typing import Optional
import wave
from google import genai 
from google.genai import types

from todo_backend.config.setting import settings

logger  = logging.getLogger(__name__)

class GeminiTSSClient:
    """cilent for gemini text- speak - TSS functionality.
    initializes the genAi cilent for use with TSS-Specific preview models.
    use the new SDK ( from google import agent Ai) for consisster wwith tss cilent.
    """
    def __init__(self, model_name: str = "models/gemini-2.5-flash-preview-tts"):
        """
        initializes the tss client with the api key and model.

        Args:
            model_name (str, optional): _description_. Defaults to "model/gemini-2.5-flash-preview-tts".
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini_api_key is not configuare in settings.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name
        logger.info(f" Gemini Tss init with model: {model_name}")

    def _create_wav_bytes(self, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):

        """
        Args:
            pcm_data (bytes): _description_
            channels (init, optional): _description_. Defaults to 1.
            rate (init, optional): _description_. Defaults to 2400.
            sample_with (init, optional): _description_. Defaults to 2.

        Returns:
            bytes: _description_
        """
        wav_buffer  = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)
        return wav_buffer.getvalue()
        
    async def speak(self , text: str , voice_name: Optional[str] = "Kore", speed: Optional[float] = None)-> bytes : 
        """_summary_

        Args:
            sefl (_type_): _description_
            text (str): _description_
            voice_name (Optional[str], optional): _description_. Defaults to "Kore".
            speed (Optional[float], optional): _description_. Defaults to None.

        Returns:
            bytes: _description_
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")
        if speed is not None:
            pace_instruction = "slowly" if speed < 1.0 else "quickly" if speed > 1.0 else ""
            text = f"Say{pace_instruction}: {text}"
        try:
            logger.info(f"genenrate TTS for text length: {len(text)} with voice {voice_name} ")
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents = text,
                config = types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        ),
                    ),
                ),

            )
            if not response.candidates or not response.candidates[0].content.parts:

                raise ValueError (" no audio generate in repoense .")
            audio_part = response.candidates[0].content.parts[0]
            if not hasattr(audio_part, 'inline_data') or audio_part.inline_data is None:
                raise ValueError (" Auto data not found in repose pasrt.")
            
            pcm_bytes = audio_part.inline_data.data
            wav_bytes = self._create_wav_bytes(pcm_bytes)
            logger.info (f"TTS generate susscessfully: {len(wav_bytes)} bytes of wav audio")
            return wav_bytes
        except Exception as e:
            logger.error(f" Error generate TTS for text: {str(e)}")
            raise Exception (f" TSS  generate failse : { str(e)}" )