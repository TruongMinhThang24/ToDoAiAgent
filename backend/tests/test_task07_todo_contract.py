from pydantic import ValidationError

from todo_backend.api.schemas.todos_schema import TodoRequest


def test_todo_request_accepts_contract_fields() -> None:
    payload = TodoRequest(
        title="Task 07 contract",
        description="payload mapping",
        priority=3,
        status="not_started",
        completed=False,
        due_date=None,
        thumbnail_url="https://example.com/thumb.png",
        is_vital=True,
        checklist_data=[{"label": "step 1", "done": False}],
    )

    assert payload.title == "Task 07 contract"
    assert payload.priority == 3
    assert payload.status == "not_started"
    assert payload.thumbnail_url == "https://example.com/thumb.png"
    assert payload.is_vital is True


def test_todo_request_rejects_blob_thumbnail_url() -> None:
    try:
        TodoRequest(
            title="Task with local blob",
            description="invalid thumbnail",
            priority=2,
            thumbnail_url="blob:http://localhost:3000/abc",
        )
    except ValidationError as exc:
        assert "thumbnail_url must be a server-accessible URL" in str(exc)
        return

    raise AssertionError("Expected TodoRequest to reject blob thumbnail URL")
