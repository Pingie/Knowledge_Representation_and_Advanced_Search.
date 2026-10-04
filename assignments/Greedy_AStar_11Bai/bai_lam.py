"""SINH VIÊN HOÀN THÀNH 5 HÀM -- đây là KHUNG, không phải mã mẫu bị lỗi.

Có thể tham khảo cấu trúc demo, tự viết lại và bổ sung kiểm thử/giải thích.
Không import hàm tìm kiếm từ *_demo.py hay thư viện tìm đường có sẵn.
Được dùng helper common.py (validate, record, make_result, maze_graph...).
Giữ nguyên chữ ký và các trường kết quả trong đề.
"""
from collections import deque
from heapq import heappush, heappop
from math import inf
from common import validate, record, make_result


def dfs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
    validate(graph, start, goal)
    stack = [(start, None)]
    visited, parent = set(), {}
    order, trace = [], []
    expanded = skipped = 0
    peak = 1
    view = lambda: [f"{u}<-{p}" for u, p in reversed(stack)]
    record(trace, "INIT", start, [], view(), step=step)
    while stack:
        before = view()
        u, predecessor = stack.pop()
        if u in visited:
            skipped += 1
            record(trace, "SKIP", u, before, view(), "visited", step)
            continue
        visited.add(u)
        parent[u] = predecessor
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, view(), step=step)
            return make_result(graph, parent, goal, order, expanded, skipped,
                               0, peak, trace, True)
        for v, weight in reversed(graph[u]):
            if v not in visited:
                stack.append((v, u))
        expanded += 1
        peak = max(peak, len(stack))
        record(trace, "EXPAND", u, before, view(), step=step)
    record(trace, "FAIL", goal, [], [], step=step)
    return make_result(graph, parent, goal, order, expanded, skipped,
                       0, peak, trace, False)


def bfs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
    validate(graph, start, goal)
    queue = deque([start])
    discovered, parent = {start}, {start: None}
    order, trace = [], []
    expanded, peak = 0, 1
    record(trace, "INIT", start, [], list(queue), step=step)
    while queue:
        before = list(queue)
        u = queue.popleft()
        order.append(u)
        if u == goal:
            record(trace, "GOAL", u, before, list(queue), step=step)
            return make_result(graph, parent, goal, order, expanded, 0,
                               0, peak, trace, True)
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


def ucs(graph: dict, start: str, goal: str, step: bool = False) -> dict:
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


def greedy(graph: dict, start: str, goal: str, h: dict,
           step: bool = False) -> dict:
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


def astar(graph: dict, start: str, goal: str, h: dict,
          step: bool = False, reopen: bool = True) -> dict:
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
            if not reopen and v in closed:
                continue
            if new_g < best_g.get(v, inf):
                best_g[v] = new_g
                parent[v] = u
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
