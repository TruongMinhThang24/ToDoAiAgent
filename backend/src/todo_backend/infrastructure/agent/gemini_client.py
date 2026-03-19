import logging
from google import genai
from google.genai import types
from fastapi import HTTPException, status

from todo_backend.config.setting import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client chuyên trách giao tiếp với Google Gemini API (Sử dụng NEW SDK: google-genai).
    Hỗ trợ xử lý bất đồng bộ (Async) cho các tác vụ Multimodal.
    """

    def __init__(self, model_name: str = "models/gemini-2.5-flash"):
        self.model_name = model_name
        self.client = self._init_client()
        logger.info(f"GeminiClient (New SDK) initialized with model: {self.model_name}")

    def _init_client(self) -> genai.Client:
        """Khởi tạo Google GenAI Client."""
        if not settings.GEMINI_API_KEY:
            logger.critical("GEMINI_API_KEY is missing in settings!")
            raise ValueError("GEMINI_API_KEY must be set.")
        
        # Trong SDK mới, ta khởi tạo Client trực tiếp với API Key
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/mp3") -> str:
        """
        Gửi audio bytes trực tiếp lên Gemini để phiên âm (sử dụng Async Client của SDK mới).
        """
        try:
            logger.debug(f"Sending {len(audio_bytes)} bytes ({mime_type}) to Gemini {self.model_name}...")

            # 1. Chuẩn bị nội dung (Native Audio - Inline Data)
            # SDK mới sử dụng các class 'types' để định nghĩa cấu trúc dữ liệu rõ ràng hơn.
            prompt_text = "Please transcribe the following audio strictly verbatim. Return ONLY the words spoken."
            
            # 2. Gọi API bất đồng bộ thông qua 'client.aio'
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(text=prompt_text),
                            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0 # Đặt nhiệt độ = 0 để transcript chính xác nhất
                )
            )

            # 3. Kiểm tra kết quả
            if not response.text:
                logger.warning("Gemini returned empty response.")
                raise ValueError("Could not transcribe audio (empty response).")

            return response.text.strip()

        except Exception as e:
            # SDK mới có thể throw các loại exception khác nhau, 
            # ta bắt chung Exception và log lại để debug dễ dàng hơn trong giai đoạn đầu.
            logger.error(f"Gemini (New SDK) transcription failed: {e}", exc_info=True)
            
            # Phân loại lỗi cơ bản dựa trên message (do SDK mới chưa ổn định tài liệu về Exception types)
            error_msg = str(e).lower()
            if "400" in error_msg or "invalid" in error_msg:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid audio file.")
            elif "429" in error_msg or "quota" in error_msg:
                 raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Gemini AI is busy.")
            else:
                 raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI Service unavailable.")