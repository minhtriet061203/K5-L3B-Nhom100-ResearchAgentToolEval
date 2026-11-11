"""Chạy ba kịch bản UI với API thật và lưu transcript, không gửi Telegram thật."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest


def main() -> None:
    scenarios = {
        "research": [
            'Tìm 2 tin web hôm nay về "clean energy" và tóm tắt mỗi tin trong một câu, có link nguồn.',
        ],
        "missing_information": [
            "Lấy 2 bài đăng mới nhất giúp tôi.",
            "Tài khoản @NASA nhé, vẫn 2 bài.",
        ],
        "publication_confirmation": [
            'Đăng bản tin "Điểm tin nghiên cứu: nhóm đã hoàn thành phần tổng hợp nguồn." lên Telegram của nhóm.',
            "Tôi đồng ý chuẩn bị, chưa cho phép gửi.",
            'Nội dung cuối vẫn là "Điểm tin nghiên cứu: nhóm đã hoàn thành phần tổng hợp nguồn." Hãy hỏi tôi xác nhận trước khi gửi lên Telegram của nhóm.',
            'Tôi xác nhận gửi chính xác nội dung "Điểm tin nghiên cứu: nhóm đã hoàn thành phần tổng hợp nguồn." lên Telegram của nhóm.',
        ],
    }
    evidence = []
    for name, queries in scenarios.items():
        at = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        assert not at.exception, at.exception
        at.session_state.transcript["source"] = "streamlit-apptest-live"
        at.session_state.transcript["demo_scenario"] = name
        for index, query in enumerate(queries, 1):
            print(f"{name}: {index}/{len(queries)}", flush=True)
            at.chat_input[0].set_value(query).run(timeout=180)
            assert not at.exception, at.exception
            record = at.session_state.transcript["turns"][-1]
            print(json.dumps({"status": record["status"], "tools": [e["tool"] for e in record["tool_events"]]}, ensure_ascii=True), flush=True)
        transcript = at.session_state.transcript
        evidence.append({
            "scenario": name,
            "file": f"starter_v0/transcripts/{transcript['transcript_id']}.transcript.json",
            "statuses": [t["status"] for t in transcript["turns"]],
        })
    output = ROOT.parent / "report/team/evidence/ui_live_demo.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    assert all("provider_error" not in e["statuses"] for e in evidence), evidence
    print(f"Saved: {output}", flush=True)


if __name__ == "__main__":
    main()
