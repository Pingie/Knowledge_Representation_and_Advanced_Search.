"""Dữ liệu VÍ DỤ TRÊN LỚP, không phải dữ liệu bài nộp."""
GRAPH = {
    "S": [("A", 2), ("B", 1), ("G", 10)],
    "A": [("C", 2)],
    "B": [("C", 5), ("D", 2)],
    "C": [("G", 2)],
    "D": [("C", 1), ("G", 6)],
    "G": [], "X": []
}
H = {"S": 4, "A": 3, "B": 4, "C": 2, "D": 3, "G": 0, "X": 0}
# Đây là ví dụ bổ sung: h chấp nhận được nhưng không nhất quán.
REOPEN_GRAPH = {"S": [("A", 2), ("B", 1)], "A": [("C", 1)],
                "B": [("C", 4)], "C": [("G", 4)], "G": []}
REOPEN_H = {"S": 2, "A": 5, "B": 1, "C": 1, "G": 0}
MAZE = ["SwwwG", ".....", "..#.."]

FRONTIER_GRAPH = {"S": [("A", 1), ("B", 2)], "A": [("D", 2)],
                  "B": [("G", 3)], "D": [("G", 7)], "G": []}
FRONTIER_H = {"S": 4, "A": 1, "B": 2, "D": 6, "G": 0}
