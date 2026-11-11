from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

from chat import execute_tool_call, json_text, now_iso, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from providers.base import ToolCall
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"


def new_session(provider: str = "openai", model: str = "gpt-4o-mini") -> dict[str, Any]:
    return {
        "transcript_id": f"v3-ui_{datetime.now():%Y%m%dT%H%M%S}_{uuid4().hex[:8]}",
        **artifact_version_dict(build_artifact_version("v3-ui", PROMPT, TOOLS)),
        "provider": provider,
        "model": model,
        "system_prompt": str(PROMPT),
        "tools": str(TOOLS),
        "source": "streamlit",
        "demo_mode": True,
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def demo_tool_executor(call: ToolCall) -> dict[str, Any]:
    if call.name == "send":
        return {
            "tool": call.name,
            "args": call.args,
            "result": {
                "tool": "send_telegram",
                "status": "demo_preview",
                "message": "Chế độ demo: chỉ tạo bản xem trước, chưa gửi Telegram thật.",
                "text": call.args.get("text", ""),
            },
        }
    return execute_tool_call(call)


def submit_turn(session: dict[str, Any], user_text: str, provider: Any = None) -> dict[str, Any]:
    history = []
    for turn in session["turns"]:
        if turn["status"] != "provider_error":
            history.extend([
                {"role": "user", "content": turn["user"]},
                {"role": "assistant", "content": turn["assistant_text"]},
            ])
    record = {
        "turn_index": len(session["turns"]) + 1,
        "started_at": now_iso(), "user": user_text,
        "rounds": [], "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=provider if provider is not None else make_provider(session["provider"]),
            messages=[
                {"role": "system", "content": PROMPT.read_text(encoding="utf-8")},
                *trim_history(history, session["history_window"]),
                {"role": "user", "content": user_text},
            ],
            tools=to_openai_tools(load_tool_declarations(TOOLS)),
            model=session["model"], max_tool_rounds=session["max_tool_rounds"],
            tool_executor=demo_tool_executor,
        )
        record.update(result)
        if any(e["result"].get("status") == "demo_preview" for e in result["tool_events"]):
            record["assistant_text"] = "Đã tạo bản xem trước. Chế độ demo không gửi Telegram thật; nội dung nằm trong phần hoạt động của agent."
            record["status"] = "demo_preview"
        elif record["status"] == "max_tool_rounds":
            record["assistant_text"] = "Agent đã đạt giới hạn xử lý của lượt này. Bạn có thể xem hoạt động bên dưới và tiếp tục yêu cầu."
    except Exception as exc:
        record.update({
            "status": "provider_error", "error": type(exc).__name__,
            "assistant_text": "Không thể hoàn thành lượt này. Hãy kiểm tra kết nối và cấu hình provider rồi thử lại.",
        })
    record["ended_at"] = now_iso()
    session["turns"].append(record)
    return record


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn["assistant_text"])
        if turn["status"] == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung hoặc xác nhận ở ô hội thoại bên dưới.")
        failed_tools = [e["tool"] for e in turn["tool_events"] if isinstance(e.get("result"), dict) and e["result"].get("error")]
        if failed_tools:
            st.warning("Tool gặp lỗi: " + ", ".join(failed_tools) + ". Xem chi tiết hoạt động bên dưới; kết quả có thể chưa đầy đủ.")
        if turn["tool_events"]:
            with st.expander("Xem hoạt động của agent"):
                for event in turn["tool_events"]:
                    st.markdown(f"**{event['tool']}**")
                    st.json(event)


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="centered")
    st.title("🔎 Research Agent")
    st.caption("Tìm nguồn · Đọc bài · Tổng hợp nghiên cứu")
    st.info("Phiên demo: agent xin xác nhận trước khi gửi; Telegram chỉ được xem trước, không gửi thật.")
    with st.sidebar:
        st.header("Phiên nghiên cứu")
        provider = st.selectbox("Nhà cung cấp cho phiên mới", ["openai", "openrouter"])
        default_model = "gpt-4o-mini" if provider == "openai" else "openai/gpt-4o-mini"
        model = st.text_input("Mô hình cho phiên mới", value=default_model, key=f"model_{provider}")
        if st.button("Bắt đầu phiên mới", use_container_width=True) or "transcript" not in st.session_state:
            st.session_state.transcript = new_session(provider, model.strip() or default_model)
        session = st.session_state.transcript
        st.caption(f"Đang dùng: {session['provider']} · {session['model']}")
        st.metric("Số lượt trao đổi", len(session["turns"]))
        st.download_button(
            "Tải bản ghi hội thoại", data=json_text(session),
            file_name=f"{session['transcript_id']}.transcript.json",
            mime="application/json", use_container_width=True,
        )
        st.caption("Thay đổi nhà cung cấp/mô hình được áp dụng khi bắt đầu phiên mới.")
    if not session["turns"]:
        st.markdown("### Bạn muốn nghiên cứu điều gì?")
        st.markdown("- Tìm 2 tin web hôm nay về năng lượng sạch.\n- Đọc và tóm tắt một URL bạn cung cấp.\n- Loại nguồn trùng trước khi chuẩn bị bản tin.")
    for turn in session["turns"]:
        render_turn(turn)
    if user_text := st.chat_input("Nhập yêu cầu hoặc trả lời câu hỏi của agent…"):
        with st.chat_message("user"):
            st.markdown(user_text)
        with st.spinner("Agent đang xử lý…"):
            submit_turn(session, user_text)
            write_transcript(ROOT / "transcripts" / f"{session['transcript_id']}.transcript.json", session)
        st.rerun()


if __name__ == "__main__":
    main()
