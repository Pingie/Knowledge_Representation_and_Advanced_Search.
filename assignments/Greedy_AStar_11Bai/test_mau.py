"""Kiểm thử MÃ MẪU. Chạy ở thư mục gốc: python -m unittest -v test_mau
Không dùng test_mau để chấm bai_lam.py: nó kiểm thử các demo đã cho.
"""
import copy
import io
import random
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from math import inf
from common import maze_graph, path_cost
from run_demo import ALGORITHMS
from data_mau import GRAPH, H, REOPEN_GRAPH, REOPEN_H, MAZE
from astar_demo import astar
from ucs_demo import ucs
from dfs_demo import dfs
from bfs_demo import bfs
from greedy_demo import greedy


def oracle(graph, start, goal, unit=False):
    """Liệt kê đường đơn độc lập, không dùng một thuật toán trong demo."""
    costs = []
    def visit(u, used, cost):
        if u == goal:
            costs.append(cost)
            return
        for v, w in graph[u]:
            if v not in used:
                visit(v, used | {v}, cost + (1 if unit else w))
    visit(start, {start}, 0)
    return min(costs, default=inf)


class DemoTests(unittest.TestCase):
    def all_runs(self, graph, start, goal, h):
        for name, fn in ALGORITHMS.items():
            yield name, fn(graph, start, goal, h) if name in ("greedy", "astar") else fn(graph, start, goal)

    def test_examples(self):
        costs = {"dfs": 6, "bfs": 10, "ucs": 6, "greedy": 10, "astar": 6}
        for name, result in self.all_runs(GRAPH, "S", "G", H):
            self.assertEqual(result["cost"], costs[name])
            self.assertEqual(result["cost"], path_cost(GRAPH, result["path"]))
            self.assertEqual(result["expanded"], len(result["order"]) - 1)

    def test_start_is_goal(self):
        for name, r in self.all_runs(GRAPH, "G", "G", H):
            self.assertEqual((r["path"], r["cost"], r["expanded"]), (["G"], 0, 0))

    def test_unreachable(self):
        for name, r in self.all_runs(GRAPH, "S", "X", H):
            self.assertIsNone(r["path"])
            self.assertEqual(r["cost"], inf)
            self.assertEqual(r["expanded"], len(r["order"]))

    def test_cycle_and_self_loop(self):
        g = {"S": [("S", 1), ("A", 2)], "A": [("S", 1), ("G", 2)], "G": []}
        for name, r in self.all_runs(g, "S", "G", {"S": 1, "A": 1, "G": 0}):
            self.assertEqual(r["path"], ["S", "A", "G"])

    def test_dfs_duplicate_pending(self):
        g = {"S": [("A", 1), ("B", 1)], "A": [("B", 1)], "B": [], "X": []}
        r = dfs(g, "S", "X")
        self.assertEqual(r["order"], ["S", "A", "B"])
        self.assertEqual(r["skipped"], 1)

    def test_ucs_improves(self):
        g = {"S": [("A", 8), ("B", 1)], "A": [("G", 9)], "B": [("A", 1)], "G": []}
        r = ucs(g, "S", "G")
        self.assertEqual((r["path"], r["cost"], r["skipped"]), (["S", "B", "A", "G"], 11, 1))

    def test_not_goal_at_generation(self):
        g = {"S": [("G", 10), ("A", 1)], "A": [("G", 2)], "G": []}
        self.assertEqual(ucs(g, "S", "G")["cost"], 3)
        self.assertEqual(astar(g, "S", "G", {"S": 2, "A": 1, "G": 0})["cost"], 3)

    def test_equal_parent_kept(self):
        g = {"S": [("G", 3), ("A", 1)], "A": [("G", 2)], "G": []}
        h = {u: 0 for u in g}
        self.assertEqual(ucs(g, "S", "G")["path"], ["S", "G"])
        self.assertEqual(astar(g, "S", "G", h)["path"], ["S", "G"])

    def test_ties_use_names(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("G", 2)], "B": [("G", 2)], "G": []}
        h = {u: 0 for u in g}
        for name in ("ucs", "greedy", "astar"):
            fn = ALGORITHMS[name]
            r = fn(g, "S", "G", h) if name != "ucs" else fn(g, "S", "G")
            self.assertEqual(r["path"], ["S", "A", "G"])

    def test_zero_heuristic_not_bfs(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("C", 1)], "B": [("G", 1)], "C": [("G", 1)], "G": []}
        r1, r2 = bfs(g, "S", "G"), greedy(g, "S", "G", {u: 0 for u in g})
        self.assertNotEqual(r1["order"], r2["order"])

    def test_global_frontier(self):
        g = {"S": [("A", 1), ("B", 1)], "A": [("D", 1)], "B": [("G", 1)], "D": [("G", 5)], "G": []}
        h = {"S": 3, "A": 1, "B": 2, "D": 8, "G": 0}
        self.assertEqual(greedy(g, "S", "G", h)["order"], ["S", "A", "B", "G"])

    def test_reopening(self):
        yes = astar(REOPEN_GRAPH, "S", "G", REOPEN_H)
        no = astar(REOPEN_GRAPH, "S", "G", REOPEN_H, reopen=False)
        self.assertEqual((yes["cost"], yes["reopened"]), (7, 1))
        self.assertEqual(no["cost"], 9)
        self.assertEqual(yes["order"].count("C"), 2)

    def test_h_zero_matches_ucs(self):
        a = astar(GRAPH, "S", "G", {u: 0 for u in GRAPH})
        b = ucs(GRAPH, "S", "G")
        for key in ("path", "cost", "order", "expanded", "skipped", "max_frontier"):
            self.assertEqual(a[key], b[key])

    def test_invalid_weights(self):
        for w in [0, -1, inf, float("nan"), True, "3"]:
            with self.subTest(w=w):
                g = {"S": [("G", w)], "G": []}
                with self.assertRaises(ValueError):
                    ucs(g, "S", "G")

    def test_invalid_graph(self):
        bad = [{}, {"S": [("MISSING", 1)], "G": []},
               {"S": [("G", 1), ("G", 2)], "G": []}, {"S": set(), "G": []}]
        for g in bad:
            with self.assertRaises(ValueError):
                dfs(g, "S", "G")
        with self.assertRaises(ValueError):
            bfs(GRAPH, "NO", "G")

    def test_invalid_h(self):
        for h in [{}, {**H, "G": 1}, {**H, "A": -1}, {**H, "A": inf}, {**H, "A": float("nan")}]:
            with self.assertRaises(ValueError):
                astar(GRAPH, "S", "G", h)

    def test_does_not_mutate_inputs(self):
        g, h = copy.deepcopy(GRAPH), H.copy()
        list(self.all_runs(g, "S", "G", h))
        self.assertEqual(g, GRAPH)
        self.assertEqual(h, H)

    def test_maze_validations(self):
        for rows in [[], ["S", "..G"], ["S?G"], ["..."], ["SSG"]]:
            with self.assertRaises(ValueError):
                maze_graph(rows)
        with self.assertRaises(ValueError):
            maze_graph(["SG"], water_cost=0)

    def test_water(self):
        g, s, z, h = maze_graph(MAZE)
        self.assertEqual(astar(g, s, z, h)["cost"], 6)
        self.assertEqual(greedy(g, s, z, h)["cost"], 16)
        self.assertTrue(all(h[u] <= w + h[v] for u in g for v, w in g[u]))

    def test_live_step_and_snapshot(self):
        with patch("builtins.input", return_value="") as pause, redirect_stdout(io.StringIO()):
            r = dfs(GRAPH, "S", "G", step=True)
        self.assertEqual(pause.call_count, r["expanded"] + r["skipped"] + 1)
        first = r["trace"][1]
        self.assertEqual(first["before"], ["S<-None"])
        self.assertEqual(first["after"], ["A<-S", "B<-S", "G<-S"])
        self.assertEqual(r["trace"][2]["before"][0], "A<-S")

    def test_cli(self):
        root = Path(__file__).resolve().parent
        p = subprocess.run([sys.executable, str(root / "run_demo.py"), "--algo", "astar", "--step"],
                           input="\n" * 100, text=True, capture_output=True, cwd=root.parent, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("COST: 6", p.stdout)
        p2 = subprocess.run([sys.executable, str(root / "structures_demo.py")], text=True,
                            capture_output=True, cwd=root.parent, timeout=10)
        self.assertIn("STACK before: ['B', 'A'] -> pop: A -> after: ['B']", p2.stdout)

    def test_random_graph_oracle(self):
        rng = random.Random(20260923)
        names = ["S", "A", "B", "C", "G"]
        for trial in range(100):
            g = {u: [] for u in names}
            for u in names[:-1]:
                for v in names:
                    if v != u and (v == "G" or rng.random() < .35):
                        g[u].append((v, rng.randint(1, 9)))
                rng.shuffle(g[u])
            true_h = {u: oracle(g, u, "G") for u in g}
            admissible = {u: rng.randint(0, int(true_h[u])) for u in g}
            with self.subTest(trial=trial):
                optimum = oracle(g, "S", "G")
                self.assertEqual(ucs(g, "S", "G")["cost"], optimum)
                self.assertEqual(astar(g, "S", "G", admissible)["cost"], optimum)
                self.assertEqual(astar(g, "S", "G", true_h, reopen=False)["cost"], optimum)
                self.assertEqual(len(bfs(g, "S", "G")["path"]) - 1, oracle(g, "S", "G", unit=True))
                for name, r in self.all_runs(g, "S", "G", admissible):
                    self.assertEqual(r["cost"], path_cost(g, r["path"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
