"""A*: f=g+h, có thể mở lại trạng thái khi g tốt hơn.

reopen=True: phần cài đặt bổ sung cho heuristic chấp nhận được nhưng không nhất quán.
reopen=False: đóng một lần; chỉ có bảo đảm tối ưu khi h nhất quán.
"""
from heapq import heappush, heappop
from math import inf
from common import validate, record, make_result


def astar(graph: dict, start: str, goal: str, h: dict,
          step: bool = False, reopen: bool = True) -> dict:
    # B1. Tuple (f, tên đỉnh, g): cùng f thì theo tên; g dùng nhận phiếu cũ.
    validate(graph, start, goal, h)
    heap = [(h[start], start, 0)]
    best_g, parent = {start: 0}, {start: None}
    closed, order, trace = set(), [], []
    expanded = skipped = reopened = 0
    peak = 1
    view = lambda: [f"{u}(g={g},f={f})" for f, u, g in sorted(heap)]
    record(trace, "INIT", start, [], view(), step=step)
    while heap:
        before = view()
        f, u, g = heappop(heap)
        # B2. Chỉ xử lý bản ghi mang chi phí tốt nhất đang biết.
        if g != best_g[u] or u in closed:
            skipped += 1
            record(trace, "SKIP", u, before, view(), "old/closed", step)
            continue
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, view(), f"g={g}", step)
            return make_result(graph, parent, goal, order, expanded, skipped,
                               reopened, peak, trace, True)
        closed.add(u)
        changes = []
        for v, weight in graph[u]:
            new_g = g + weight
            # B3. Bản đóng-một-lần bỏ luôn ứng viên vào đỉnh đã đóng.
            if not reopen and v in closed:
                continue
            if new_g < best_g.get(v, inf):
                best_g[v] = new_g
                parent[v] = u
                # B4. Mở lại: loại v khỏi closed trước khi đưa bản mới vào heap.
                if v in closed:
                    closed.remove(v)
                    reopened += 1
                    changes.append(f"REOPEN {v}")
                heappush(heap, (new_g + h[v], v, new_g))
                changes.append(f"{v}:g={new_g},f={new_g+h[v]},parent={u}")
        expanded += 1
        peak = max(peak, len(heap))
        record(trace, "EXPAND", u, before, view(), "; ".join(changes), step)
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, skipped,
                       reopened, peak, trace, False)


if __name__ == "__main__":
    from run_demo import run_named
    run_named("astar")
