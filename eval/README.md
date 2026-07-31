# VLearn Golden Eval

Bộ eval gồm đúng **25 case**:

| Nhóm | Số case | Kỳ vọng |
|---|---:|---|
| Ngoài phạm vi học tập | 6 | Block với code `scope` |
| Prompt injection | 4 | Block với code `prompt_injection` |
| Quyền riêng tư | 3 | Block với code `privacy` |
| Nội dung nguy hiểm | 4 | Block với code `unsafe` |
| Câu hỏi mơ hồ | 5 | Hỏi lại với code `ambiguous` |
| Câu học tập hợp lệ | 3 | Cho phép xử lý |

## Chạy offline

Không gọi backend, embedding hoặc model. Chế độ này chấm routing guardrail và
phát hiện câu mơ hồ:

```powershell
.\.venv\Scripts\python.exe eval\run_eval.py
```

## Chạy live

Khởi động backend trước, sau đó chạy:

```powershell
.\.venv\Scripts\python.exe eval\run_eval.py --mode live
```

Live eval gọi API thật. Các case hợp lệ có thể gọi OpenAI và phát sinh chi phí;
runner còn kiểm tra số citation tối thiểu.

## Kết quả

Mỗi lượt chạy ghi hai báo cáo:

- `eval/results/latest.json`: dữ liệu đầy đủ để xử lý tiếp.
- `eval/results/latest.md`: bảng đọc nhanh và breakdown theo nhóm.

Runner trả exit code `1` nếu có ít nhất một case fail, nên có thể dùng trong CI.
