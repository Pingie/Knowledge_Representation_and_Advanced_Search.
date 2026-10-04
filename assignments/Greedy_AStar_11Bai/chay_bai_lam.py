"""Chạy dữ liệu CHÍNH của bài làm và lưu kết quả vào output/.

Lệnh chuẩn:
    python chay_bai_lam.py --bai 7
    python chay_bai_lam.py --bai 8 --case blocked
    python chay_bai_lam.py --bai 10 --case h2
    python chay_bai_lam.py --bai 11 --k 1
    python chay_bai_lam.py --bai 11 --step

Mỗi lần chạy ghi output/bai{N}.json (kết quả + trace) và
output/bai{N}_trace.csv (từng sự kiện). Runner chỉ chạy dữ liệu chính;
các ca biến đổi và ca biên do sinh viên tự kiểm thử trong test_bai_lam.py.
"""
import argparse
import csv
import json
from math import inf
from pathlib import Path

import bai_lam
from common import show_result, maze_graph, draw_maze
from du_lieu_baitap import (DFS_GRAPH, BFS_MAZE, BFS_BLOCKED, UCS_GRAPH,
                            GREEDY_GRAPH, GREEDY_H, GREEDY_H2, WATER_MAZE,
                            REOPEN_GRAPH, REOPEN_H)

ROOT = Path(__file__).resolve().parent
ALGO = {7: "dfs", 8: "bfs", 9: "ucs", 10: "greedy", 11: "astar"}
CASES = {7: ("graph",), 8: ("maze", "blocked"), 9: ("graph",),
         10: ("h", "h2", "h0"), 11: ("maze", "reopen")}


def build_case(bai: int, case: str, goal: str, k: int) -> dict:
    info = {"rows": None, "h": None}
    if bai == 7:
        target = goal or "G"
        info.update(graph=DFS_GRAPH, start="S", goal=target)
    elif bai == 8:
        info["rows"] = BFS_BLOCKED if case == "blocked" else BFS_MAZE
        graph, start, target, _ = maze_graph(info["rows"])
        info.update(graph=graph, start=start, goal=target)
    elif bai == 9:
        target = goal or "G"
        info.update(graph=UCS_GRAPH, start="S", goal=target)
    elif bai == 10:
        target = goal or "G"
        if case == "h2":
            h = GREEDY_H2
        elif case == "h0":
            h = {u: 0 for u in GREEDY_GRAPH}
        else:
            h = GREEDY_H
        info.update(graph=GREEDY_GRAPH, start="S", goal=target, h=h)
    elif case == "reopen":
        info.update(graph=REOPEN_GRAPH, start="S", goal="G", h=REOPEN_H)
    else:
        info["rows"] = WATER_MAZE
        graph, start, target, h = maze_graph(WATER_MAZE, water_cost=k)
        info.update(graph=graph, start=start, goal=target, h=h)
    if bai == 7:
        label = f"DFS_GRAPH S->{info['goal']}"
    elif bai == 8:
        label = f"maze {info['rows']}"
    elif bai == 9:
        label = f"UCS_GRAPH S->{info['goal']}"
    elif bai == 10:
        label = f"GREEDY_GRAPH {case} S->{info['goal']}"
    elif case == "reopen":
        label = "REOPEN_GRAPH (Bai 5) S->G"
    else:
        label = f"WATER_MAZE k={k}"
    info.update(case=case, label=label)
    return info


def save_output(bai: int, info: dict, result: dict) -> list:
    folder = ROOT / "output"
    folder.mkdir(exist_ok=True)
    payload = {"bai": bai, "algo": ALGO[bai], "case": info["case"],
               "input": info["label"], "start": info["start"],
               "goal": info["goal"]}
    payload.update(result)
    if payload["cost"] == inf:
        payload["cost"] = None
    json_path = folder / f"bai{bai}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2,
                                    allow_nan=False), encoding="utf-8")
    csv_path = folder / f"bai{bai}_trace.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "event", "node", "note", "before", "after"])
        for index, row in enumerate(result["trace"]):
            writer.writerow([index, row["event"], row["node"], row["note"],
                             " | ".join(row["before"]),
                             " | ".join(row["after"])])
    return [json_path, csv_path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Chay bai lam va luu output/")
    parser.add_argument("--bai", type=int, choices=tuple(ALGO), required=True,
                        help="so bai 7..11")
    parser.add_argument("--case", default=None,
                        help="ca du lieu chinh; xem CASES trong file nay")
    parser.add_argument("--goal", default=None, help="doi dinh (vd: X)")
    parser.add_argument("--k", type=int, default=5,
                        help="phi di vao o nuoc cho bai 11 (mac dinh 5)")
    parser.add_argument("--step", action="store_true",
                        help="dung TRONG thuat toan sau moi su kien")
    parser.add_argument("--summary", action="store_true",
                        help="chi in ket qua (khong dung voi --step)")
    parser.add_argument("--no-reopen", action="store_true",
                        help="A* dong mot lan, chi cho bai 11")
    parser.add_argument("--no-save", action="store_true",
                        help="khong ghi file vao output/")
    args = parser.parse_args()
    if args.step and args.summary:
        parser.error("--step va --summary la hai che do khac nhau; chi chon mot")
    if args.case is None:
        args.case = CASES[args.bai][0]
    if args.case not in CASES[args.bai]:
        parser.error(f"bai {args.bai} chi co cac case: {', '.join(CASES[args.bai])}")
    if args.no_reopen and args.bai != 11:
        parser.error("--no-reopen chi danh cho bai 11 (A*)")
    if args.goal and args.bai not in (7, 9, 10):
        parser.error("--goal chi danh cho bai 7, 9, 10")
    try:
        info = build_case(args.bai, args.case, args.goal, args.k)
        function = getattr(bai_lam, ALGO[args.bai])
        kwargs = {"step": args.step}
        if info["h"] is not None:
            kwargs["h"] = info["h"]
        if args.bai == 11 and info["case"] != "reopen":
            kwargs["reopen"] = not args.no_reopen
        result = function(info["graph"], info["start"], info["goal"], **kwargs)
    except NotImplementedError as exc:
        parser.exit(2, f"Chua lam bai: {exc}\n")
    except (ValueError, EOFError) as exc:
        parser.exit(2, f"Loi: {exc}\nChay --step trong TERMINAL, khong trong Output/Debug Console.\n")
    except KeyboardInterrupt:
        print("\nDa dung theo yeu cau.")
        raise SystemExit(130)
    print(f"BAI {args.bai} | {ALGO[args.bai]} | {info['label']}")
    show_result(result, include_trace=not (args.step or args.summary))
    if info["rows"] is not None:
        print("\nMAZE (* is the returned path):\n"
              + draw_maze(info["rows"], result["path"]))
    if not args.no_save:
        for path in save_output(args.bai, info, result):
            print("SAVED:", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
