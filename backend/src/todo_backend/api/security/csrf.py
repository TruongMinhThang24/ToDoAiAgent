import secrets

from fastapi import HTTPException, Request, status

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"
AUTH_COOKIE_NAME = "access_token"


def _is_exempt_path(path: str) -> bool:
    """Các endpoint public/infra không yêu cầu CSRF."""
    return (
        path in {"/health", "/auth/token", "/auth/register", "/auth/"}
        or path.startswith("/docs")
        or path.startswith("/redoc")
        or path.startswith("/openapi")
    )


async def validate_csrf_request(request: Request) -> None:
    """
    Validate CSRF theo mô hình Double Submit Cookie.

    Rule:
    - Bỏ qua method an toàn (GET/HEAD/OPTIONS).
    - Bỏ qua endpoint public được whitelist.
    - Chỉ enforce với request có phiên đăng nhập (có access_token cookie).
    - Với request ghi dữ liệu: cookie csrf_token và header X-CSRF-Token phải tồn tại và khớp nhau.
    """
    if request.method in SAFE_METHODS:
        return

    path = request.url.path
    if _is_exempt_path(path):
        return

    # Chỉ áp CSRF cho request đang có phiên đăng nhập cookie-based.
    if not request.cookies.get(AUTH_COOKIE_NAME):
        return

    csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
    csrf_header = request.headers.get(CSRF_HEADER_NAME)

    if not csrf_cookie or not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )

    if not secrets.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )
