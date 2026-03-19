# Todos project
Huog dan chay: chay moi truong :
 & "C:\Users\thangtm25\AppData\Local\pypoetry\Cache\virtualenvs\todos-list-Aod6zpnz-py3.13\Scripts\Activate.ps1"

poetry run uvicorn api.main:app --reload

hoach
poetry shell
uvicorn api.main:app --reload

 fastapi dev backend\todo_backend\api\main.py --reload

 deactivate

 huong dan alembic 
 TAO DU AN :
 alembic init alembic

 TAO THAY DOI:
 alembic revision --autogenerate -m "Mô tả thay đổi"   Để áp dụng các thay đổi vào cơ sở dữ liệu, chạy lệnh:
 alembic upgrade head
 alembic downgrade -1 Quay lại phiên bản trước:
 alembic current

 Giả sử bạn thêm một cột mới age vào bảng Users trong tệp models.py:

Python
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String, nullable=True)
    age = Column(Integer, nullable=True)  # Thêm cột mới
Chạy lệnh:

Bash
alembic revision --autogenerate -m "Add age column to Users"
alembic upgrade head


dunng cong chiem serrver 
netstat -ano | findstr :8000  kiem tra 

taskkill /IM python.exe /F     kill het ok
cmd //c "taskkill /IM python.exe /F" git bash

isort . xắp xếp inport

lẹnh git : chưa tạo git : git init, git add ., git commit -m "", 
tạo rồi: thêm commit mới:
git add . , git commit -m "", git log xem , git status xem trạng thái , git checkout <..comit_id> trở lại commit củ 


cach chua benh bang poetry 
 C:\Todos\backend>
 
 uvicorn todo_backend.main:app --reload

 poetry config virtualenvs.in-project true 

 chạy cai nay truoc 
 $ poetry env info
 roi chạy cai $ C
(todos-py3.13) 

roi chạy cai nay 
$ uvicorn src.main:app --reload


đầu tiên phải vào đúng cấu trúc thư mục trước
cd.. để out ra
tiếp theo 
kích hoạt môi trường ảo đúng  source .venv/Scripts/activate
tiếp theo chạy môi trường ảo sẽ tự động uvicorn src.main:app --reload

tại sao lại vậy? tại sao lại vào đúng, Khi môi trường ảo hoạt động sẽ tự sinh ra file .venv . vào đúng để gọi thư mục activate trong venv 

Tại sao file chạy lại nằm ở .venv/Scripts/activate mà ko ở chỗ khác như .venv/run hay j khác 
.venv là tn môi trường ảo , 
. là để ẩn thư mục trong unix_like system ( hệ điều hành ảo tương tự hệ điều hành gốc , để sử dụng )
 venv là viết tắt của virtual eviroment ( môi trường py độc lập)

scripts ( kịch bản) là khi scripts trên win , bin trên unix 
chứa các file thực thi 
activate là 1 trong cac file thực thi 

khi clone dự án về bạn cần phải:
1. Chạy lệnh poetry install để cài đặt tất cả các phụ thuộc được liệt kê trong tệp pyproject.toml.
2. Kích hoạt môi trường ảo bằng lệnh source .venv/Scripts/activate (trên Windows) hoặc source .venv/bin/activate (trên Unix-like systems).
3. Chạy ứng dụng bằng lệnh uvicorn src.main:app --reload.

nếu gặp vấn đè
$ poetry install
bash: poetry: command not found
hãy chạy lệnh

Mở Git Bash và gõ:
python --version

2. Nếu Python đã được cài đặt, bạn sẽ thấy phiên bản của nó. Nếu không, hãy tải và cài đặt Python từ trang chính thức: https://www.python.org/downloads/

3. Cài đặt Poetry bằng lệnh sau:
curl -sSL https://install.python-poetry.org | py -

4. Sau khi cài đặt xong, hãy đóng và mở lại Git Bash để cập nhật biến môi trường.

Thêm đường dẫn vào Biến Môi trường (Environment Variables)
Nhấn phím Windows, gõ env và chọn "Edit the system environment variables" (Chỉnh sửa các biến môi trường hệ thống).

Trong cửa sổ System Properties, nhấn vào nút "Environment Variables..." (Biến môi trường...).

Trong cửa sổ mới, nhìn vào ô phía trên ("User variables for Tên_Người_Dùng"). Tìm và chọn biến Path, sau đó nhấn "Edit..." (Chỉnh sửa...).

Nhấn "New" (Mới) và dán đường dẫn của Poetry vào:

C:\Users\Admin-PC\AppData\Roaming\pypoetry\venv\Scripts

Admin-PC là tên máy tính của bạn, có thể khác với tên máy tính trong ví dụ này.
Nhấn OK ở tất cả các cửa sổ để lưu lại thay đổi.

poetry --version

sau đó chạy lại lệnh poetry install

sau đó chạy tiếp các bước kích hoạt môi trường ảo và chạy ứng dụng như đã hướng dẫn ở trên.
$ poetry env activate
kích hoạt môi trường ảo

sửa lại đường dẫn đúng trong .env

và packages = [
    { include = "todo_backend" ,from = "src" }
]



#### Cach sua vàng, dung poetry env info , roi copy duong dan dai nhat 
vao STR + shift + p roi select inter.. roi chọn enter interpreter path dan vao duong dẫn roi vao powershell .. ? 
