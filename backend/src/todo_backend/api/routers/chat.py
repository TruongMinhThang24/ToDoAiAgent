#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\chat.py
import io
import json
import logging
import re
import uuid

import urllib.parse
from typing import Any as _Any
from pydub import AudioSegment
from typing import Annotated, Any, Dict, List, Optional
from langchain_tavily import TavilySearch
import docx
# checkpointer is now async Postgres-backed; use generic typing
from fastapi.responses import StreamingResponse
from ...infrastructure.agent.gemini_tts_client import GeminiTSSClient
from fastapi import (APIRouter, Depends, File, Form, Header, HTTPException, Query,
                     UploadFile, status)
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from sqlalchemy.orm import Session

from ...app.usecases.rag import RAGUseCases
from ...app.usecases.agent_service import AgentService
from ...app.usecases.chat_thread_service import ChatThreadService
from ...infrastructure.agent.dependencies import (get_checkpointer,
                                                  get_gemini_model,
                                                  get_optional_tavily_tool,
                                                  get_rag_usecase)
from ...infrastructure.database.database import sessionLocal
from ...infrastructure.repositories.chat_repository_impl import ChatRepositoryImpl
from ..schemas.chat_schema import (AddDocumentRequest, AgentChatReponse,
                                   ChatRequest, CreateThreadRequest,
                                   ThreadListResponse,
                                   ThreadMessageListResponse,
                                   ThreadMessageResponse)
from .auth import get_current_user

logger = logging.getLogger(__name__)
AudioSegment.converter = "C:\\ffmpeg\\ffmpeg-2025-11-06-git-222127418b-full_build\\bin\\ffmpeg.exe"
router = APIRouter( prefix = "/chat" , tags = ["Chat agent "])


def _sse_event(payload: dict[str, Any]) -> str:
    """Format one Server-Sent Event frame."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

def get_db():
    db = sessionLocal()
    try: 
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session , Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
model_dependency = Annotated[ChatGoogleGenerativeAI , Depends(get_gemini_model)]
memory_dependency = Annotated[_Any, Depends(get_checkpointer)]
rag_usecase_dependency = Annotated[RAGUseCases, Depends(get_rag_usecase)]
tavily_dependency = Annotated[Optional[TavilySearch], Depends(get_optional_tavily_tool)]
def get_agent_service(
    db: db_dependency,
    user: user_dependency,  
    tavily_tool: tavily_dependency,
    rag_usecase: rag_usecase_dependency, 
    model: model_dependency, 
    checkpointer: memory_dependency
) -> AgentService:
    """
    Dependency tạo AgentService với đầy đủ ngữ cảnh (DB, User, Tools ngoài).
    Mỗi request sẽ tạo một AgentService mới gắn liền với user đó.
    """
    return AgentService(db=db, user_id=user['id'], tavily_tool=tavily_tool,rag_usecase=rag_usecase, model=model, checkpointer=checkpointer)

agent_service_dependency = Annotated[AgentService, Depends(get_agent_service)]


def get_chat_thread_service(
    db: db_dependency,
    user: user_dependency,
) -> ChatThreadService:
    repo = ChatRepositoryImpl(db)
    return ChatThreadService(repo=repo, owner_id=user["id"])


chat_thread_service_dependency = Annotated[ChatThreadService, Depends(get_chat_thread_service)]


def _sanitize_message(message: str) -> str:
    cleaned = (message or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(cleaned) > 4000:
        raise HTTPException(status_code=400, detail="Message too long (max 4000 chars)")
    return cleaned

@router.post("/", response_model=AgentChatReponse)
async def chat_with_agent(
    request: ChatRequest,
    user: user_dependency,
    agent_service: agent_service_dependency,  # ✅ Inject AgentService
    thread_service: chat_thread_service_dependency,
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
):
    """
    ✅ FIXED: Dùng AgentService thay vì tạo agent mới
    Loại bỏ duplicate AGENT_PROMPT
    """
    owner_id = user["id"]
    user_message = _sanitize_message(request.message)
    client_thread_id = request.thread_id
    thread_id_to_use: str

    # Generate/validate thread_id
    if client_thread_id:
        if not client_thread_id.startswith(f"user_chat_session_{owner_id}_"):
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")
        thread_id_to_use = client_thread_id
        thread_service.ensure_thread(thread_id_to_use)
        logger.info(f"Continue chat for {owner_id} on {thread_id_to_use}")
    else:
        new_uuid = str(uuid.uuid4())
        thread_id_to_use = f"user_chat_session_{owner_id}_{new_uuid}"
        thread_service.create_thread(thread_id_to_use, title=None)
        logger.info(f"Create NEW chat for user {owner_id} on thread {thread_id_to_use}")

    thread_service.add_message(thread_id=thread_id_to_use, role="user", content=user_message)
    
    # ✅ Gọi AgentService (đã có prompt mới)
    try:
        agent_response = await agent_service.run_text_command(
            user_query=user_message,
            thread_id=thread_id_to_use,
            custom_api_key=x_gemini_api_key,
        )
        if agent_response.friendly_message:
            thread_service.add_message(
                thread_id=thread_id_to_use,
                role="assistant",
                content=str(agent_response.friendly_message),
            )
        return agent_response
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return AgentChatReponse(
            friendly_message="Xin lỗi, đã có lỗi xảy ra.",
            thread_id=thread_id_to_use,
            needs_clarification=False,
            clarification_prompt=None
        )


@router.post("/stream")
async def chat_with_agent_stream(
    request: ChatRequest,
    user: user_dependency,
    agent_service: agent_service_dependency,
    thread_service: chat_thread_service_dependency,
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
):
    """Stream text response for chat UI using SSE.

    Event payloads:
    - {"type": "chunk", "content": "...", "thread_id": "..."}
    - {"type": "done", "thread_id": "...", "needs_clarification": bool, ...}
    - {"type": "error", "message": "...", "thread_id": "..."}
    """
    owner_id = user["id"]
    user_message = _sanitize_message(request.message)
    client_thread_id = request.thread_id
    thread_id_to_use: str

    if client_thread_id:
        if not client_thread_id.startswith(f"user_chat_session_{owner_id}_"):
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")
        thread_id_to_use = client_thread_id
        thread_service.ensure_thread(thread_id_to_use)
    else:
        thread_id_to_use = f"user_chat_session_{owner_id}_{uuid.uuid4()}"
        thread_service.create_thread(thread_id_to_use, title=None)

    # Persist user message first to keep DB memory consistent.
    thread_service.add_message(thread_id=thread_id_to_use, role="user", content=user_message)

    async def _event_generator():
        assistant_text = ""
        try:
            agent_response = await agent_service.run_text_command(
                user_query=user_message,
                thread_id=thread_id_to_use,
                custom_api_key=x_gemini_api_key,
            )
            assistant_text = str(agent_response.friendly_message or "")

            # Stream by token-like chunks (words) for typewriter UX.
            words = assistant_text.split()
            if not words:
                yield _sse_event({"type": "chunk", "content": "", "thread_id": thread_id_to_use})
            else:
                for index, word in enumerate(words):
                    chunk = word if index == len(words) - 1 else f"{word} "
                    yield _sse_event({"type": "chunk", "content": chunk, "thread_id": thread_id_to_use})

            # Persist assistant response after streaming completes.
            if assistant_text:
                thread_service.add_message(
                    thread_id=thread_id_to_use,
                    role="assistant",
                    content=assistant_text,
                )

            yield _sse_event(
                {
                    "type": "done",
                    "thread_id": thread_id_to_use,
                    "needs_clarification": bool(agent_response.needs_clarification),
                    "clarification_prompt": agent_response.clarification_prompt,
                }
            )
        except Exception as exc:
            logger.error(f"Streaming chat failed: {exc}", exc_info=True)
            if assistant_text:
                try:
                    thread_service.add_message(
                        thread_id=thread_id_to_use,
                        role="assistant",
                        content=assistant_text,
                    )
                except Exception:
                    logger.warning("Failed to persist partial assistant stream", exc_info=True)
            yield _sse_event(
                {
                    "type": "error",
                    "message": "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý.",
                    "thread_id": thread_id_to_use,
                }
            )

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    user: user_dependency,
    thread_service: chat_thread_service_dependency,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = thread_service.list_threads(limit=limit, offset=offset)
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/threads", status_code=201)
async def create_thread(
    request: CreateThreadRequest,
    user: user_dependency,
    thread_service: chat_thread_service_dependency,
):
    owner_id = user["id"]
    thread_id = f"user_chat_session_{owner_id}_{uuid.uuid4()}"
    thread = thread_service.create_thread(thread_id=thread_id, title=request.title)
    return {
        "thread_id": thread.id,
        "title": thread.title,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
    }


@router.get("/threads/{thread_id}/messages", response_model=ThreadMessageListResponse)
async def get_thread_messages(
    thread_id: str,
    user: user_dependency,
    thread_service: chat_thread_service_dependency,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    owner_id = user["id"]
    if not thread_id.startswith(f"user_chat_session_{owner_id}_"):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập vào luồng chat này.")

    messages = thread_service.list_messages(thread_id=thread_id, limit=limit, offset=offset)
    items = [
        ThreadMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )
        for msg in messages
    ]
    return {
        "thread_id": thread_id,
        "items": items,
        "limit": limit,
        "offset": offset,
    }


@router.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: str,
    user: user_dependency,
    thread_service: chat_thread_service_dependency,
):
    owner_id = user["id"]
    if not thread_id.startswith(f"user_chat_session_{owner_id}_"):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập vào luồng chat này.")
    thread_service.delete_thread(thread_id=thread_id)
    return None

@router.get("/history_chat/{thread_id}", response_model=List[Dict[str, Any]])
async def chat_history(
    thread_id: str,
    user: user_dependency,
    thread_service: chat_thread_service_dependency,
):
    """Legacy endpoint: trả lịch sử chat từ bảng persisted messages."""
    owner_id = user["id"]

    if not thread_id.startswith(f"user_chat_session_{owner_id}_"):
        raise HTTPException(status_code=403, detail="Không có quyền truy cập vào luồng chat này.")

    messages = thread_service.list_messages(thread_id=thread_id, limit=200, offset=0)
    return [{"role": m.role, "content": m.content} for m in messages]

@router.post("/knowledge", status_code=201)
async def add_document(
    request: AddDocumentRequest,
    user: user_dependency,
    rag_usecase: rag_usecase_dependency
):
    """Thêm một tài liệu mới vào cơ sở kiến thức của user."""
    owner_id = user["id"]
    result = rag_usecase.add_document_to_knowledge_base(
        user_id=owner_id, 
        text=request.text
    )
    return {"message": result}

@router.post("/knowledge/upload", status_code=201)
async def add_file(
    user: user_dependency,                      
    rag_usecase: rag_usecase_dependency,        
    file: UploadFile = File(...)
):
    """
    Add new file (PDF, DOCX, TXT) from file upload 
    into user's knowledge base.
    """
    owner_id = user["id"]
    extracted_text = ""

    # Read content
    contents = await file.read()
    
    try:
        # 1. PDF
        if file.content_type == "application/pdf":
            pdf_stream = io.BytesIO(contents)
            reader_pdf = PdfReader(pdf_stream)
            for page in reader_pdf.pages:
                page_text = page.extract_text()
            
                if page_text:
                    # 1. Xóa các tag [Image X]
                    cleaned_text = re.sub(r'\[Image \d+\]', '', page_text)
                    
                    # 2. Xóa các tag --- PAGE X ---
                    cleaned_text = re.sub(r'--- PAGE \d+ ---', '', cleaned_text)
                    
                    # 3. Xóa các dòng chỉ chứa số (số trang)
                    cleaned_text = re.sub(r'^\d+\s*$', '', cleaned_text, flags=re.MULTILINE)
                    
                    # 4. (Tùy chọn) Xóa các dòng trống thừa
                    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
                    
                    extracted_text += cleaned_text + "\n"
                # === KẾT THÚC DỌN RÁC ===
        
        # 2. DOCX
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc_stream = io.BytesIO(contents)
            reader_doc = docx.Document(doc_stream)
            doc_text = ""  # Tạm lưu text thô từ tất cả paragraphs
            for para in reader_doc.paragraphs:
                if para.text.strip():  # Bỏ qua para rỗng ngay từ đầu
                    doc_text += para.text + "\n"
            
            # === BẮT ĐẦU DỌN RÁC CHO DOCX (TƯƠNG TỰ PDF) ===
            if doc_text:
                # 1. Xóa các tag [Image X] nếu có (hiếm, nhưng an toàn)
                cleaned_text = re.sub(r'\[Image \d+\]', '', doc_text)
                
                # 2. Xóa các tag --- PAGE X --- nếu có
                cleaned_text = re.sub(r'--- PAGE \d+ ---', '', cleaned_text)
                
                # 3. Xóa các dòng chỉ chứa số (số trang/header)
                cleaned_text = re.sub(r'^\d+\s*$', '', cleaned_text, flags=re.MULTILINE)
                
                # 4. Xóa dòng trống thừa
                cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
                
                # 5. (Thêm cho DOCX) Xóa tab/multiple spaces thừa (từ format Word)
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize spaces
                cleaned_text = re.sub(r'\t+', ' ', cleaned_text)  # Tab → space
                
                extracted_text = cleaned_text + "\n"
            # === KẾT THÚC DỌN RÁC ===
        
        # 3. TXT
        elif file.content_type == "text/plain":  
            extracted_text = contents.decode("utf-8")
        
        # 4. Unsupported
        else:
            raise HTTPException(
                status_code=415,
                detail="Only support: PDF, DOCX, TXT."  
            )
    except Exception as e:
        logger.error(f"Error processing file {file.filename} for user {owner_id}: {e}")  
        raise HTTPException(status_code=422, detail="File error or not PDF, DOCX, TXT.")  # Fix status & detail

    # Check if extracted text is empty
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="File is empty or no text extracted.")

    # Use usecase
    result = rag_usecase.add_document_to_knowledge_base(
        user_id=owner_id,
        text=extracted_text  
    )
    return {"message": result, "file_name": file.filename, "content_type": file.content_type}  # Fix key

#--- THÊM vào router ---
@router.post("/voice")
async def chat_with_voice(
    user: user_dependency,
    agent_service: agent_service_dependency,
    audio: UploadFile = File(...),
    thread_id: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(default=None, alias="X-Gemini-API-Key"),
):
    """
    Nhận file ghi âm, xử lý qua Agent và trả về phản hồi dạng text.
    """
    owner_id = user["id"]

    logger.info(f"--- VOICE REQUEST RECEIVED (USER: {owner_id}) ---")
    logger.info(f"Received Thread ID: '{thread_id}' (Type: {type(thread_id)})")
    logger.info(f"Received Audio: {audio.filename}, Content-Type: {audio.content_type}, Size: {audio.size}")
    
    # 1. Quản lý Thread ID 
    if thread_id:
        if not thread_id.startswith(f"user_chat_session_{owner_id}_"):
             raise HTTPException(status_code=403, detail="Invalid thread ID for this user.")
        current_thread_id = thread_id
        logger.info(f"Voice chat continuing on thread: {current_thread_id}")
    else:
        new_uuid = str(uuid.uuid4())
        current_thread_id = f"user_chat_session_{owner_id}_{new_uuid}"
        logger.info(f"Voice chat started new thread: {current_thread_id}")

    # 2. Validate file audio cơ bản
    valid_mimes = {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/webm",           # ← THÊM: Không có codecs
        "audio/webm;codecs=opus",
        "audio/ogg",
        "audio/ogg;codecs=opus",
        "audio/mp4",
        "audio/x-m4a"    # Alternative M4A
    } # Fix: Add mp3

    logger.info("📥 Received voice request:")
    logger.info(f"  - Content-Type: {audio.content_type}")
    logger.info(f"  - Filename: {audio.filename}")
    logger.info(f"  - Size: {audio.size if hasattr(audio, 'size') else 'unknown'}")


    base_mime = audio.content_type.split(';')[0]  # "audio/webm;codecs=opus" → "audio/webm"
    
    if base_mime not in valid_mimes and audio.content_type not in valid_mimes:
        logger.error(f"❌ Invalid MIME type: {audio.content_type} (base: {base_mime})")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Format audio '{audio.content_type}' không được hỗ trợ. Vui lòng dùng: {', '.join(valid_mimes)}"
        )
    
    if audio.content_type not in valid_mimes:
        raise HTTPException(status_code=415, detail="Unsupported audio format. Please upload wav/mp3/webm/ogg.")


    try:
        # 3. Đọc nội dung file và gọi AgentService
        audio_content = await audio.read()
        logger.info(f"📦 Audio file size: {len(audio_content)} bytes")
        if len(audio_content) < 1000:
            logging.warning("Audio file quá nhỏ, có thể bị lỗi")
            raise HTTPException(status_code=422, detail="Audio quá ngắn hoặc rỗng")
        
        # Gọi Use Case để xử lý toàn bộ flow (Transcribe -> Agent -> Response)
        response_text = await agent_service.run_voice_command(
            audio_bytes=audio_content,
            mime_type=audio.content_type,
            thread_id=current_thread_id,
            custom_api_key=x_gemini_api_key,
        )
        if response_text.needs_clarification:
            tts_text = response_text.clarification_prompt or response_text.friendly_message
        else:
            tts_text = response_text.friendly_message

        logger.info(f"Agent response text: '{tts_text[:100]}...'") 
        tts_client = GeminiTSSClient()
        audio_wav_bytes = await tts_client.speak(tts_text)

        wav_io= io.BytesIO(audio_wav_bytes)
        audio_wav = AudioSegment.from_wav(wav_io)

        mp3_io = io.BytesIO()
        audio_wav.export(mp3_io, format="mp3")
        clarification_prompt_text = response_text.clarification_prompt or ""
        encoded_prompt = urllib.parse.quote(clarification_prompt_text, safe='')
        mp3_io.seek(0)
        return StreamingResponse(
            mp3_io,
            media_type="audio/mpeg",
            headers = {
                "Content-Disposition": f"attachment; filename=response_{current_thread_id}.mp3",
                "X-Needs-Clarification": str(response_text.needs_clarification),
                "X-Clarification-Prompt": encoded_prompt,  
                "Cache-Control": "no-cache",
            }
        )
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Voice failure: {ve}") 
    except RuntimeError as re:
        logger.error(f" Voice run error {re}")
    except Exception as e:
        logger.error(f"Error in voice chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing your voice command.")