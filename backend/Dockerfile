# ==========================================
# STAGE 1: BUILDER (Môi trường cài đặt)
# ==========================================
FROM python:3.11-slim as builder

# Đặt thư mục làm việc
WORKDIR /app

# Cài đặt các công cụ cần thiết để build các package Python (ví dụ: psycopg2 cho Postgres)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy file requirements (Đảm bảo bạn đã có file requirements.txt trong thư mục backend)
COPY requirements.txt .

# Tạo các file binary (wheels) cho thư viện thay vì cài đặt trực tiếp
# Điều này giúp sang Stage 2 không cần mang theo gcc hay cache nữa
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==========================================
# STAGE 2: RUNNER (Môi trường chạy thực tế)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Chỉ cài đặt thư viện runtime cho PostgreSQL (nhẹ hơn libpq-dev rất nhiều)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

# Tạo user không có quyền root (Security Best Practice)
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy wheels từ STAGE 1 sang và cài đặt
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy toàn bộ mã nguồn (src, alembic, alembic.ini)
COPY ./src ./src
COPY ./alembic ./alembic
COPY alembic.ini .

# Cấp quyền sở hữu thư mục cho appuser
RUN chown -R appuser:appgroup /app

# Chuyển sang dùng appuser thay vì root
USER appuser

# Expose port (Thông báo cho Docker biết container dùng port nào)
EXPOSE 8000

# Lệnh khởi chạy được định nghĩa trong docker-compose.yml nên có thể bỏ trống ở đây, 
# hoặc set mặc định như sau:
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]