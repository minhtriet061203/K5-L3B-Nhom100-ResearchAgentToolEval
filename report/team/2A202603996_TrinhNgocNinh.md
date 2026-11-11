# Báo cáo cá nhân — TrinhNgocNinh-2A202603996

## 1. Thông tin thành viên

- Họ tên: Trịnh Ngọc Ninh
- MSSV: 2A202603996
- Email: 26ai.ninhtn@vinuni.edu.vn
- GitHub: ninhtrinhdev

## 2. Phần việc phụ trách

Thiết kế và cài đặt 3 tool mới cho agent: `text_stats`, `date_diff`, `dedupe`. Viết unit test cho các tool này và bổ sung các case vào `eval_group.json`.

## 3. Đóng góp cụ thể

- Thêm 3 tool mới `text_stats`, `date_diff`, `dedupe` trong `starter_v0/tools/<tên>/` (`tool.py` + `TOOL.md`), đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`.
- Viết unit test cho 3 tool trong `starter_v0/tests/test_tools_todo.py`.
- Bổ sung case vào `starter_v0/data/eval_group.json` và chạy eval.
- Giữ lại run base có 3 tool mới (`v3_B_base_openrouter_20261110T193958769896.json`), bỏ run nhóm không đủ case để không lẫn vào bằng chứng.

## 4. Bằng chứng

- File/commit/PR:
  - `2636ec9` — feat(tools): add text_stats, date_diff, dedupe tools with unit tests and group eval cases
  - `2d3ddf1` — chore(runs): keep base run with 3 new tools; drop partial 3-case group run
  - Lưu ý: hai commit này có tác giả git là `w3schools-test <jw715855@gmail.com>` (cấu hình git cục bộ của tôi), không phải tên GitHub `ninhtrinhdev`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code hỗ trợ viết code và tài liệu. Kết quả được kiểm tra bằng `pytest` (0 failed) và đọc lại `failures` trong run JSON.

## 5. Tự đánh giá

...
