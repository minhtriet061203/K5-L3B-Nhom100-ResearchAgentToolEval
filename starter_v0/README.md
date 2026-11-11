# Source code

Toàn bộ source code của lab nằm trong folder này. Chạy mọi lệnh từ `starter_v0/`.

- File bắt đầu chạy: `run_eval.py` (chạy eval), `chat.py` (chat live), `scripts/preflight_provider.py` (kiểm tra provider).
- Cách chạy: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`; `python chat.py --provider openrouter --version v3`; `pytest`.
- Input: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, bộ case `data/*.json`, API key trong `.env` (mẫu ở `.env.example`).
- Output: `runs/*.json` (kết quả eval), `transcripts/*.transcript.json` (chat live), `analysis/*.csv` (nếu chạy `scripts/parse_runs.py`).
- File học viên được sửa: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tools/` (thêm tool mới và đăng ký trong `tools/__init__.py`), `tests/test_tools_todo.py`, code UI và `requirements.txt`. Không sửa nội dung case trong `data/eval_base.json`.

Chi tiết từng bước xem [README.md](../README.md) ở root; cấu hình API key xem [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md).

## Giao diện hội thoại

Từ thư mục `starter_v0/`, cài môi trường và chạy UI:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Mở http://127.0.0.1:8501 để dùng trên máy chạy app.

### Chia sẻ UI cho người ngoài bằng Cloudflare Quick Tunnel

Đã tạo link public tạm thời: [https://revelation-preventing-roots-blink.trycloudflare.com](https://revelation-preventing-roots-blink.trycloudflare.com). Trang chính và health endpoint đã trả HTTP 200 lúc 10:20:40 ngày 11/11/2026 (GMT+7); xem [bằng chứng](../report/team/evidence/ui_public_check.json).

Giữ UI chạy, mở terminal khác tại thư mục chứa cloudflared và chạy:

```powershell
.\cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:8501
```

Dùng URL trycloudflare.com được in ra terminal để chia sẻ. Link trên thuộc phiên tunnel đã kiểm tra, không phải địa chỉ cố định: tắt máy, mất mạng hoặc dừng UI/tunnel thì không truy cập được; tạo tunnel mới có thể đổi URL. Khi đổi link, cập nhật A1 của báo cáo nhóm và thông báo cho người dùng thử.

Theo yêu cầu của người dùng, sử dụng tunnel cho demo, **bỏ qua deploy hosting**. Không đặt yêu cầu link tiếp tục chạy khi tắt máy. Kiểm tra HTTP public không thay thế việc người ngoài mở trình duyệt và gửi thử câu hỏi; bước thử chat từ máy/mạng khác chưa có bằng chứng riêng.


UI mặc định dùng OpenAI với `gpt-4o-mini`; điền `OPENAI_API_KEY` trong `.env` cục bộ hoặc cấu hình qua môi trường. Muốn chọn OpenRouter cho phiên mới, cấu hình `OPENROUTER_API_KEY` và dùng model `openai/gpt-4o-mini`. Các tool đọc tin dùng key tương ứng trong [hướng dẫn](../docs/TOOL-SETUP.md). Không nhập hoặc hiển thị key trên UI.

Nhập yêu cầu tại ô hội thoại. Khi agent hỏi thông tin hoặc xác nhận, trả lời trong cùng phiên để giữ ngữ cảnh. Mở phần hoạt động để xem lời gọi và kết quả tool; nút tạo phiên mới tách lịch sử. Transcript tự lưu sau mỗi lượt vào `transcripts/` và có thể tải từ thanh bên.

**Chế độ demo:** UI không gửi Telegram thật, kể cả khi model gọi send với confirmed=true; chỉ tạo bản xem trước. Lớp chặn chỉ áp dụng cho UI, không sửa code tool hoặc hành vi gửi của CLI chat.py. Không coi bản xem trước là bằng chứng bonus gửi Telegram thật.

**Kiểm thử ngoại tuyến:**

```powershell
python -m pytest -q -p no:cacheprovider --junitxml=../report/team/evidence/pytest_with_ui.xml
```

**Ba kịch bản UI gọi API thật:**

```powershell
python scripts/demo_ui.py
```

Kịch bản gồm nghiên cứu web, thiếu tài khoản rồi bổ sung và xin xác nhận trước khi gửi. Có thể phát sinh chi phí API. Chạy bằng Streamlit AppTest, không giả lập câu trả lời model; danh sách transcript ghi tại `report/team/evidence/ui_live_demo.json` tính từ gốc repo. Transcript lỗi phải giữ và phân biệt với phiên thành công, không tự sửa metric hoặc giả lập kết quả.

Không commit `.env` hoặc `.venv`. Thao tác commit, push, đổi tên repo từ xa và nộp LMS không nằm trong lệnh chạy UI; người dùng tự thực hiện khi chốt bài.
