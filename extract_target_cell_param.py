#!/usr/bin/env python3
import re
import argparse
from typing import Tuple, Optional

BEGIN_CHUNK_RE   = re.compile(r"-+\s*Begin\s+chunk", re.IGNORECASE)
END_CHUNK_RE     = re.compile(r"-+\s*End\s+chunk", re.IGNORECASE)
BEGIN_CRYSTAL_RE = re.compile(r"-+\s*Begin\s+crystal", re.IGNORECASE)
END_CRYSTAL_RE   = re.compile(r"-+\s*End\s+crystal", re.IGNORECASE)
HEADER_END_RE    = re.compile(r"-+\s*End\s+Unit\s+Cell\s*-+", re.IGNORECASE)

CELL_RE = re.compile(
    r"Cell\s+parameters\s+"
    r"([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*"
    r"(?:nm|Å|A)?\s*,?\s+"
    r"([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*"
    r"(?:deg)?",
    re.IGNORECASE,
)

def parse_args():
    p = argparse.ArgumentParser(
        description="Filter CrysFEL stream by Cell parameters, keeping chunk + matching crystal."
    )
    p.add_argument("infile", help="Input CrysFEL stream file")
    p.add_argument("outfile", help="Output file with header + matching chunks + crystals")
    p.add_argument("--a", type=float, required=True)
    p.add_argument("--b", type=float, required=True)
    p.add_argument("--c", type=float, required=True)
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--beta",  type=float, required=True)
    p.add_argument("--gamma", type=float, required=True)
    p.add_argument("--len-abs", type=float, default=None)
    p.add_argument("--ang-abs", type=float, default=None)
    p.add_argument("--len-rel", type=float, default=None)
    p.add_argument("--ang-rel", type=float, default=None)
    p.add_argument("--targets-in-angstrom", action="store_true")
    return p.parse_args()

def within(val: float, target: float,
           abs_tol: Optional[float], rel_pct: Optional[float]) -> bool:
    abs_ok = True if abs_tol is None else abs(val - target) <= abs_tol
    rel_ok = True if rel_pct is None else abs(val - target) <= abs(target) * (rel_pct / 100.0)
    return abs_ok and rel_ok

def match_cell(params: Tuple[float, float, float, float, float, float],
               targets: Tuple[float, float, float, float, float, float],
               len_abs: Optional[float], ang_abs: Optional[float],
               len_rel: Optional[float], ang_rel: Optional[float]) -> bool:
    a,b,c,al,be,ga = params
    ta,tb,tc,tal,tbe,tga = targets
    return (
        within(a,  ta,  len_abs, len_rel) and
        within(b,  tb,  len_abs, len_rel) and
        within(c,  tc,  len_abs, len_rel) and
        within(al, tal, ang_abs, ang_rel) and
        within(be, tbe, ang_abs, ang_rel) and
        within(ga, tga, ang_abs, ang_rel)
    )

def main():
    args = parse_args()
    targets = (args.a, args.b, args.c, args.alpha, args.beta, args.gamma)

    if args.targets_in_angstrom:
        targets = (targets[0]*0.1, targets[1]*0.1, targets[2]*0.1,
                   targets[3], targets[4], targets[5])

    wrote_any = False

    with open(args.infile, "r", encoding="utf-8", errors="replace") as fin, \
         open(args.outfile, "w", encoding="utf-8") as fout:

        # Step 1 — copy header until End Unit Cell
        for line in fin:
            fout.write(line)
            if HEADER_END_RE.search(line):
                break

        # Step 2 — parse in chunk+crystal pairs
        while True:
            chunk_lines = []
            crystal_lines = []
            found_cell = None

            # Find next chunk
            for line in fin:
                if BEGIN_CHUNK_RE.search(line):
                    chunk_lines.append(line)
                    break
            else:
                break  # no more chunks, EOF

            # Read chunk body
            for line in fin:
                chunk_lines.append(line)
                if END_CHUNK_RE.search(line):
                    break

            # Expect a crystal right after
            for line in fin:
                if BEGIN_CRYSTAL_RE.search(line):
                    crystal_lines.append(line)
                    break
            else:
                break  # no more crystals

            # Read crystal body
            for line in fin:
                crystal_lines.append(line)
                if found_cell is None:
                    m = CELL_RE.search(line)
                    if m:
                        found_cell = tuple(map(float, m.groups()))
                if END_CRYSTAL_RE.search(line):
                    break

            # Now decide whether to keep both
            if found_cell and match_cell(
                found_cell, targets,
                args.len_abs, args.ang_abs, args.len_rel, args.ang_rel
            ):
                fout.writelines(chunk_lines)
                fout.writelines(crystal_lines)
                wrote_any = True

    if not wrote_any:
        print("No matching chunk+crystal pairs found (header still written).")

if __name__ == "__main__":
    main()
