"""BFS: số cạnh ít nhất. Chạy: python bfs_demo.py --step"""
from collections import deque
from common import validate, record, make_result


def bfs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
    # B1. FIFO: thêm cuối, lấy đầu. Đánh dấu ngay khi đưa vào biên.
    validate(graph, start, goal)
    queue = deque([start])
    discovered, parent = {start}, {start: None}
    order, trace = [], []
    expanded, peak = 0, 1
    record(trace, "INIT", start, [], list(queue), step=step)
    while queue:
        # B2. Bản sao before không thay đổi khi hàng đợi bị thay đổi.
        before = list(queue)
        u = queue.popleft()
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, list(queue), step=step)
            return make_result(graph, parent, goal, order, expanded, 0,
                               0, peak, trace, True)
        # B3. Một đỉnh chỉ được đưa vào hàng đợi một lần.
        for v, weight in graph[u]:
            if v not in discovered:
                discovered.add(v)
                parent[v] = u
                queue.append(v)
        expanded += 1
        peak = max(peak, len(queue))
        record(trace, "EXPAND", u, before, list(queue), step=step)
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, 0,
                       0, peak, trace, False)


if __name__ == "__main__":
    from run_demo import run_named
    run_named("bfs")
