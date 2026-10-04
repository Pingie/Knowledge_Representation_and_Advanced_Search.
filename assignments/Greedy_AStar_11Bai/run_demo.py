"""Lối chạy ở THƯ MỤC GỐC. Không cần cd python.
python run_demo.py --algo astar --step
python run_demo.py --algo astar --case reopen --no-reopen
"""
import argparse
import json
from pathlib import Path
from common import show_result, maze_graph, draw_maze
from data_mau import GRAPH, H, REOPEN_GRAPH, REOPEN_H, MAZE, FRONTIER_GRAPH, FRONTIER_H
from dfs_demo import dfs
from bfs_demo import bfs
from ucs_demo import ucs
from greedy_demo import greedy
from astar_demo import astar

ALGORITHMS = {"dfs": dfs, "bfs": bfs, "ucs": ucs, "greedy": greedy, "astar": astar}


def run_named(default=None):
    parser = argparse.ArgumentParser(description="Tim kiem: chay mau va dung tung buoc")
    parser.add_argument("--algo", choices=ALGORITHMS, default=default or "astar")
    parser.add_argument("--case", choices=("graph", "reopen", "maze", "frontier"), default="graph")
    parser.add_argument("--step", action="store_true", help="dung TRONG thuat toan sau moi su kien")
    parser.add_argument("--summary", action="store_true", help="chi in ket qua (khong dung voi --step)")
    parser.add_argument("--no-reopen", action="store_true", help="A* dong mot lan, de doi chieu")
    parser.add_argument("--goal", default=None)
    parser.add_argument("--json", type=Path, default=None, help="luu ket qua thanh JSON")
    args = parser.parse_args()
    if args.step and args.summary:
        parser.error("--step va --summary la hai che do khac nhau; chi chon mot")
    if args.no_reopen and args.algo != "astar":
        parser.error("--no-reopen chi danh cho A*")
    graph, h, start, goal = GRAPH, H, "S", "G"
    if args.case == "reopen":
        graph, h = REOPEN_GRAPH, REOPEN_H
    elif args.case == "frontier":
        graph, h = FRONTIER_GRAPH, FRONTIER_H
    elif args.case == "maze":
        graph, start, goal, h = maze_graph(MAZE)
    goal = args.goal or goal
    # Đổi đích với Greedy/A* cần bảng h mới; bộ graph chỉ hỗ trợ G hoặc X có h=0.
    try:
        function = ALGORITHMS[args.algo]
        kwargs = {"step": args.step}
        if args.algo in ("greedy", "astar"):
            kwargs["h"] = h
        if args.algo == "astar":
            kwargs["reopen"] = not args.no_reopen
        result = function(graph, start, goal, **kwargs)
        show_result(result, include_trace=not (args.step or args.summary))
        if args.case == "maze":
            print("\nMAZE (* is the returned path):\n" + draw_maze(MAZE, result["path"]))
        if args.json:
            # Chuẩn JSON không có Infinity: dùng null cho chi phí thất bại.
            output = dict(result)
            if output["path"] is None:
                output["cost"] = None
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    except (ValueError, EOFError) as exc:
        parser.exit(2, f"Loi: {exc}\nChay --step trong TERMINAL, khong trong Output/Debug Console.\n")
    except KeyboardInterrupt:
        print("\nDa dung theo yeu cau.")
        raise SystemExit(130)


if __name__ == "__main__":
    run_named()
