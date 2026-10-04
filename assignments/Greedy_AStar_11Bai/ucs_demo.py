"""UCS: ưu tiên g, không dừng ngay khi sinh đích."""
from heapq import heappush, heappop
from math import inf
from common import validate, record, make_result


def ucs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
    # B1. Chi phí cùng tên đỉnh quyết định thứ tự, không phải thứ tự thêm.
    validate(graph, start, goal)
    heap = [(0, start)]
    best_g, parent = {start: 0}, {start: None}
    order, trace = [], []
    expanded = skipped = 0
    peak = 1
    view = lambda: [f"{u}(g={g})" for g, u in sorted(heap)]
    record(trace, "INIT", start, [], view(), step=step)
    while heap:
        before = view()
        g, u = heappop(heap)
        # B2. Phiếu cũ phải bị loại TRƯỚC order và TRƯỚC kiểm tra đích.
        if g != best_g[u]:
            skipped += 1
            record(trace, "SKIP", u, before, view(), f"old g={g}", step)
            continue
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, view(), f"g={g}", step)
            return make_result(graph, parent, goal, order, expanded, skipped,
                               0, peak, trace, True)
        changes = []
        # B3. Cải thiện chi phí: cập nhật CẢ best_g lẫn parent.
        for v, weight in graph[u]:
            new_g = g + weight
            if new_g < best_g.get(v, inf):
                best_g[v] = new_g
                parent[v] = u
                heappush(heap, (new_g, v))
                changes.append(f"{v}:g={new_g},parent={u}")
        expanded += 1
        peak = max(peak, len(heap))
        record(trace, "EXPAND", u, before, view(), "; ".join(changes), step)
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, skipped,
                       0, peak, trace, False)


if __name__ == "__main__":
    from run_demo import run_named
    run_named("ucs")
