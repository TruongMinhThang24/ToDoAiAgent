# src/todo_backend/infrastructure/agent/tools.py
import logging
from typing import List, Optional
from langchain_core.tools import tool, BaseTool
import pytz
from sqlalchemy.orm import Session
from ...app.usecases.todos import \
    TodoUseCases  
from ..repositories.todo_repository_impl import TodoRepositoryImpl
from langchain_tavily import TavilySearch
from ...app.usecases.rag import RAGUseCases
import datetime
logger = logging.getLogger(__name__)

# ===========================
# VALIDATION FUNCTIONS (TOOL-LED FAILSAFE)
# ===========================

def _validate_todo_creation(
    title: str,
    description: str,
    due_date: Optional[str]
) -> Optional[str]:
    """
    Kiểm tra đủ thông tin để tạo todo (FAILSAFE).
    Return clarification message nếu thiếu, else None.
    """
    missing_fields = []
    
    if not title or not title.strip():
        missing_fields.append("**tiêu đề (title)**")
    
    if not description or not description.strip():
        missing_fields.append("**mô tả chi tiết (description)**")
    
    if not due_date or not due_date.strip():
        missing_fields.append("**thời hạn (due_date)**")
    
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        
        # Tạo ví dụ động dựa trên trường thiếu
        examples = []
        if "tiêu đề" in missing_text:
            examples.append(
                "📌 Ví dụ tiêu đề: 'Mua sữa', 'Học bài chapter 5', 'Họp team lúc 3h'"
            )
        
        if "mô tả" in missing_text and title:
            examples.append(
                f"📝 Ví dụ mô tả cho task '{title}': "
                f"'Mua 2 lít sữa tươi TH True Milk ở siêu thị gần nhà'"
            )
        elif "mô tả" in missing_text:
            examples.append(
                "📝 Ví dụ mô tả: 'Hoàn thành bài tập trang 45-50', "
                "'Chuẩn bị slide báo cáo'"
            )
        
        if "thời hạn" in missing_text:
            examples.append(
                "⏰ Ví dụ thời hạn:\n"
                "   - 'hôm nay 5h chiều' → 2025-11-14T17:00:00\n"
                "   - 'ngày mai 9h sáng' → 2025-11-15T09:00:00\n"
                "   - 'thứ 6 tuần này lúc 2h chiều' → 2025-11-15T14:00:00"
            )
        
        example_text = "\n".join(examples)
        
        return (
            f"CLARIFY: Để tạo task, tôi cần thêm thông tin sau: {missing_text}.\n\n"
            f"{example_text}\n\n"
            f"Bạn có thể cung cấp thêm không?"
        )
    
    return None

def _validate_todo_update(
    todo_id: Optional[int],
    title_query: Optional[str],
    new_title: Optional[str],
    description: Optional[str],
    priority: Optional[int],
    completed: Optional[bool],
    due_date: Optional[str]
) -> Optional[str]:
    """
    Validate UPDATE: Phải có identifier + ít nhất 1 field mới (FAILSAFE).
    """
    # 1. Kiểm tra có identifier không
    if not todo_id and not title_query:
        return (
            "CLARIFY: Để cập nhật task, tôi cần biết **task nào** cần sửa. "
            "Bạn có thể cung cấp:\n"
            "  • **ID của task** (ví dụ: 'sửa task số 3')\n"
            "  • **Tên task** (ví dụ: 'sửa task mua sữa')\n\n"
            "Task nào bạn muốn cập nhật?"
        )
    
    # 2. Kiểm tra có field cần update không
    updated_fields = []
    if new_title and new_title.strip():
        updated_fields.append("title")
    if description and description.strip():
        updated_fields.append("description")
    if priority is not None:
        updated_fields.append("priority")
    if completed is not None:
        updated_fields.append("completed")
    if due_date and due_date.strip():
        updated_fields.append("due_date")
    
    if not updated_fields:
        identifier = (
            f"task số **{todo_id}**" if todo_id else f"task **'{title_query}'**"
        )
        return (
            f"CLARIFY: Tôi đã biết {identifier}, nhưng bạn muốn sửa **gì**?\n\n"
            f"Bạn có thể thay đổi:\n"
            f"  • Tiêu đề mới\n"
            f"  • Mô tả mới\n"
            f"  • Thời hạn mới\n"
            f"  • Mức độ ưu tiên (1-5)\n"
            f"  • Đánh dấu hoàn thành (có/không)\n\n"
            f"Bạn muốn thay đổi điều gì?"
        )
    
    return None

def _validate_todo_deletion(
    todo_id: Optional[int],
    title: Optional[str],
    confirmation: str = ""
) -> Optional[str]:
    """
    Validate DELETE: Phải có identifier + XÁC NHẬN (FAILSAFE).
    """
    # 1. Kiểm tra identifier
    if not todo_id and not title:
        return (
            "CLARIFY: Để xóa task, tôi cần biết **task nào** cần xóa. "
            "Bạn có thể cung cấp:\n"
            "  • **ID của task** (ví dụ: 'xóa task số 3')\n"
            "  • **Tên task** (ví dụ: 'xóa task mua sữa')\n\n"
            "Task nào bạn muốn xóa?"
        )
    
    # 2. Kiểm tra xác nhận (LUÔN HỎI nếu chưa có)
    identifier = f"task số **{todo_id}**" if todo_id else f"task **'{title}'**"
    
    # Nếu chưa có confirmation hoặc không hợp lệ → HỎI
    if not confirmation or confirmation.lower() not in [
        "có", "yes", "chắc chắn", "đồng ý", "ok"
    ]:
        return (
            f"CLARIFY: Bạn có **CHẮC CHẮN** muốn xóa {identifier} không? "
            f"Hành động này **không thể hoàn tác**.\n\n"
            f"📌 Trả lời **'Có'** để xác nhận, hoặc **'Không'** để hủy."
        )
    
    return None

# ===========================
# EXECUTE FUNCTIONS (LOGIC)
# ===========================
# --- ADD TODO LOGIC ---
def execute_add_todo(db: Session, owner_id: int, title: str, priority: int = 1, description: str = "",due_date: Optional[str] = None) -> str:
    """Logic for adding a Todo."""
    logger.info(f"Executing add_todo logic for user {owner_id}")
    clarify_msg = _validate_todo_creation(title, description,due_date)
    if clarify_msg:
        logger.info("[ADD_TODO] Validation failed → Returning clarification")
        return clarify_msg
    due_date_obj: Optional[datetime.datetime] = None
    if due_date:
        try:
            
            due_date_obj = datetime.datetime.fromisoformat(due_date)
            
            
            if due_date_obj.tzinfo is None:
                
                local_tz = pytz.timezone("Asia/Ho_Chi_Minh")
                due_date_obj = local_tz.localize(due_date_obj)
            
            logger.info(f"Parsed due_date: {due_date_obj}")
        except ValueError:
            logger.warning(f"Invalid due_date format received: {due_date}")
            return (
                f"CLARIFY: Thời hạn **'{due_date}'** không hợp lệ. "
                f"Vui lòng dùng định dạng: **YYYY-MM-DDTHH:MM:SS**\n\n"
                f"📌 Ví dụ:\n"
                f"  • '2025-11-14T17:00:00' (hôm nay 5h chiều)\n"
                f"  • '2025-11-15T09:00:00' (ngày mai 9h sáng)"
            )
        except Exception as e:
            logger.error(f"Error parsing due_date: {e}")
            return f"Lỗi khi xử lý ngày giờ: {e}"
    try:
        repo = TodoRepositoryImpl(db)
        usecase = TodoUseCases(repo)
        
        # ✅ FIX: Gọi add_todo (không phải create_todo)
        new_todo = usecase.create_todo(
            owner_id=owner_id,
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            due_date=due_date_obj
        )
        
        formatted_due = (
            due_date_obj.strftime("%d/%m/%Y %H:%M") if due_date_obj else "Không có"
        )
        logger.info(f"[ADD_TODO] Success → Created todo ID {new_todo.id}")
        
        return (
            f"✅ Đã tạo task mới (ID: #{new_todo.id}):\n"
            f"  • **Tiêu đề:** {new_todo.title}\n"
            f"  • **Mô tả:** {new_todo.description}\n"
            f"  • **Thời hạn:** {formatted_due}"
        )
    except Exception as e:
        logger.error(f"[ADD_TODO] Error: {e}", exc_info=True)
        return f"❌ Lỗi khi tạo task: {str(e)}"
    

# --- LIST TODOS LOGIC ---
def execute_list_todos(db: Session, owner_id: int) -> str:
    """
    FIX: Liệt kê tất cả todo dưới dạng Markdown Table.
    LUÔN trả về string (KHÔNG BAO GIỜ None)
    """
    logger.info(f"[LIST_TODOS] User {owner_id}")
    try:
        repo = TodoRepositoryImpl(db)
        usecase = TodoUseCases(repo)
        
        # FIX: Gọi list_todos (không phải get_all_todos)
        todos = usecase.get_all_todos(owner_id)
        
        if not todos:
            return "Bạn chưa có task nào. Hãy tạo task mới bằng cách nói: **'Tạo task...'**"
        
        # FIX: Markdown Table format
        result = "**Danh sách task của bạn:** \n\n"  # Thêm space ở đây
        result += "| ID | Hoàn thành | Tiêu đề | Ưu tiên | Thời hạn |\n"
        result += "|:---|:---:|:---|:---:|:---|\n"
        
        for todo in todos:
            status = "Yes" if todo.completed else "No"
            # Rút gọn ngày tháng cho vừa bảng
            due = todo.due_date.strftime("%d/%m %H:%M") if todo.due_date else "N/A"
            priority_str = f"{todo.priority}/5"
            # Đảm bảo tiêu đề không phá vỡ bảng (thay | bằng dấu cách)
            title = todo.title.replace("|", "&#124;")
            
            result += f"| #{todo.id} | {status} | {title} | {priority_str} | {due} |\n"
        logger.info(f"[LIST_TODOS] Returning {len(todos)} tasks")
        
        return result
    except Exception as e:
        logger.error(f"[LIST_TODOS] Error: {e}", exc_info=True)
        return f"❌ Lỗi khi lấy danh sách: {str(e)}"

# --- UPDATE TODO LOGIC ---
def execute_update_todo(
    db: Session,
    owner_id: int,
    todo_id: Optional[int] = None,
    title_query: Optional[str] = None,
    new_title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    completed: Optional[bool] = None,
    due_date: Optional[str] = None
) -> str:
    """Cập nhật todo với failsafe validation."""
    logger.info(
        f"[UPDATE_TODO] User {owner_id} | todo_id={todo_id} | "
        f"title_query='{title_query}'"
    )
    
    # ✅ Failsafe validation
    clarify_msg = _validate_todo_update(
        todo_id, title_query, new_title, description, priority, completed, due_date
    )
    if clarify_msg:
        logger.info("[UPDATE_TODO] Validation failed → Returning clarification")
        return clarify_msg
    
    try:
        repo = TodoRepositoryImpl(db)
        usecase = TodoUseCases(repo)

        # Tìm target_id từ title_query nếu todo_id is None
        target_id = todo_id
        current_todo = None
        if target_id:
            current_todo = usecase.get_todo_by_id(target_id, owner_id)
        elif title_query:
            # ✅ FIX: Gọi list_todos
            all_todos = usecase.get_all_todos(owner_id)
            for t in all_todos:
                if t.title.lower() == title_query.lower():
                    target_id = t.id
                    current_todo = t
                    break
        
        if not target_id or not current_todo:
            return (
                f"❌ Lỗi: Không tìm thấy task nào khớp với "
                f"ID {todo_id} hoặc tên '{title_query}'."
            )

        # Xử lý due_date nếu có
        due_date_obj = current_todo.due_date  # Giữ nguyên nếu không cung cấp
        if due_date:
            try:
                due_date_obj = datetime.datetime.fromisoformat(due_date)
                if due_date_obj.tzinfo is None:
                    local_tz = pytz.timezone("Asia/Ho_Chi_Minh")
                    due_date_obj = local_tz.localize(due_date_obj)
            except Exception:
                return (
                    f"CLARIFY: Định dạng due_date '{due_date}' không hợp lệ. "
                    f"Vui lòng dùng YYYY-MM-DDTHH:MM:SS."
                )

        updated_todo = usecase.update_todo(
            todo_id=target_id,
            owner_id=owner_id,
            title=new_title.strip() if new_title else current_todo.title,
            description=(
                description.strip() if description else current_todo.description
            ),
            priority=priority if priority is not None else current_todo.priority,
            completed=(
                completed if completed is not None else current_todo.completed
            ),
            due_date=due_date_obj
        )
        
        if not updated_todo:
            raise Exception("Hàm update_todo không trả về kết quả.")

        logger.info(f"[UPDATE_TODO] Success → Updated todo ID {updated_todo.id}")
        
        return (
            f"✅ Đã cập nhật task (ID: #{updated_todo.id}):\n"
            f"  • **Tiêu đề:** {updated_todo.title}\n"
            f"  • **Hoàn thành:** {'Có ✅' if updated_todo.completed else 'Chưa ⬜'}"
        )
    except Exception as e:
        logger.error(f"[UPDATE_TODO] Error: {e}", exc_info=True)
        return f"❌ Lỗi khi cập nhật: {str(e)}"

# --- DELETE TODO LOGIC ---
def execute_delete_todo(
    db: Session,
    owner_id: int,
    todo_id: Optional[int] = None,
    title: Optional[str] = None,
    confirmation: str = ""
) -> str:
    """Xóa todo với xác nhận (FAILSAFE quan trọng)."""
    logger.info(
        f"[DELETE_TODO] User {owner_id} | todo_id={todo_id} | "
        f"title='{title}' | confirmation='{confirmation}'"
    )
    
    # ✅ Failsafe validation
    clarify_msg = _validate_todo_deletion(todo_id, title, confirmation)
    if clarify_msg:
        logger.info("[DELETE_TODO] Validation/Confirmation failed → Returning clarification")
        return clarify_msg
    
    try:
        repo = TodoRepositoryImpl(db)
        usecase = TodoUseCases(repo)
        
        # Tìm target_id từ title nếu todo_id is None
        target_id = todo_id
        target_title = title
        if not target_id and title:
            # ✅ FIX: Gọi list_todos
            all_todos = usecase.get_all_todos(owner_id)
            for t in all_todos:
                if t.title.lower() == title.lower():
                    target_id = t.id
                    target_title = t.title
                    break
        
        if not target_id:
            return (
                f"❌ Lỗi: Không tìm thấy task nào khớp với "
                f"ID {todo_id} hoặc tên '{title}'."
            )

        success = usecase.delete_todo(owner_id=owner_id, todo_id=target_id)
        
        if not success:
            raise Exception("Hàm delete_todo trả về False.")

        identifier = f"ID #{target_id}" if target_id else f"'{target_title}'"
        logger.info(f"[DELETE_TODO] Success → Deleted {identifier}")
        
        return f"✅ Đã xóa task {identifier} thành công."
    except Exception as e:
        logger.error(f"[DELETE_TODO] Error: {e}", exc_info=True)
        return f"❌ Lỗi khi xóa task: {str(e)}"

# --- TOGGLE COMPLETION LOGIC ---
def execute_toggle_todo_completion(db: Session, owner_id: int, todo_id: int) -> str:
    """Logic for marking a Todo as complete/incomplete."""
    logger.info(f"Executing toggle_todo_completion logic for user {owner_id}, todo_id {todo_id}")
    try:
        usecase = TodoUseCases(TodoRepositoryImpl(db))
        current_todo = usecase.get_todo_by_id(todo_id=todo_id, owner_id=owner_id)
        if not current_todo:
            return f"Error: No task found with ID {todo_id}."

        new_completed_status = not current_todo.completed

        success = usecase.update_todo(
            todo_id=todo_id,
            owner_id=owner_id,
            title=current_todo.title,
            description=current_todo.description,
            priority=current_todo.priority,
            completed=new_completed_status,
            due_date= current_todo.due_date
        )

        if success:
            status_text = "completed" if new_completed_status else "not completed"
            return f"Marked task ID {todo_id} as '{status_text}'."
        else:
            return f"Error: Unable to update completion status for task ID {todo_id}."
    except Exception as e:
        logger.error(f"Error in execute_toggle_todo_completion: {e}")
        return f"Error updating status of task ID {todo_id}: {str(e)}"
    
def execute_search_internet(query: str , tavily_tools: TavilySearch ) -> str:
    """_summary_

    Args:
        query (str): _description_
        tavily_tool (TavilySearch): _description_

    Returns:
        str: _description_
    """
    logger.info(f"[TAVILY_LOGIC] Start execution for query: '{query}'")
    if tavily_tools is None:
        logger.error("[TAVILY_LOGIC] FATAL ERROR: tavily_tool is None!")
        return "Lỗi hệ thống: Công cụ tìm kiếm (Tavily) không được khởi tạo."
    try:
        logger.info("[TAVILY_LOGIC] Preparing to call tavily_tool.invoke()....")
        results_string: str = tavily_tools.invoke(query)
        logger.info(f"[TAVILY_LOGIC] Tavily returned {len(results_string)} results.")
        if not results_string:
            logger.info(f"[TAVILY] returned no results for {query}")
            return f" khong tim thay ket qua tra ve {query}"
    
        return results_string
    except Exception as e:
        logger.exception(f"THERE WAS A FATAL ERROR running execute_search_internet with query: '{query}'")
        return f"Lỗi hệ thống khi tìm kiếm internet: {str(e)}. Quản trị viên đã được thông báo."
    
# ==========================================
# FACTORY FUNCTION (THÊM VÀO CUỐI FILE)
# ==========================================
def get_tools(
    db: Session,
    owner_id: int,
    tavily_tool: Optional[TavilySearch] = None,
    rag_usecase: Optional[RAGUseCases] = None
) -> List[BaseTool]:
    """
    Tạo tools với closure db/owner_id.
    Auto-add RAG tool nếu rag_usecase provided.
    """
    
    @tool
    def add_todo_tool(
        title: str,
        description: str,
        due_date: str,
        priority: int = 1
    ) -> str:
        """
        Thêm một công việc mới (Todo) vào danh sách của người dùng.
        
        ⚠️ CHỈ GỌI KHI ĐÃ CÓ ĐỦ 100% THÔNG TIN.
        AI phải tự kiểm tra và hỏi user trước khi gọi tool này.
        
        Args:
            title: Tiêu đề task (BẮT BUỘC)
            description: Mô tả chi tiết (BẮT BUỘC)
            due_date: Thời hạn ISO 8601 'YYYY-MM-DDTHH:MM:SS' (BẮT BUỘC)
            priority: Mức độ ưu tiên 1-5 (mặc định 1)
        
        Returns:
            Success message hoặc CLARIFY request nếu thiếu thông tin
        """
        return execute_add_todo(db, owner_id, title, priority, description, due_date)

    @tool
    def list_todos_tool() -> str:
        """
        ✅ LIỆT KÊ tất cả tasks của user.
        **WHEN TO USE:** 
        - User yêu cầu HIỂN THỊ/XEM danh sách tasks
        - Keywords: "liệt kê", "xem", "danh sách", "list", "todo nào"
        
        **CRITICAL:** 
        - KHÔNG CẦN parameters → Tự động lấy theo user đang login
        - GỌI NGAY khi detect keywords → KHÔNG HỎI user
        
        Returns:
            Markdown table: | ID | Hoàn thành | Tiêu đề | Ưu tiên | Thời hạn |
        """
        return execute_list_todos(db, owner_id)

    @tool
    def update_todo_tool(
        todo_id: Optional[int] = None,
        title_query: Optional[str] = None,
        new_title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        completed: Optional[bool] = None,
        due_date: Optional[str] = None
    ) -> str:
        """
        Cập nhật task hiện có.
        
        ⚠️ AI phải đảm bảo có identifier (todo_id HOẶC title_query) + ít nhất 1 field mới.
        
        Args:
            todo_id: ID của task (ưu tiên)
            title_query: Tên task (nếu không có ID)
            new_title: Tiêu đề mới (TÙY CHỌN)
            description: Mô tả mới (TÙY CHỌN)
            priority: Ưu tiên mới (1-5) (TÙY CHỌN)
            completed: Trạng thái hoàn thành (TÙY CHỌN)
            due_date: Thời hạn mới 'YYYY-MM-DDTHH:MM:SS' (TÙY CHỌN)
        
        Returns:
            Success message hoặc CLARIFY request
        """
        return execute_update_todo(
            db=db,
            owner_id=owner_id,
            todo_id=todo_id,
            title_query=title_query,
            new_title=new_title,
            description=description,
            priority=priority,
            completed=completed,
            due_date=due_date
        )

    @tool
    def delete_todo_tool(
        todo_id: Optional[int] = None,
        title: Optional[str] = None,
        confirmation: str = ""
    ) -> str:
        """
        Xóa task (CẦN XÁC NHẬN).
        
        ⚠️ AI PHẢI HỎI XÁC NHẬN TỪ USER TRƯỚC KHI GỌI TOOL NÀY.
        KHÔNG BAO GIỜ gọi tool này mà không có xác nhận.
        
        Args:
            todo_id: ID của task
            title: Tên task (nếu không có ID)
            confirmation: Xác nhận từ user ('Có', 'Yes', 'Chắc chắn', 'ok', 'đồng ý')
        
        Returns:
            Confirmation request hoặc success message
        """
        return execute_delete_todo(db, owner_id, todo_id, title, confirmation)

    @tool
    def mark_complete_tool(todo_id: int) -> str:
        """
        Đánh dấu một công việc là đã hoàn thành/chưa hoàn thành (đảo trạng thái).
        
        Args:
            todo_id: ID của task
        
        Returns:
            Success message
        """
        return execute_toggle_todo_completion(db, owner_id, todo_id)

    @tool
    def search_internet_tool(query: str) -> str:
        """
        Tìm kiếm thông tin CÔNG KHAI trên internet (tin tức, kiến thức chung).
        
        Args:
            query: Câu hỏi cần tra cứu
        
        Returns:
            Kết quả tìm kiếm từ Tavily
        """
        if not tavily_tool:
            return "Chức năng tìm kiếm internet hiện không khả dụng."
        return execute_search_internet(query, tavily_tool)

    # Tổng hợp danh sách tools
    tools = [
        add_todo_tool,
        list_todos_tool,
        update_todo_tool,
        delete_todo_tool,
        mark_complete_tool,
        search_internet_tool
    ]
    
    # Thêm RAG tool nếu có
    if rag_usecase:
        @tool
        def search_knowledge_base_tool(query: str) -> str:
            """
            Tìm kiếm trong cơ sở kiến thức cá nhân của user.
            CHỈ DÙNG khi user hỏi rõ ràng về 'tài liệu của tôi', 'file tôi upload'.
            
            Args:
                query: Câu hỏi về tài liệu cá nhân
            
            Returns:
                Thông tin từ cơ sở kiến thức
            """
            logger.info(
                f"Agent is calling search_knowledge_base for user {owner_id} "
                f"with query: '{query}'"
            )
            return rag_usecase.retrieve_context(user_id=owner_id, query=query)
        
        tools.append(search_knowledge_base_tool)
        logger.info("RAG tool added to agent tools.")

    return tools