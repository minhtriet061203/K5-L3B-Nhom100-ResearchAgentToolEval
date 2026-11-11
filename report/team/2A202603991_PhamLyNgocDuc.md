# Báo cáo cá nhân — Phạm Lý Ngọc Đức — 2A202603991

## 1. Thông tin thành viên

- Họ tên: Phạm Lý Ngọc Đức.
- MSSV: 2A202603991.
- Email / GitHub: [26ai.ducpln@vinuni.edu.vn](https://github.com/Ducbaynao)
- Nhánh làm việc: `2A202603991_PhamLyNgocDuc`.

## 2. Phần việc phụ trách

Bổ sung UI Streamlit còn thiếu trong repo nhóm, tích hợp hội thoại nhiều lượt và transcript, kiểm thử và cập nhật bằng chứng CP5. Chỉ ghi nhận phần UI/tích hợp ở đây, không nhận phần baseline, 3 tool mới hoặc 10 eval case do các thành viên khác đã làm.

## 3. Đóng góp cụ thể

- Tái sử dụng UI từ phiên làm việc/repo cũ (commit local bdd183b), đưa app.py, test_ui_flow.py và demo_ui.py vào repo này; không khẳng định viết toàn bộ từ đầu.
- Thêm Streamlit vào requirements.txt. UI có chat nhiều lượt, xem hoạt động tool, cảnh báo lỗi, tạo phiên mới và tải transcript.
- Tích hợp với vòng model/tool hiện có trong chat.py qua tham số tool_executor tùy chọn. UI chỉ tạo bản xem trước khi model gọi send, không gửi Telegram thật; giữ hành vi CLI mặc định.
- Sửa log console thành ASCII để tránh UnicodeEncodeError trên Windows. Không sửa system_prompt.md, tools.yaml, code tool hoặc bộ eval có sẵn.
- Thiết lập môi trường cục bộ được Git bỏ qua; kiểm tra toàn repo đạt 115 passed, 0 failed, 0 skipped (109 test có sẵn + 6 test UI).
- Thu 3 phiên UI / 7 lượt bằng OpenAI gpt-4o-mini qua Streamlit AppTest, cập nhật A1/B4/B5a. Đây là kiểm thử tự động với API thật, không phải gõ tay trên trình duyệt.


### Kết quả kiểm thử thủ công bổ sung

Người dùng cung cấp 3 transcript tải từ UI, tổng 7 lượt; [biên bản đối chiếu](evidence/ui_manual_verification.json). Đã đối chiếu nội dung JSON với bản tự lưu trong repo: trùng dữ liệu. Các bước tìm web, hỏi tài khoản rồi lấy 2 bài NASA, từ chối/chấp thuận gửi ở chế độ preview và tính khoảng cách 5 ngày đều thể hiện đúng thao tác tool mong đợi trong các lượt này. Phản hồi tìm web vẫn bằng tiếng Anh; không khẳng định mọi câu trả lời model đều đúng hoặc mọi lỗi ở demo trước đã hết.

- Phần chia sẻ UI: người dùng đã tạo Cloudflare Quick Tunnel; đã cập nhật link và bằng chứng HTTP public vào A1/B5a. Chọn tunnel phục vụ demo, bỏ qua hosting theo yêu cầu; không coi đây là deploy chạy độc lập khi máy tắt.

## 4. Bằng chứng

- [UI](../../starter_v0/app.py), [vòng tool](../../starter_v0/chat.py), [test UI](../../starter_v0/tests/test_ui_flow.py), [demo](../../starter_v0/scripts/demo_ui.py).
- [Pytest XML](evidence/pytest_with_ui.xml), [danh sách transcript](evidence/ui_live_demo.json), [HTTP](evidence/ui_http_check.json), [tổng hợp kiểm chứng](evidence/ui_verification.json).
- AI/công cụ: dùng Codex hỗ trợ tái sử dụng code, tích hợp, viết test, chạy kiểm tra và soạn báo cáo. Học viên cần đọc code/test và tự giải thích được luồng model → tool → hỏi lại → tiếp tục, cùng khác biệt giữa UI demo và gửi Telegram thật.

## 5. Hạn chế và tự đánh giá

- UI local: http://127.0.0.1:8501. Người dùng đã tạo [Quick Tunnel public tạm thời](https://revelation-preventing-roots-blink.trycloudflare.com); kiểm tra HTTP 200 và health ok ngày 11/11/2026 ([bằng chứng](evidence/ui_public_check.json)). Chưa xác nhận chat qua trình duyệt từ máy khác; link hết hiệu lực khi dừng tunnel/UI.
- Chưa kiểm tra hình ảnh bằng trình duyệt tự động; đã kiểm tra widget bằng AppTest và HTTP server.
- Demo cho thấy model gọi thêm social_search ở yêu cầu web, và gọi send ở lượt chỉ đồng ý chuẩn bị nhưng chưa cho phép gửi. UI chặn gửi thật và lưu đúng lời gọi; chưa coi các hành vi đó là đúng hoàn toàn.


