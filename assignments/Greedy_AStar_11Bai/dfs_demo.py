"""DFS: học theo B1--B5 trong Hướng dẫn. Chạy: python dfs_demo.py --step"""
from common import validate, record, make_result


def dfs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
    # B1. Ngăn xếp lưu (đỉnh, cha dự kiến); đỉnh ngăn xếp ở CUỐI list.
    validate(graph, start, goal)
    stack = [(start, None)]
    visited, parent, order, trace = set(), {}, [], []
    expanded = skipped = 0
    peak = 1
    view = lambda: [f"{u}<-{p}" for u, p in reversed(stack)]
    record(trace, "INIT", start, [], view(), step=step)
    while stack:
        # B2. Chụp trước khi pop; không truyền stack và stack.pop vào print.
        before = view()
        u, predecessor = stack.pop()
        if u in visited:
            skipped += 1
            record(trace, "SKIP", u, before, view(), "visited", step)
            continue
        # B3. Chỉ bản ghi hợp lệ đầu tiên chốt cha và đánh dấu đã thăm.
        visited.add(u)
        parent[u] = predecessor
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, view(), step=step)
            return make_result(graph, parent, goal, order, expanded, skipped,
                               0, peak, trace, True)
        # B4. Đẩy đảo thứ tự để hàng xóm đầu tiên được lấy trước.
        for v, weight in reversed(graph[u]):
            if v not in visited:
                stack.append((v, u))
        expanded += 1
        peak = max(peak, len(stack))
        record(trace, "EXPAND", u, before, view(), step=step)
    # B5. Biên rỗng: thất bại hữu hạn, không có đường đến goal.
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, skipped,
                       0, peak, trace, False)


if __name__ == "__main__":
    from run_demo import run_named
    run_named("dfs")
