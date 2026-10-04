"""Greedy best-first: chọn min h trên TOÀN BỘ heap, không phải hàng xóm hiện tại."""
from heapq import heappush, heappop
from common import validate, record, make_result


def greedy(graph: dict, start: str, goal: str, h: dict,
           step: bool = False) -> dict:
    # B1. Biến thể bài thực hành: đánh dấu khi thêm, giữ cha lần đầu.
    validate(graph, start, goal, h)
    heap = [(h[start], start)]
    discovered, parent = {start}, {start: None}
    order, trace = [], []
    expanded, peak = 0, 1
    view = lambda: [f"{u}(h={p})" for p, u in sorted(heap)]
    record(trace, "INIT", start, [], view(), step=step)
    while heap:
        before = view()
        priority, u = heappop(heap)
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, view(), step=step)
            return make_result(graph, parent, goal, order, expanded, 0,
                               0, peak, trace, True)
        # B2. Giữ các ứng viên cũ trong heap, thêm hàng xóm chưa phát hiện.
        for v, weight in graph[u]:
            if v not in discovered:
                discovered.add(v)
                parent[v] = u
                heappush(heap, (h[v], v))
        expanded += 1
        peak = max(peak, len(heap))
        record(trace, "EXPAND", u, before, view(), step=step)
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, 0,
                       0, peak, trace, False)


if __name__ == "__main__":
    from run_demo import run_named
    run_named("greedy")
