# 🎯 Task 20: Xây dựng Giao diện "Phòng Trò Chuyện" (Voice-to-Voice AI)

## 1. Context
Backend xử lý Voice-to-Voice (nhận file audio, trả về file audio) ĐÃ HOÀN THIỆN. 
Nhiệm vụ của bạn bây giờ CHỈ LÀ LÀM FRONTEND. Cần tạo một giao diện "Phòng trò chuyện" độc lập với Text Chat, cho phép người dùng thu âm và phát lại phản hồi của AI.

## 2. Requirements (Chỉ thao tác trên Frontend)

**BƯỚC 1: ĐIỀU HƯỚNG & SIDEBAR**
- Cập nhật Component Sidebar (thanh điều hướng bên trái): Thêm một menu item tên là "Phòng trò chuyện" (hoặc Voice Room) với icon Microphone.
- Đảm bảo Routing của React/Vue chuyển hướng đúng sang trang mới này mà không làm hỏng trang Text Chat cũ.

**BƯỚC 2: XÂY DỰNG COMPONENT `VoiceRoom`**
- Tạo UI tối giản: Chính giữa màn hình là một nút Microphone lớn.
- **Quản lý Trạng thái (State):** `isRecording` (Đang thu âm), `isProcessing` (Đang chờ AI trả lời).
- **Logic Thu âm (Web Audio API):**
  - Dùng `navigator.mediaDevices.getUserMedia({ audio: true })` và `MediaRecorder`.
  - Khi user bấm nút: Bắt đầu thu âm. Hiển thị hiệu ứng/chữ "Đang nghe...".
  - Khi user bấm dừng: Đóng gói các audio chunks thành dạng `Blob` (audio/webm hoặc audio/mp3).

**BƯỚC 3: KẾT NỐI API & PHÁT AUDIO (Có tích hợp BYOK)**
- Lấy Gemini API Key từ `localStorage` (giống luồng Text Chat).
- Tạo `FormData` chứa file audio vừa thu.
- Gọi hàm `fetch` tới endpoint Voice của Backend (hãy tìm trong code Backend xem endpoint voice là `/api/v1/chat/voice` hay gì để điền cho đúng).
- **Headers bắt buộc:** Nhét header cấu hình API Key vào (ví dụ: `X-Gemini-API-Key`).
- **Xử lý Response:** Nhận dữ liệu trả về dạng Blob (`response.blob()`), tạo URL (`URL.createObjectURL`), và dùng đối tượng `new Audio(audioUrl).play()` để phát giọng nói của AI. Hiển thị trạng thái "AI đang nói...".

HÀNH ĐỘNG CỦA BẠN:
1. Đọc lướt qua code Frontend hiện tại để nắm cấu trúc (Router, Sidebar).
2. Kiểm tra nhanh file Router Backend để lấy đúng URL của endpoint Voice.
3. Nhả Code Block tạo mới file `VoiceRoom` (React/Vue component), cập nhật Sidebar và hệ thống Routing. KHÔNG chạm vào code Backend.