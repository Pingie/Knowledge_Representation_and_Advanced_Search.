"""Ví dụ ngắn: sao chép BEFORE trước thao tác làm thay đổi cấu trúc."""
from collections import deque
from heapq import heappush, heappop

stack = ["B", "A"]
before = stack.copy()
popped = stack.pop()
print("STACK before:", before, "-> pop:", popped, "-> after:", stack)

queue = deque(["A", "B"])
before = list(queue)
popped = queue.popleft()
print("QUEUE before:", before, "-> pop:", popped, "-> after:", list(queue))

heap = []
for pair in [(4, "C"), (1, "B"), (1, "A")]:
    heappush(heap, pair)
before = sorted(heap)
popped = heappop(heap)
print("HEAP ordered before:", before, "-> pop:", popped, "-> after:", sorted(heap))
print("At equal priority, names decide: A before B.")
