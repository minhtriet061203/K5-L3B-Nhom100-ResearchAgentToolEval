"""Kiểm tra hội thoại nhiều lượt và chặn gửi thật trong phiên demo."""
import json

import app
import chat
from providers.base import ModelResponse, ToolCall


class SequenceProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(list(messages))
        return next(self.responses)


def test_demo_never_dispatches_send_even_when_model_sets_confirmed(monkeypatch):
    def forbidden(call):
        raise AssertionError("Không được gọi tool gửi thật")
    monkeypatch.setattr(app, "execute_tool_call", forbidden)
    event = app.demo_tool_executor(ToolCall("send", {"text": "Bản tin", "confirmed": True}))
    assert event["result"]["status"] == "demo_preview"


def test_clarification_pauses_and_next_turn_uses_supplied_information(monkeypatch):
    provider = SequenceProvider([
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Tài khoản nào?", "response_type": "text"})]),
        ModelResponse(tool_calls=[ToolCall("timeline", {"screenname": "NASA", "limit": 2})]),
        ModelResponse(text="Đã tổng hợp hai bài từ NASA."),
    ])
    actual_executor = app.execute_tool_call
    def local_executor(call):
        if call.name == "timeline":
            return {"tool": "timeline", "args": call.args, "result": {"items": []}}
        return actual_executor(call)
    monkeypatch.setattr(app, "execute_tool_call", local_executor)
    session = app.new_session()
    first = app.submit_turn(session, "Lấy 2 bài mới nhất", provider)
    assert first["status"] == "waiting_for_user"
    assert len(first["tool_events"]) == 1
    second = app.submit_turn(session, "Tài khoản NASA", provider)
    assert second["status"] == "answered"
    assert second["tool_events"][0]["args"] == {"screenname": "NASA", "limit": 2}
    assert any(m["content"] == "Tài khoản nào?" for m in provider.messages[1])


def test_provider_error_is_recorded_without_exposing_exception_details():
    class BrokenProvider:
        def complete(self, *args, **kwargs):
            raise RuntimeError("chi-tiet-nhay-cam")
    session = app.new_session()
    record = app.submit_turn(session, "Tìm tin", BrokenProvider())
    assert record["status"] == "provider_error"
    assert record["error"] == "RuntimeError"
    assert "chi-tiet-nhay-cam" not in json.dumps(session)


def test_streamlit_loads_with_chat_input_and_new_session_button():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(app.ROOT / "app.py")).run(timeout=15)
    assert not at.exception
    assert len(at.chat_input) == 1
    previous_id = at.session_state.transcript["transcript_id"]
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert at.session_state.transcript["transcript_id"] != previous_id
    assert at.session_state.transcript["turns"] == []


def test_chat_tool_log_is_safe_for_ascii_console(monkeypatch):
    logs = []
    def ascii_console(message):
        logs.append(message.encode("ascii"))
    monkeypatch.setattr(chat, "print", ascii_console, raising=False)
    provider = SequenceProvider([
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Bạn muốn nguồn nào?", "response_type": "text"})]),
    ])
    session = app.new_session()
    result = app.submit_turn(session, "Tìm nguồn", provider)
    assert result["status"] == "waiting_for_user"
    assert len(logs) == 1


def test_tool_errors_are_visible_without_opening_the_activity_panel():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string('''
from app import render_turn
render_turn({
    "user": "Tìm tin", "assistant_text": "Chưa có đủ kết quả.", "status": "answered",
    "tool_events": [{"tool": "lookup", "args": {}, "result": {"error": "RuntimeError", "message": "Thiếu cấu hình"}}]
})
''').run(timeout=15)
    assert not at.exception
    assert len(at.warning) == 1
    assert "lookup" in at.warning[0].value
