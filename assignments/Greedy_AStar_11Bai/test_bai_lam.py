"""Kiểm thử BÀI LÀM: import bai_lam, KHÔNG import *_demo.
Chạy ở thư mục gốc: python -m unittest -v test_bai_lam
"""
import copy
import io
import json
import random
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from math import inf
from pathlib import Path
from unittest.mock import patch

import bai_lam as s
from common import maze_graph, path_cost
from du_lieu_baitap import (DFS_GRAPH, BFS_MAZE, BFS_BLOCKED, UCS_GRAPH,
                            GREEDY_GRAPH, GREEDY_H, GREEDY_H2, WATER_MAZE,
                            REOPEN_GRAPH, REOPEN_H)

ROOT = Path(__file__).resolve().parent


def oracle(graph, start, goal, unit=False):
    best = [inf]

    def visit(u, used, cost):
        if u == goal:
            best[0] = min(best[0], cost)
            return
        for v, w in graph[u]:
            if v not in used:
                visit(v, used | {v}, cost + (1 if unit else w))
    visit(start, {start}, 0)
    return best[0]


class DfsTests(unittest.TestCase):
    def test_main_data(self):
        r = s.dfs(DFS_GRAPH, "S", "G")
        self.assertEqual(r["path"], ["S", "A", "C", "E", "B", "D", "G"])
        self.assertEqual(r["cost"], 6)
        self.assertEqual(r["order"], ["S", "A", "C", "E", "B", "D", "G"])
        self.assertEqual(r["expanded"], 6)
        self.assertEqual(r["skipped"], 0)
        self.assertEqual(r["max_frontier"], 4)

    def test_swap_first_branch_on_copy(self):
        original = copy.deepcopy(DFS_GRAPH)
        graph = copy.deepcopy(DFS_GRAPH)
        graph["S"].reverse()
        r = s.dfs(graph, "S", "G")
        self.assertEqual(r["path"], ["S", "B", "D", "G"])
        self.assertEqual(r["cost"], 3)
        self.assertEqual(r["order"], ["S", "B", "D", "G"])
        self.assertEqual(r["expanded"], 3)
        self.assertEqual(graph["S"], [("B", 1), ("A", 1)])
        self.assertEqual(DFS_GRAPH, original)

    def test_unreachable_ends_with_fail(self):
        r = s.dfs(DFS_GRAPH, "S", "X")
        self.assertIsNone(r["path"])
        self.assertEqual(r["cost"], inf)
        self.assertEqual(r["expanded"], len(r["order"]))
        self.assertEqual(r["trace"][-1]["event"], "FAIL")

    def test_start_is_goal(self):
        r = s.dfs(DFS_GRAPH, "S", "S")
        self.assertEqual((r["path"], r["cost"], r["expanded"]), (["S"], 0, 0))

    def test_cycle_and_self_loop(self):
        g = {"S": [("S", 1), ("A", 2)], "A": [("S", 1), ("G", 2)], "G": []}
        r = s.dfs(g, "S", "G")
        self.assertEqual(r["path"], ["S", "A", "G"])
        self.assertEqual(r["order"], ["S", "A", "G"])
        self.assertEqual(len(r["order"]), len(set(r["order"])))
        self.assertEqual(r["skipped"], 0)

    def test_duplicate_pending_recorded_as_skip(self):
        g = {"S": [("A", 1), ("B", 1)], "A": [("B", 1)], "B": [], "X": []}
        r = s.dfs(g, "S", "X")
        self.assertEqual(r["order"], ["S", "A", "B"])
        self.assertEqual(r["skipped"], 1)

    def test_invalid_graph(self):
        for bad in [{}, {"S": [("MISSING", 1)], "G": []},
                    {"S": [("G", 1), ("G", 2)], "G": []}, {"S": set(), "G": []}]:
            with self.assertRaises(ValueError):
                s.dfs(bad, "S", "G")
        with self.assertRaises(ValueError):
            s.dfs(DFS_GRAPH, "NO", "G")
        with self.assertRaises(ValueError):
            s.dfs(DFS_GRAPH, "S", "NO")

    def test_step_pauses_inside_algorithm(self):
        with patch("builtins.input", return_value="") as pause, \
                redirect_stdout(io.StringIO()):
            r = s.dfs(DFS_GRAPH, "S", "G", step=True)
        self.assertEqual(pause.call_count, r["expanded"] + r["skipped"] + 1)


class BfsTests(unittest.TestCase):
    def test_maze_path(self):
        graph, start, goal, _ = maze_graph(BFS_MAZE)
        r = s.bfs(graph, start, goal)
        self.assertEqual(r["path"], ["0,0", "0,1", "0,2", "1,2", "2,2",
                                     "3,2", "3,3", "3,4", "2,4", "1,4"])
        self.assertEqual(r["cost"], 9)
        self.assertEqual(len(r["path"]) - 1, 9)
        self.assertEqual(len(r["order"]), 17)
        self.assertEqual(r["expanded"], 16)
        self.assertEqual(r["skipped"], 0)
        self.assertEqual(r["max_frontier"], 3)

    def test_maze_blocked_has_no_path(self):
        graph, start, goal, _ = maze_graph(BFS_BLOCKED)
        r = s.bfs(graph, start, goal)
        self.assertIsNone(r["path"])
        self.assertEqual(r["cost"], inf)
        self.assertEqual(len(r["order"]), 11)
        self.assertEqual(r["expanded"], 11)

    def test_fewest_edges_against_oracle(self):
        graph, start, goal, _ = maze_graph(BFS_MAZE)
        r = s.bfs(graph, start, goal)
        self.assertEqual(len(r["path"]) - 1, oracle(graph, start, goal, unit=True))

    def test_start_is_goal(self):
        r = s.bfs(GREEDY_GRAPH, "G", "G")
        self.assertEqual((r["path"], r["cost"], r["expanded"]), (["G"], 0, 0))
        maze, start, _, _ = maze_graph(BFS_MAZE)
        r2 = s.bfs(maze, start, start)
        self.assertEqual((r2["path"], r2["cost"], r2["expanded"]),
                         ([start], 0, 0))

    def test_maze_validation(self):
        for rows in [[], ["S", "..G"], ["S?G"], ["..."], ["SSG"]]:
            with self.assertRaises(ValueError):
                maze_graph(rows)
        with self.assertRaises(ValueError):
            maze_graph(["SG"], water_cost=0)

    def test_equal_h_and_queue_differ_from_greedy(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("C", 1)], "B": [("G", 1)],
             "C": [("G", 1)], "G": []}
        r = s.bfs(g, "S", "G")
        g0 = {u: 0 for u in g}
        self.assertEqual(r["order"], ["S", "B", "A", "G"])
        self.assertNotEqual(r["order"], s.greedy(g, "S", "G", g0)["order"])

    def test_does_not_mutate_input(self):
        graph, start, goal, _ = maze_graph(BFS_MAZE)
        before = copy.deepcopy(graph)
        s.bfs(graph, start, goal)
        self.assertEqual(graph, before)


class UcsTests(unittest.TestCase):
    def test_main_data(self):
        r = s.ucs(UCS_GRAPH, "S", "G")
        self.assertEqual(r["path"], ["S", "B", "D", "C", "G"])
        self.assertEqual(r["cost"], 9)
        self.assertEqual(r["order"], ["S", "B", "A", "D", "C", "G"])
        self.assertEqual(r["expanded"], 5)
        self.assertEqual(r["skipped"], 2)
        self.assertEqual(r["max_frontier"], 5)

    def test_stale_records_dropped_before_goal(self):
        r = s.ucs(UCS_GRAPH, "S", "G")
        skips = [row for row in r["trace"] if row["event"] == "SKIP"]
        self.assertEqual(len(skips), r["skipped"])
        self.assertEqual(r["order"].count("G"), 1)
        self.assertLess(r["order"].index("G"), len(r["order"]))

    def test_equal_cost_keeps_old_parent(self):
        g = {"S": [("G", 3), ("A", 1)], "A": [("G", 2)], "G": []}
        r = s.ucs(g, "S", "G")
        self.assertEqual(r["path"], ["S", "G"])
        self.assertEqual(r["cost"], 3)
        self.assertEqual(r["skipped"], 0)

    def test_ties_use_vertex_names(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("G", 2)], "B": [("G", 2)],
             "G": []}
        self.assertEqual(s.ucs(g, "S", "G")["path"], ["S", "A", "G"])

    def test_not_stopping_at_generation(self):
        g = {"S": [("G", 10), ("A", 1)], "A": [("G", 2)], "G": []}
        self.assertEqual(s.ucs(g, "S", "G")["cost"], 3)

    def test_invalid_weights(self):
        for w in [0, -1, inf, float("nan"), True, "3"]:
            with self.subTest(w=w):
                g = {"S": [("G", w)], "G": []}
                with self.assertRaises(ValueError):
                    s.ucs(g, "S", "G")

    def test_start_is_goal_and_unreachable(self):
        self.assertEqual(s.ucs(UCS_GRAPH, "G", "G")["path"], ["G"])
        r = s.ucs(UCS_GRAPH, "S", "X")
        self.assertIsNone(r["path"])
        self.assertEqual(r["cost"], inf)


class GreedyTests(unittest.TestCase):
    def test_main_h(self):
        r = s.greedy(GREEDY_GRAPH, "S", "G", GREEDY_H)
        self.assertEqual(r["path"], ["S", "B", "E", "G"])
        self.assertEqual(r["cost"], 12)
        self.assertEqual(r["order"], ["S", "A", "B", "E", "G"])
        self.assertEqual(r["expanded"], 4)
        self.assertEqual(r["max_frontier"], 3)

    def test_selects_from_whole_frontier(self):
        r = s.greedy(GREEDY_GRAPH, "S", "G", GREEDY_H)
        self.assertEqual(r["order"][1], "A")
        self.assertEqual(r["order"][2], "B")
        self.assertNotIn("B", [v for v, w in GREEDY_GRAPH["A"]])

    def test_h2_changes_decision(self):
        r = s.greedy(GREEDY_GRAPH, "S", "G", GREEDY_H2)
        self.assertEqual(r["path"], ["S", "C", "G"])
        self.assertEqual(r["cost"], 6)
        self.assertEqual(r["expanded"], 2)

    def test_h0_is_not_bfs_order(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("C", 1)], "B": [("G", 1)],
             "C": [("G", 1)], "G": []}
        g0 = {u: 0 for u in g}
        r = s.greedy(g, "S", "G", g0)
        self.assertEqual(r["order"], ["S", "A", "B", "C", "G"])
        self.assertEqual(r["path"], ["S", "B", "G"])
        self.assertEqual(s.bfs(g, "S", "G")["order"], ["S", "B", "A", "G"])

    def test_invalid_h(self):
        for h in [{}, {k: v for k, v in GREEDY_H.items() if k != "X"},
                  {**GREEDY_H, "A": -1}, {**GREEDY_H, "G": 1}]:
            with self.subTest(h=h):
                with self.assertRaises(ValueError):
                    s.greedy(GREEDY_GRAPH, "S", "G", h)

    def test_cycle_and_unreachable(self):
        g = {"S": [("A", 1)], "A": [("S", 1)], "G": []}
        r = s.greedy(g, "S", "G", {"S": 1, "A": 1, "G": 0})
        self.assertIsNone(r["path"])
        self.assertEqual(r["order"], ["S", "A"])


class AstarTests(unittest.TestCase):
    def maze(self, k):
        return maze_graph(WATER_MAZE, water_cost=k)

    def test_maze_k5(self):
        graph, start, goal, h = self.maze(5)
        r = s.astar(graph, start, goal, h)
        self.assertEqual(r["cost"], 5)
        self.assertEqual(r["path"], ["0,0", "1,0", "1,1", "1,2", "1,3", "0,3"])
        self.assertEqual(r["expanded"], 5)
        self.assertEqual(r["max_frontier"], 5)
        self.assertEqual(r["cost"], oracle(graph, start, goal))

    def test_maze_k1_and_k8(self):
        for k, expected in ((1, 3), (8, 5)):
            graph, start, goal, h = self.maze(k)
            r = s.astar(graph, start, goal, h)
            with self.subTest(k=k):
                self.assertEqual(r["cost"], expected)
                self.assertEqual(r["cost"], oracle(graph, start, goal))

    def test_manhattan_is_consistent(self):
        graph, start, goal, h = self.maze(5)
        for u in graph:
            for v, w in graph[u]:
                self.assertLessEqual(h[u], w + h[v])

    def test_h_zero_matches_ucs(self):
        h = {u: 0 for u in UCS_GRAPH}
        a = s.astar(UCS_GRAPH, "S", "G", h)
        b = s.ucs(UCS_GRAPH, "S", "G")
        for key in ("path", "cost", "order", "expanded", "skipped",
                    "max_frontier"):
            self.assertEqual(a[key], b[key])

    def test_reopen_vs_closed_once(self):
        yes = s.astar(REOPEN_GRAPH, "S", "G", REOPEN_H)
        no = s.astar(REOPEN_GRAPH, "S", "G", REOPEN_H, reopen=False)
        self.assertEqual((yes["cost"], yes["reopened"]), (9, 1))
        self.assertEqual(yes["order"], ["S", "B", "C", "A", "C", "G"])
        self.assertEqual(yes["expanded"], 5)
        self.assertEqual(no["cost"], 11)
        self.assertEqual(no["reopened"], 0)

    def test_not_stopping_at_generation(self):
        g = {"S": [("G", 10), ("A", 1)], "A": [("G", 2)], "G": []}
        r = s.astar(g, "S", "G", {"S": 2, "A": 1, "G": 0})
        self.assertEqual((r["path"], r["cost"]), (["S", "A", "G"], 3))

    def test_invalid_h(self):
        for h in [{}, {**GREEDY_H, "G": 1}, {**GREEDY_H, "A": -1},
                  {**GREEDY_H, "A": inf}, {**GREEDY_H, "A": float("nan")}]:
            with self.assertRaises(ValueError):
                s.astar(GREEDY_GRAPH, "S", "G", h)

    def test_start_is_goal(self):
        r = s.astar(GREEDY_GRAPH, "G", "G", GREEDY_H)
        self.assertEqual((r["path"], r["cost"], r["expanded"]),
                         (["G"], 0, 0))

    def test_ties_use_vertex_names(self):
        g = {"S": [("B", 1), ("A", 1)], "A": [("G", 1)],
             "B": [("G", 1)], "G": []}
        h = {"S": 2, "A": 1, "B": 1, "G": 0}
        r = s.astar(g, "S", "G", h)
        self.assertEqual(r["order"], ["S", "A", "B", "G"])
        self.assertEqual((r["path"], r["cost"]), (["S", "A", "G"], 2))


class ContractTests(unittest.TestCase):
    KEYS = {"path", "cost", "order", "expanded", "skipped", "reopened",
            "max_frontier", "trace"}

    def all_runs(self, graph, start, goal, h):
        yield "dfs", s.dfs(graph, start, goal)
        yield "bfs", s.bfs(graph, start, goal)
        yield "ucs", s.ucs(graph, start, goal)
        yield "greedy", s.greedy(graph, start, goal, h)
        yield "astar", s.astar(graph, start, goal, h)

    def test_result_keys(self):
        for name, r in self.all_runs(GREEDY_GRAPH, "S", "G", GREEDY_H):
            with self.subTest(name=name):
                self.assertEqual(set(r), self.KEYS)
                self.assertEqual(r["reopened"], 0)

    def test_trace_counters_match_result(self):
        graph, start, goal, h = maze_graph(WATER_MAZE, water_cost=5)
        for name, r in self.all_runs(graph, start, goal, h):
            events = [row["event"] for row in r["trace"]]
            with self.subTest(name=name):
                self.assertEqual(events[0], "INIT")
                self.assertIn(events[-1], ("GOAL", "FAIL"))
                self.assertEqual(events.count("EXPAND"), r["expanded"])
                self.assertEqual(events.count("SKIP"), r["skipped"])
                self.assertGreaterEqual(r["max_frontier"], 1)

    def test_path_cost_consistency(self):
        for name, r in self.all_runs(UCS_GRAPH, "S", "G",
                                     {u: 0 for u in UCS_GRAPH}):
            with self.subTest(name=name):
                self.assertEqual(r["cost"], path_cost(UCS_GRAPH, r["path"]))

    def test_no_import_of_demo_modules(self):
        source = (ROOT / "bai_lam.py").read_text(encoding="utf-8")
        lines = [line.strip() for line in source.splitlines()]
        imports = [line for line in lines
                   if line.startswith(("import ", "from "))]
        self.assertFalse([line for line in imports if "_demo" in line])

    def test_random_graphs_optimal(self):
        rng = random.Random(11112026)
        names = ["S", "A", "B", "C", "G"]
        for trial in range(40):
            g = {u: [] for u in names}
            for u in names[:-1]:
                for v in names:
                    if v != u and (v == "G" or rng.random() < .35):
                        g[u].append((v, rng.randint(1, 9)))
                rng.shuffle(g[u])
            true_h = {u: oracle(g, u, "G") for u in g}
            admissible = {u: 0 if true_h[u] == inf
                          else rng.randint(0, int(true_h[u])) for u in g}
            optimum = oracle(g, "S", "G")
            with self.subTest(trial=trial):
                self.assertEqual(s.ucs(g, "S", "G")["cost"], optimum)
                self.assertEqual(s.astar(g, "S", "G", admissible)["cost"],
                                 optimum)
                self.assertEqual(s.astar(g, "S", "G", true_h, reopen=False)["cost"],
                                 optimum)
                r = s.bfs(g, "S", "G")
                self.assertEqual(len(r["path"]) - 1,
                                 oracle(g, "S", "G", unit=True))
                for name, result in self.all_runs(g, "S", "G", admissible):
                    if result["path"] is not None:
                        self.assertEqual(result["cost"],
                                         path_cost(g, result["path"]))


class RunnerTests(unittest.TestCase):
    def test_runner_saves_output(self):
        p = subprocess.run([sys.executable, str(ROOT / "chay_bai_lam.py"),
                            "--bai", "9", "--summary"],
                           text=True, capture_output=True, cwd=ROOT, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("COST: 9", p.stdout)
        payload = json.loads((ROOT / "output" / "bai9.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(payload["bai"], 9)
        self.assertEqual(payload["cost"], 9)
        self.assertEqual(payload["path"], ["S", "B", "D", "C", "G"])
        csv_text = (ROOT / "output" / "bai9_trace.csv").read_text(
            encoding="utf-8-sig")
        self.assertTrue(csv_text.splitlines()[0].startswith("index,event,node"))

    def test_runner_rejects_wrong_case(self):
        p = subprocess.run([sys.executable, str(ROOT / "chay_bai_lam.py"),
                            "--bai", "7", "--case", "blocked", "--no-save"],
                           text=True, capture_output=True, cwd=ROOT, timeout=30)
        self.assertNotEqual(p.returncode, 0)

    def test_runner_step_without_saving(self):
        p = subprocess.run([sys.executable, str(ROOT / "chay_bai_lam.py"),
                            "--bai", "7", "--step", "--no-save"],
                           input="\n" * 40, text=True, capture_output=True,
                           cwd=ROOT, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("COST: 6", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
