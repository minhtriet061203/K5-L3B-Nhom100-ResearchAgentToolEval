# Báo cáo cá nhân — NguyenMinhTriet-2A202603995

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Triết
- MSSV: 2A202603995
- Email: 26ai.trietnm2@vinuni.edu.vn
- GitHub: `minhtriet061203`

## 2. Phần việc phụ trách

- **CP1 — Baseline v0:** chạy eval base (`eval_base.json`, 20 case) trên prompt/tools gốc của starter để có mốc so sánh.
- **CP2 — Vòng tối ưu v1–v3:** mỗi version chỉ sửa một artifact và kiểm một giả thuyết: v1, v2 sửa `system_prompt.md`, v3 sửa `tools.yaml`. Ghi từng vòng vào `version_log.csv`.
- **Báo cáo:** viết bảng B1 Version Evidence và B2 Failure Analysis trong `group_report.md`.
- Tạo repo nhóm, review và merge PR #1 (`feat/team-tools`).

## 3. Đóng góp cụ thể

1. **Baseline v0:** dùng OpenRouter `openai/gpt-4o-mini` với temperature 0. Kết quả: case_accuracy **0.65** (13/20), routing 0.75, args 0.65, multiturn 1.00, `provider_error_cases = 0`.
2. **Phân tích lỗi v0 (B2):** đọc `results[*].result.failures` trong run JSON và chia 7 case fail thành 2 nhóm nguyên nhân:
   - 5/7 lỗi (R08, R10, R11, R12, R14) do chỉ dẫn xấu cố ý trong prompt gốc: đoán account ("pick Sam Altman"), bịa URL ("assume a likely URL"), gửi không cần xác nhận, ép "pick one tool" nên câu ngoài phạm vi vẫn gọi `send`.
   - 2/7 lỗi (R03, R13) là `wrong_arg_value`: route đúng tool nhưng sai giá trị args (`query="AI news"` thay vì `"AI"`, thiếu `topic=news`) vì chưa có quy ước args. R03 hết lỗi từ v1 khi prompt được viết lại; R13 phải đến v3, khi `tools.yaml` có quy ước args, mới PASS.
3. **v1 — `system_prompt.md`:** bỏ 3 chỉ dẫn xấu. Thêm phạm vi (ngoài phạm vi thì không gọi tool), thêm rule "thiếu account/URL → `clarify`" và rule "trước `send` phải `clarify(yes_no)`". Kết quả **0.65 → 0.80**: sửa được R03, R08, R10, R11, R13, R14. Đổi lại, R01, R04, R05 bị regress vì model hỏi lại quá mức dù đã đủ thông tin.
4. **v2 — `system_prompt.md`:** thu hẹp rule hỏi lại theo đúng lỗi regress của v1:
   - Có tên người thì tự đổi sang handle; có URL thì gọi tool ngay.
   - Tool đọc không bao giờ cần xác nhận; chỉ `send` cần `yes_no`.
   - Chỉ `clarify(text)` khi thật sự không có account/URL trong hội thoại.
   - Cho phép gọi nhiều tool cùng lượt.

   Kết quả **0.80 → 0.95**, routing 1.00. R13 vẫn dao động vì thiếu `topic=news`.
5. **v3 — `tools.yaml`:** viết lại description của mọi tool theo khung *làm gì / KHI NÀO dùng / KHI NÀO KHÔNG dùng*. Thêm quy ước args:
   - `query` chỉ chứa chủ đề cốt lõi;
   - "tin tức" → `topic=news`, "hôm nay" → `timeframe=day`;
   - handle không có `@`;
   - "nổi bật" → `search_type=Top`.

   Đồng thời ghi rõ boundary xác nhận của `send` ngay trong tool. Kết quả giữ **0.95** và R13 PASS ổn định. Nhưng M06 bị regress (multiturn 1.00 → 0.83): user đã nói "bỏ Twitter" mà model vẫn gọi thừa `social_search`.
6. **Version log:** ghi 4 dòng v0–v3 vào `version_log.csv`, mỗi dòng có artifact hash (`prompt_hash`, `tools_hash`), lý do, giả thuyết, metric trước/sau và đường dẫn run file.

## 4. Bằng chứng

- File/commit/PR:
  - Commit `7cd8f4b` — "Baseline v0 + tối ưu v1-v3 (0.65 -> 0.95) + failure analysis B2"; merge PR #1.
  - Artifact: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv` (dòng v0–v3).
  - Run JSON (đều có `provider_error_cases = 0`, `measured_cases = total_cases = 20`):
    - `starter_v0/runs/v0_B_base_openrouter_20261110T175213197182.json` (0.65)
    - `starter_v0/runs/v1_B_base_openrouter_20261110T181644444661.json` (0.80)
    - `starter_v0/runs/v2_B_base_openrouter_20261110T182837689317.json` (0.95)
    - `starter_v0/runs/v3_B_base_openrouter_20261110T184559398755.json` (0.95)
  - Báo cáo: `report/team/group_report.md` bảng B1, B2.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng AI assistant để hỗ trợ đọc log failure và soạn câu chữ cho prompt/description, sau đó tự sửa lại cho khớp từng case lỗi.
  - Tự kiểm tra:
    - Mỗi version chỉ đổi một artifact và đối chiếu hash trong run JSON với `version_log.csv`.
    - Chỉ ghi run hợp lệ, tức `provider_error_cases == 0`.
    - Mọi số trong B1/B2 đọc trực tiếp từ `summary` và `results[*].result.failures` của run JSON.
    - Mỗi version đều ghi cả case regress, không chỉ ghi case được sửa.

## 5. Tự đánh giá

- **Làm tốt:** quy trình tối ưu có kỷ luật: một giả thuyết, một artifact, một run cho mỗi version, và mọi version đều truy được về run file. Phân tích B2 chỉ ra nguyên nhân gốc của từng nhóm lỗi, nên fix nhắm đúng chỗ. Regress của v1 (hỏi lại quá mức) được nhận ra và sửa ngay ở v2.
- **Hạn chế:**
  - v3 không tăng case_accuracy (0.95 → 0.95) và còn làm M06 regress (multiturn 0.83). Mình chưa làm thêm v4 để sửa lỗi này, ví dụ rule "tôn trọng yêu cầu bỏ nguồn của user ở lượt trước".
  - Mỗi version chỉ chạy 1 lần ở temperature 0 nên chưa đo được độ dao động giữa các lần chạy.
- **Bài học:**
  - Sửa prompt theo hướng "cấm" dễ gây tác dụng ngược: v1 làm model hỏi lại quá mức. Phải nói rõ cả khi nào **không** cần làm.
  - Lỗi về giá trị args được sửa hiệu quả hơn ở `tools.yaml` (quy ước gắn với từng tool) so với ở system prompt.