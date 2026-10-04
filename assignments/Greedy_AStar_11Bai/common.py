"""Hàm phụ trợ; chỉ dùng thư viện chuẩn. Python 3.10+.

trace: ảnh chụp TRƯỚC và SAU mỗi vòng lặp, phần tử lấy tiếp ở bên trái.
step=True: dừng ngay TRONG thuật toán sau mỗi sự kiện, không phát lại kết quả.
"""
from math import inf, isfinite


def validate(graph: dict, start: str, goal: str, h=None) -> None:
    if not isinstance(graph, dict) or not graph:
        raise ValueError("graph phai la dict khong rong")
    if any(not isinstance(u, str) or not u for u in graph):
        raise ValueError("ten dinh phai la chuoi khong rong")
    if start not in graph or goal not in graph:
        raise ValueError("start/goal phai co trong graph")
    for u, edges in graph.items():
        if not isinstance(edges, (list, tuple)):
            raise ValueError("danh sach ke phai co thu tu")
        seen = set()
        for edge in edges:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise ValueError("canh phai co dang (v, w)")
            v, w = edge
            if not isinstance(v, str) or v not in graph or v in seen:
                raise ValueError("dinh ke thieu khoa hoac canh song song")
            if type(w) not in (int, float) or not isfinite(w) or w <= 0:
                raise ValueError("trong so phai huu han va duong")
            seen.add(v)
    if h is not None:
        if not isinstance(h, dict) or set(h) != set(graph):
            raise ValueError("h phai co dung tap dinh cua graph")
        if any(type(x) not in (int, float) or not isfinite(x) or x < 0
               for x in h.values()):
            raise ValueError("h phai huu han, khong am")
        if h[goal] != 0:
            raise ValueError("h(goal) phai bang 0")


def restore_path(parent: dict, goal: str) -> list:
    path, current = [], goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def path_cost(graph: dict, path) -> float:
    if path is None:
        return inf
    total = 0
    for u, v in zip(path, path[1:]):
        costs = [w for neighbor, w in graph[u] if neighbor == v]
        if len(costs) != 1:
            raise ValueError("duong tra ve chua canh khong hop le")
        total += costs[0]
    return total


def record(trace: list, event: str, node: str, before: list,
           after: list, note: str = "", step: bool = False) -> None:
    # Các phần tử là chuỗi bất biến; copy giữ độc lập hai ảnh chụp.
    row = {"event": event, "node": node, "before": before.copy(),
           "after": after.copy(), "note": note}
    trace.append(row)
    if step:
        print_row(len(trace) - 1, row)
        if event not in ("GOAL", "FAIL"):
            input("Enter: xu ly tiep | Ctrl+C: dung > ")


def print_row(index: int, row: dict) -> None:
    print(f"\n[{index:02d}] {row['event']} {row['node']} {row['note']}")
    print("  BEFORE (next at left):", row["before"])
    print("  AFTER  (next at left):", row["after"])


def make_result(graph, parent, goal, order, expanded, skipped, reopened,
                peak, trace, found):
    path = restore_path(parent, goal) if found else None
    return {"path": path, "cost": path_cost(graph, path), "order": order,
            "expanded": expanded, "skipped": skipped, "reopened": reopened,
            "max_frontier": peak, "trace": trace}


def show_result(result: dict, include_trace=True):
    if include_trace:
        for i, row in enumerate(result["trace"]):
            print_row(i, row)
    print("\nPATH:", result["path"])
    print("COST:", result["cost"])
    print("ORDER:", result["order"])
    print("EDGES:", None if result["path"] is None else len(result["path"]) - 1)
    for key in ("expanded", "skipped", "reopened", "max_frontier"):
        print(key.upper() + ":", result[key])


def maze_graph(rows: list, water_cost: int = 5):
    """R,D,L,U; phí một cạnh = phí ĐI VÀO ô đích của cạnh đó.

    Tên ô 'r,c' là chuỗi. S/G/. có phí vào 1, w có phí water_cost.
    Thứ tự tên khi heap đồng hạng là từ điển chuỗi, không thứ tự số.
    """
    if type(water_cost) is not int or water_cost < 1:
        raise ValueError("water_cost phai la so nguyen >= 1")
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ValueError("me cung rong")
    if any(not isinstance(row, str) or not row for row in rows):
        raise ValueError("hang phai la chuoi khong rong")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("me cung phai hinh chu nhat")
    if any(c not in "SG.#w" for row in rows for c in row):
        raise ValueError("ky tu me cung khong hop le")
    if sum(row.count("S") for row in rows) != 1 or sum(row.count("G") for row in rows) != 1:
        raise ValueError("can dung mot S va mot G")
    graph, positions = {}, {}
    start = goal = None
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            if value == "#":
                continue
            u = f"{r},{c}"
            graph[u], positions[u] = [], (r, c)
            if value == "S":
                start = u
            if value == "G":
                goal = u
    for u, (r, c) in positions.items():
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            rr, cc = r + dr, c + dc
            v = f"{rr},{cc}"
            if v in graph:
                weight = water_cost if rows[rr][cc] == "w" else 1
                graph[u].append((v, weight))
    gr, gc = positions[goal]
    h = {u: abs(r - gr) + abs(c - gc) for u, (r, c) in positions.items()}
    return graph, start, goal, h


def draw_maze(rows: list, path) -> str:
    board = [list(row) for row in rows]
    if path is not None:
        for u in path:
            r, c = map(int, u.split(","))
            if board[r][c] not in "SG#":
                board[r][c] = "*"
    return "\n".join("".join(row) for row in board)
