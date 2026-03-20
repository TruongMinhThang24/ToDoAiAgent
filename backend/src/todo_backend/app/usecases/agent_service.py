# D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\app\usecases\agent_service.py
import logging
from typing import Optional , Any
import re
import inspect
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
from datetime import timedelta
import pytz
from todo_backend.config.setting import settings
from todo_backend.infrastructure.agent.gemini_client import GeminiClient
from todo_backend.infrastructure.agent.tools import get_tools
from fastapi import HTTPException

from todo_backend.api.schemas.chat_schema import AgentChatReponse
from todo_backend.app.usecases.rag import RAGUseCases
logger = logging.getLogger(__name__)

################################################################################
# ## AGENT_PROMPT MỚI: "HYBRID VALIDATION" (AGENT-LED + TOOL-LED FAILSAFE) ##
################################################################################
AGENT_PROMPT = """
Bạn là Trợ lý AI quản lý Todo, giao tiếp tự nhiên như con người.

📅 **CONTEXT THỜI GIAN (QUAN TRỌNG!):**
- Ngày giờ HIỆN TẠI: {{current_datetime}}
- Ngày HÔM NAY: {{current_date}}
- Ngày MAI: {{ngày mai}}

⚠️ **LƯU Ý:** Đây là thời gian THỰC. Sử dụng chính xác các giá trị này khi tính toán deadline.

═══════════════════════════════════════════════════════════════════
🎯 QUY TẮC TỐI THƯỢNG
═══════════════════════════════════════════════════════════════════
1. CHỈ xử lý tin nhắn CUỐI CÙNG của user. KHÔNG tự ý lặp lại tác vụ cũ.
2. LUÔN ưu tiên GỌI TOOL trước khi trả lời văn bản.
3. NẾU đủ thông tin → GỌI TOOL NGAY. NẾU thiếu → HỎI ngắn gọn.
4. Giao tiếp linh hoạt: nghiêm túc khi cần, thoải mái khi được.


═══════════════════════════════════════════════════════════════════
🛠️ TOOLS & KỊCH BẢN
═══════════════════════════════════════════════════════════════════

**1️⃣ LIỆT KÊ TODO**
Keywords: "liệt kê", "xem", "danh sách", "list", "show", "có task nào", "task", "todo", "công việc"
→ GỌI NGAY: `list_todos_tool()` (KHÔNG hỏi thêm)

**CRITICAL RULES:**
- NẾU user hỏi về "danh sách", "liệt kê", "xem task" → GỌI TOOL NGAY
- KHÔNG được trả lời "Đã xử lý" mà không gọi tool
- Tool KHÔNG cần parameters → Tự động lấy theo user đang login
**OUTPUT HANDLING:**
```
Tool trả về: "**Danh sách task:**\n  ID | ... |"
→ Bạn PHẢI trả: "**Danh sách task:**\n  ID | ... |"
   (KHÔNG thêm "Tuyệt vời!" hay "Bạn muốn gì?")
```

**VÍ DỤ:**
```
User: "Liệt kê danh sách todo"  ← PHẢI GỌI TOOL
User: "liet ke cho toi danh sach todo"  ← PHẢI GỌI TOOL (có lỗi chính tả)
User: "xem task"  ← PHẢI GỌI TOOL
User: "show me todos"  ← PHẢI GỌI TOOL
```

**2️⃣ THÊM TODO**
Cần: `title` + `description` + `due_date` (priority mặc định = 1)

**Case A: ĐỦ 100% → GỌI NGAY**
```
User: "Tạo task họp team, slide Q4, ngày mai 3h chiều, ưu tiên cao"
→ Phân tích:
  ✅ title = "họp team"
  ✅ desc = "slide Q4"
  ✅ due_date = "ngày mai 3h chiều" → {{ngày mai}}T15:00:00
  ✅ priority = 5
→ GỌI: add_todo_tool("họp team", "slide Q4", "2025-11-15T15:00:00", 5)
```

**Case B: THIẾU → HỎI TUẦN TỰ**
```
User: "Tạo task học bài"
→ Phân tích: ✅ title | ❌ desc | ❌ due_date
→ HỎI: "Task 'Học bài' - bạn học gì và khi nào?"

User: "Làm chapter 5, 8h tối nay"
→ Phân tích: ✅ title | ✅ desc | ✅ due_date
→ GỌI: add_todo_tool("học bài", "Làm chapter 5", "{{current_date}}T20:00:00", 1)
```

**⏰ CHUYỂN ĐỔI THỜI GIAN:**
- "tối nay 8h" → `{{current_date}}T20:00:00`
- "ngày mai 9h" → `{{ngày mai}}T09:00:00`
- "thứ 6 2h chiều" → Tính toán → `YYYY-MM-DDT14:00:00`

---

**3️⃣ SỬA TODO**
Cần: `todo_id` HOẶC `title_query` + ít nhất 1 field mới

```
User: "Sửa task mua sữa"
→ ❌ Thiếu field cần sửa
→ HỎI: "Bạn muốn sửa gì? (tiêu đề/mô tả/thời hạn/ưu tiên/hoàn thành)"

User: "Đổi thành mua 3 lít"
→ ✅ Có identifier + description
→ GỌI: update_todo_tool(title_query="mua sữa", description="mua 3 lít")
```

---

**4️⃣ XÓA TODO**
Cần: `todo_id` HOẶC `title` + xác nhận

**QUY TRÌNH 2 BƯỚC:**
```
User: "Xóa task 123"
→ Bước 1: GỌI delete_todo_tool(todo_id=123, confirmation="")
           Tool trả về: "CLARIFY: Bạn CHẮC CHẮN xóa...?"
→ Bước 2: Forward CLARIFY cho user
→ User: "Có"
→ Bước 3: GỌI delete_todo_tool(todo_id=123, confirmation="Có")
```

---

**5️⃣ HOÀN THÀNH TODO**
```
User: "Hoàn thành task mua sữa"
→ GỌI NGAY: update_todo_tool(title_query="mua sữa", completed=True)
```

---

**6️⃣ TÌM KIẾM THÔNG TIN**
- `search_internet_tool(query)`: MẶC ĐỊNH cho kiến thức chung, tin tức, thời tiết
- `search_knowledge_base_tool(query)`: CHỈ DÙNG khi user hỏi "tài liệu của tôi", "file upload"

KHÔNG dùng cả 2 cùng lúc.

═══════════════════════════════════════════════════════════════════
🔄 HUMAN-IN-THE-LOOP (HITL)
═══════════════════════════════════════════════════════════════════
NẾU tool trả về `CLARIFY: ...` → FORWARD nguyên văn cho user.
KHÔNG tự viết clarification mới.

Ví dụ:
```
Tool trả về: "CLARIFY: Bạn muốn xóa task 'Học bài' (ID: 5)?"
→ Bạn forward: "CLARIFY: Bạn muốn xóa task 'Học bài' (ID: 5)?"
```

═══════════════════════════════════════════════════════════════════
❌ KHÔNG BAO GIỜ:
═══════════════════════════════════════════════════════════════════
- Gọi tool khi thiếu thông tin BẮT BUỘC
- Hỏi lại thông tin đã có trong context
- Dùng câu mẫu máy móc ("Task '{{title}}' nghe hay đấy!")

═══════════════════════════════════════════════════════════════════
✅ LUÔN LUÔN:
═══════════════════════════════════════════════════════════════════
- Phân tích đủ/thiếu TRƯỚC khi gọi tool
- Chuyển thời gian sang ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- Tin tưởng vào tool validation (có failsafe riêng)
- Hỏi ngắn gọn, có ví dụ cụ thể
"""
class AgentService:
    """
    Application Service chịu trách nhiệm điều phối AI Agent.
    Đóng gói logic khởi tạo Agent, xử lý đầu vào text/voice và trả về kết quả cuối cùng.
    Sử dụng chiến lược Hybrid Validation: Agent-led (90%) + Tool-led failsafe (10%).
    """

    def __init__(self, db: Session, user_id: int, tavily_tool: Any = None,rag_usecase: Optional[RAGUseCases] = None, model: Optional[ChatGoogleGenerativeAI] = None, checkpointer: Optional[Any] = None):
        """
        Khởi tạo service với database session.
        Session này sẽ được truyền xuống cho các tools cần truy cập DB.
        """
        self.db = db
        self.user_id = user_id
        self.tavily_tool = tavily_tool
        self.rag_usecase = rag_usecase
        self.gemini_client = GeminiClient()
        self.model = model or ChatGoogleGenerativeAI(  
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.checkpointer = checkpointer

         # ✅ CRITICAL: Tính toán thời gian THỰC với timezone
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        now = datetime.now(vietnam_tz)
        tomorrow = now + timedelta(days=1)
        
        # ✅ Format prompt với NHIỀU placeholders
        self.formatted_prompt = AGENT_PROMPT.replace(
            "{{current_datetime}}", now.strftime("%Y-%m-%d %H:%M:%S %A")
        ).replace(
            "{{current_date}}", now.strftime("%Y-%m-%d")
        ).replace(
            "{{ngày mai}}", tomorrow.strftime("%Y-%m-%d")
        )
        
        # ✅ LOG để verify
        logger.info("📅 Agent Prompt Context Initialized:")
        logger.info(f"  - Current datetime: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
        logger.info(f"  - Current date: {now.strftime('%Y-%m-%d')}")
        logger.info(f"  - Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")
        logger.info(f"  - Model temperature: {self.model.temperature}")

        self.agent_executor = self._initialize_agent()

        self.question_pattern = re.compile(
            r'\?$|hỏi.*\?|cho.*biết.*\?|mô tả.*\?|tiêu đề.*\?', re.IGNORECASE)
        
    def _initialize_agent(self):
        """
        Thiết lập và khởi tạo ReAct Agent sử dụng LangGraph.
        """
        # Lấy danh sách tools, inject DB session và RAG nếu có
        tools = get_tools(db=self.db, owner_id=self.user_id, tavily_tool=self.tavily_tool, rag_usecase=self.rag_usecase)  # NEW: Pass rag
        logger.info(f"📋 Registered tools: {[tool.name for tool in tools]}")
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description[:100]}...")
        # Tạo prebuilt ReAct agent với prompt HITL
        agent_executor = create_react_agent(
            self.model, 
            tools=tools, 
            checkpointer=self.checkpointer  
        )
        
        logger.info(f"Agent initialized successfully for user {self.user_id} with tools and HITL prompt.")
        return agent_executor

    def _is_async_checkpointer(self) -> bool:
        """Detect whether the configured checkpointer exposes async methods.

        LangGraph supports both sync and async checkpointers. We switch the
        invocation path accordingly to avoid event-loop/thread errors.
        """
        cp = self.checkpointer
        if cp is None:
            return False
        async_attrs = ("load", "save", "aget", "aset")
        return any(inspect.iscoroutinefunction(getattr(cp, attr, None)) for attr in async_attrs)
    
    async def run_text_command(self, user_query: str, thread_id: str) -> AgentChatReponse:
        """
        Xử lý yêu cầu từ văn bản (Text-to-Action) với HITL parsing.
        """
        if not user_query.strip():
            return AgentChatReponse(
                friendly_message="Tôi không nhận được yêu cầu nào. Bạn cần giúp gì?",
                thread_id=thread_id,
                needs_clarification=True,
                clarification_prompt="Hãy cho tôi biết bạn muốn làm gì nhé!"
            )

        logger.info(f"Agent executing text command: '{user_query}' for thread: {thread_id}")

        config = {"configurable": {"thread_id": thread_id}}

        try:
            inputs = {
                "messages": [
                    SystemMessage(content=self.formatted_prompt),
                    HumanMessage(content=user_query),
                    SystemMessage(content=(
                        "⚠️ REMINDER: Nếu user hỏi về 'danh sách', 'liệt kê', 'xem task' "
                        "→ GỌI NGAY `list_todos_tool()`. "
                        "KHÔNG được trả lời 'Đã xử lý' mà không gọi tool!"
                    ))
                ]
            }
            
            logger.info("🤖 Agent config:")
            logger.info(f"  - Model: {self.model.model}")
            logger.info(f"  - Temperature: {self.model.temperature}")
            logger.info(f"  - Tools: {[tool.name for tool in self.agent_executor.tools] if hasattr(self.agent_executor, 'tools') else 'Unknown'}")
            logger.info(f"📤 Agent invoked with query: '{user_query}'")

            use_async = self._is_async_checkpointer()
            logger.info(
                "🚦 Invocation mode: %s | Checkpointer: %s",
                "async" if use_async else "sync",
                self.checkpointer.__class__.__name__ if self.checkpointer else "None",
            )

            if use_async:
                response = await self.agent_executor.ainvoke(inputs, config=config)
            else:
                response = self.agent_executor.invoke(inputs, config=config)

            # --- PARSE RESPONSE ---
            last_message = response.get("messages", [])[-1]
            
            # ✅ FIX: Debug log BEFORE parsing
            logger.info("🔍 RAW last_message:")
            logger.info(f"  - Type: {type(last_message)}")
            logger.info(f"  - Content type: {type(last_message.content) if hasattr(last_message, 'content') else 'N/A'}")
            logger.info(f"  - Content value: {last_message.content if hasattr(last_message, 'content') else 'N/A'}")
            
            # Extract content từ AIMessage
            if not isinstance(last_message, AIMessage):
                final_message_content = str(last_message.content) if last_message.content else ""
            elif isinstance(last_message.content, list) and last_message.content:
                final_message_content = last_message.content[0].get("text", "")
            else:
                final_message_content = str(last_message.content) if last_message.content else ""

            needs_clarify = False
            clarify_prompt = None

            # ✅ Parse CLARIFY
            if "CLARIFY:" in final_message_content:
                parts = final_message_content.split("CLARIFY:", 1)
                clarify_prompt = parts[1].strip() if len(parts) > 1 else final_message_content
                needs_clarify = True
                final_message_content = parts[0].strip() if parts[0].strip() else ""
                logger.info(f"HITL detected via CLARIFY (AI): {clarify_prompt}")
            
            # Kiểm tra ToolMessage có CLARIFY
            elif getattr(last_message, "tool_calls", None):
                for msg in response["messages"][-3:]:
                    if isinstance(msg, ToolMessage) and "CLARIFY:" in str(msg.content):
                        clarify_prompt = str(msg.content).split("CLARIFY:", 1)[1].strip()
                        needs_clarify = True
                        final_message_content = ""
                        logger.info(f"HITL detected in ToolMessage: {clarify_prompt}")
                        break
            
            # Heuristic: Detect question pattern
            else:
                if (
                    self.question_pattern.search(final_message_content) and
                    ("mô tả" in final_message_content.lower() or
                    "chi tiết" in final_message_content.lower())
                ):
                    needs_clarify = True
                    clarify_prompt = final_message_content
                    logger.info(f"HITL detected via heuristic: {clarify_prompt}")
            
            # ✅ CRITICAL FIX: Fallback 3 bước + Debug log
            friendly_message = (
                final_message_content or 
                clarify_prompt or 
                "Đã xử lý yêu cầu."
            )
            
            # ✅ FIX: Safe logging (tránh None[:100])
            logger.info("📤 Returning response:")
            if friendly_message:
                preview = friendly_message[:100] if len(friendly_message) > 100 else friendly_message
                logger.info(f"  - friendly_message: {preview}...")
            else:
                logger.warning("  - friendly_message: (None - FALLBACK FAILED!)")
                friendly_message = "Đã xử lý yêu cầu."  # ✅ Double fallback
            
            logger.info(f"  - needs_clarification: {needs_clarify}")
            logger.info(f"  - clarification_prompt: {clarify_prompt}")
            
            return AgentChatReponse(
                friendly_message=friendly_message,
                thread_id=thread_id,
                needs_clarification=needs_clarify,
                clarification_prompt=clarify_prompt
            )

        except Exception as e:
            logger.error(
                f"Error during agent execution for thread {thread_id}: {e}",
                exc_info=True
            )
            return AgentChatReponse(
                friendly_message="Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý.",
                thread_id=thread_id,
                needs_clarification=False,
                clarification_prompt=None
            )

    async def run_voice_command(self, audio_bytes: bytes, thread_id: str, mime_type: str = "audio/mp3") -> AgentChatReponse:
        """
        Xử lý yêu cầu từ giọng nói (Voice-to-Action).
        Transcribe audio → run_text_command.
        """
        logger.info(f"Processing voice command ({len(audio_bytes)} bytes, {mime_type}) for thread {thread_id}...")

        base_error_response = {
            "thread_id": thread_id,
            "needs_clarification": False,
            "clarification_prompt": None
        }

        try:
            transcribed_text = await self.gemini_client.transcribe_audio(audio_bytes, mime_type)

            if not transcribed_text:
                logger.warning(f"Voice transcription returned empty text for thread {thread_id}.")
                return AgentChatReponse(
                    friendly_message="Tôi không nghe rõ bạn nói gì. Vui lòng thử lại.",
                    **base_error_response
                )

            logger.info(f"Voice transcribed for thread {thread_id}: '{transcribed_text}'")

            # Giờ run_text_command return object
            agent_response = await self.run_text_command(transcribed_text, thread_id=thread_id)

            return agent_response
        
        except HTTPException as he:
            logger.warning(f"HTTPException during voice processing: {he.detail}")
            return AgentChatReponse(
                friendly_message=f"Lỗi xử lý audio: {he.detail}",
                **base_error_response
            )
        except ValueError as ve:
            logger.warning(f"Voice processing failed (Value Error): {ve}")
            return AgentChatReponse(
                friendly_message=str(ve),
                **base_error_response
            )
        except RuntimeError as re:
            logger.error(f"Voice processing failed (Runtime Error): {re}")
            return AgentChatReponse(
                friendly_message="Dịch vụ giọng nói tạm thời không khả dụng. Vui lòng thử lại sau.",
                **base_error_response
            )
        except Exception:
            logger.exception(f"Unexpected error in voice command pipeline for thread {thread_id}.")
            return AgentChatReponse(
                friendly_message="Đã xảy ra lỗi không mong muốn khi xử lý giọng nói.",
                **base_error_response
            )