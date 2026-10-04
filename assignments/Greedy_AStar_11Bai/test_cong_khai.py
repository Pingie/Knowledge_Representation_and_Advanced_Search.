"""Kiểm thử nhỏ cho bài làm. Chưa thay thế các kiểm thử sinh viên phải tự viết.
Ví dụ: python -m unittest -v test_cong_khai.PublicTests.test_dfs
"""
import unittest
import bai_lam as s


class PublicTests(unittest.TestCase):
    def setUp(self):
        self.graph = {"S": [("A", 1)], "A": [("G", 1)], "G": [], "X": []}
        self.h = {"S": 2, "A": 1, "G": 0, "X": 0}

    def check(self, r):
        self.assertEqual(r["path"], ["S", "A", "G"])
        self.assertEqual(r["cost"], 2)
        self.assertEqual(r["order"], ["S", "A", "G"])
        self.assertEqual(r["expanded"], 2)

    def test_dfs(self):
        self.check(s.dfs(self.graph, "S", "G"))

    def test_bfs(self):
        self.check(s.bfs(self.graph, "S", "G"))

    def test_ucs(self):
        self.check(s.ucs(self.graph, "S", "G"))

    def test_greedy(self):
        self.check(s.greedy(self.graph, "S", "G", self.h))

    def test_astar(self):
        self.check(s.astar(self.graph, "S", "G", self.h))


if __name__ == "__main__":
    unittest.main(verbosity=2)
