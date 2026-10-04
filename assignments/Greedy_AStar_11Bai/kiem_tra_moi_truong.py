"""Kiểm tra chỗ đang đứng và các tệp đi kèm; không cài thêm phần mềm."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
print("Python:", sys.version.split()[0])
print("Executable:", sys.executable)
print("Terminal cwd:", Path.cwd())
print("Project folder:", root)
for name in ["run_demo.py", "common.py", "data_mau.py", "dfs_demo.py",
             "bfs_demo.py", "ucs_demo.py", "greedy_demo.py", "astar_demo.py",
             "bai_lam.py", "chay_bai_lam.py", "test_bai_lam.py",
             "du_lieu_baitap.py"]:
    print("OK     " if (root / name).is_file() else "MISSING", name)
if sys.version_info < (3, 10):
    print("WARNING: can Python 3.10 tro len.")
if Path.cwd() != root:
    print("NOTE: Terminal khac thu muc goi. Chuyen vao project folder hoac go duong dan day du.")
print("Next: python run_demo.py --algo astar --step")
