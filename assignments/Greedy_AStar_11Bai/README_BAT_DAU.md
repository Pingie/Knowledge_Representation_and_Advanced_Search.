# Greedy, A* và thực hành năm thuật toán tìm kiếm
**Nguyễn Bích Vân|Biểu diễn tri thức và tìm kiếm nâng cao— IAI–UET–VNU**

## 1. Mở tài liệu nào?

- `hw2-student.pdf`: 6 bài tính tay (4 trung bình, 2 khó) và 5 bài Python, tổng 100 điểm.
- `HuongDan_CaiDat_Python.pdf/.tex`: hướng dẫn từng bước; có mã đầy đủ và đáp án VÍ DỤ HỌC TRÊN LỚP, không phải bộ đáp án bài nộp.



## 2. Chạy mẫu trên VS Code (Windows)

1. Giải nén TOÀN BỘ; không mở Python trong cửa sổ ZIP.
2. File → Open Folder → chọn **Greedy_AStar_11Bai**, nơi nhìn thấy trực tiếp `run_demo.py`.
3. Ctrl+Shift+P → Python: Select Interpreter → chọn Python 3.10+ có sẵn (Anaconda cũng được).
4. Terminal → New Terminal. Gõ từng dòng, không dán tất cả khi chương trình đang chờ Enter:

```powershell
python kiem_tra_moi_truong.py
python structures_demo.py
python run_demo.py --algo dfs --step
```

**Không gõ `cd python`: gói mới này để các tệp chạy chính ở thư mục gốc.**

Thay `dfs` bằng `bfs`, `ucs`, `greedy`, `astar`. Hoặc chạy trực tiếp:

```powershell
python astar_demo.py --step
python run_demo.py --algo greedy --case frontier --step
python run_demo.py --algo astar --case reopen --step
python run_demo.py --algo astar --case reopen --no-reopen
python run_demo.py --algo astar --case maze --summary
python -m unittest -v test_mau
```

Trong `--step`, nhấn Enter ở **Terminal** để xử lý tiếp. Mã dừng TRONG thuật toán sau INIT hoặc một vòng xử lý; không phát lại kết quả tính sẵn. `before` chụp trước pop; `after` chụp sau xử lý toàn bộ bước đó. Dùng Ctrl+C để dừng. Chỉ dùng `--step` hoặc `--summary`, không dùng đồng thời.

Muốn xem từng DÒNG mã: mở Run and Debug, chọn “File dang mo - dung breakpoint va F10”, đặt breakpoint tại `popped = stack.pop()` trong `structures_demo.py`, rồi F5/F10. `.vscode/launch.json` dùng Terminal tích hợp để nhập được Enter. Cấu hình này cần tiện ích Python/Python Debugger của Microsoft.

`common.py` và `data_mau.py` phải đi cùng các tệp demo. Không tải mỗi `astar_demo.py` rồi bỏ các tệp còn lại.

### Nếu không tìm thấy tệp

Gõ `dir` trong PowerShell: phải thấy `run_demo.py`. Nếu không thấy, mở lại đúng thư mục hoặc dùng `cd "đường dẫn tới Greedy_AStar_11Bai"`. Nếu hiện `>>>`, gõ `exit()` trước; đó là Python REPL, không phải Terminal shell.

Kiểm tra interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```



Sinh viên dùng đúng đường dẫn Python trên máy mình. Nếu `python` chưa có trong PATH nhưng máy có Python Launcher, có thể thay bằng `py -3`. Bộ mã không yêu cầu `pip install`.

## 3. Làm năm bài Python

Sửa  file **`bai_lam.py`**: năm hàm còn `NotImplementedError` là phần CỐ Ý CHƯA VIẾT để sinh viên làm. Đây không phải lỗi demo.

- Bài 7: `dfs`
- Bài 8: `bfs`
- Bài 9: `ucs`
- Bài 10: `greedy`
- Bài 11: `astar`

Được dùng các helper trong `common.py`; không import hàm tìm kiếm demo làm thay bài nộp. Giữ chữ ký và trường kết quả; không sửa dữ liệu đầu vào. Dữ liệu nộp nằm trong `du_lieu_baitap.py`, khác dữ liệu mẫu.

Chạy một bài ngay khi làm xong, không cần đợi đủ năm hàm:

```powershell
python -m unittest -v test_cong_khai.PublicTests.test_dfs
python chay_bai_lam.py --bai 7
```

Đổi số bài 7–11; runner lưu `output/bai7.json`, `output/bai7_trace.csv`... ngay cạnh chương trình. Runner chỉ chạy dữ liệu CHÍNH; sinh viên tự thêm các biến thể và ca biên theo đề.

Tạo thêm `test_bai_lam.py` với `import bai_lam`, rồi chạy:

```powershell
python -m unittest -v test_bai_lam
```

`test_mau` kiểm chương trình mẫu, KHÔNG kiểm bài của sinh viên. Không dùng kết quả “test_mau OK” làm bằng chứng bài nộp đã đúng.

## 4. Quy ước dễ nhầm

- DFS: stack có `(node, parent)`; đánh dấu/chốt cha khi pop hợp lệ; push hàng xóm đảo thứ tự.
- BFS: đánh dấu khi enqueue; FIFO với deque; cha lần đầu.
- UCS: `(g,node)`; cải thiện strict `<`; giữ cha khi giá bằng; bỏ phiếu cũ trước order/goal.
- Greedy: `(h,node)`, chọn trên TOÀN BỘ heap; bản này đánh dấu khi thêm; không dùng g để ưu tiên.
- A*: `(f,node,g)`; f=g+h; mở lại đỉnh khi g rẻ hơn nếu `reopen=True`. Nếu không mở lại, bỏ ứng viên vào closed trước mọi cập nhật.
- `order` gồm đích nhưng không gồm phiếu cũ bị bỏ; không phải đường lời giải. `expanded` không tính đích, nhưng tính mỗi lần mở rộng lại.
- `max_frontier` đếm BẢN GHI THỰC, gồm phiếu cũ đang chờ; không là toàn bộ bộ nhớ.
- Mọi trọng số hữu hạn dương. h hữu hạn không âm và h(goal)=0. Bộ validate chỉ kiểm kiểu/miền giá trị; không chứng minh h chấp nhận được.
- Mê cung dùng chi phí ĐI VÀO ô; không thu phí ô xuất phát. h phải gắn với goal hiện tại.
- Snapshot DFS được in đảo so với raw list để phần tử lấy tiếp ở trái. Heap dùng sorted bản xem; không thay cơ chế heap.
- Trace chỉ để học và gỡ lỗi; đừng dùng thời gian có in/sắp trace như benchmark thuật toán.

## 5. Đóng gói bài nộp

`MSSV_HoTen_Search.zip`: phần viết tay 1–6, `bai_lam.py`, helper và dữ liệu cần thiết, `test_bai_lam.py`, JSON/CSV, báo cáo nhận xét cho phần Python, README cách chạy. Có thể dùng `MAU_BAO_CAO.md` làm khung.

Không đưa vào bài nộp:  môi trường ảo, ảnh kết quả không có mã. Chạy thử sau khi giải nén tại thư mục mới. Sinh viên cần tự giải thích mã và thực hiện một thay đổi nhỏ trên lớp theo hướng dẫn giảng viên.


