#!/usr/bin/env python3
import re
import argparse
from typing import Tuple, Optional

BEGIN_RE = re.compile(r"-+\s*Begin\s+crystal", re.IGNORECASE)
END_RE   = re.compile(r"-+\s*End\s+crystal", re.IGNORECASE)

# Example line:
# Cell parameters 28.28323 16.77610 28.65649 nm, 89.34792 119.42151 89.96030 deg
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
        description="Filter crystal blocks by Cell parameters with tolerances."
    )
    p.add_argument("infile", help="Input log file")
    p.add_argument("outfile", help="Where to write matching crystal blocks")
    p.add_argument("--a", type=float, required=True)
    p.add_argument("--b", type=float, required=True)
    p.add_argument("--c", type=float, required=True)
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--beta",  type=float, required=True)
    p.add_argument("--gamma", type=float, required=True)

    # Tolerances: absolute or relative (%) for lengths/angles
    p.add_argument("--len-abs", type=float, default=None,
                   help="Absolute tolerance for a,b,c (same units as inputs)")
    p.add_argument("--ang-abs", type=float, default=None,
                   help="Absolute tolerance for α,β,γ in degrees")
    p.add_argument("--len-rel", type=float, default=None,
                   help="Relative tolerance %% for a,b,c (e.g., 1.0 means ±1%)")
    p.add_argument("--ang-rel", type=float, default=None,
                   help="Relative tolerance %% for α,β,γ")

    p.add_argument("--targets-in-angstrom", action="store_true",
                   help="If set, convert your a,b,c from Å to nm to match logs that print nm.")
    return p.parse_args()

def within(val: float, target: float,
           abs_tol: Optional[float], rel_pct: Optional[float]) -> bool:
    abs_ok = True
    if abs_tol is not None:
        abs_ok = abs(val - target) <= abs_tol
    rel_ok = True
    if rel_pct is not None:
        rel_tol = abs(target) * (rel_pct / 100.0)
        rel_ok = abs(val - target) <= rel_tol
    # If both provided, require BOTH to pass (strict). Change to "or" if you prefer.
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

    # Optional Å → nm conversion for targets if your log prints "nm"
    if args.targets_in_angstrom:
        # 1 Å = 0.1 nm
        targets = (targets[0]*0.1, targets[1]*0.1, targets[2]*0.1,
                   targets[3], targets[4], targets[5])

    in_block = False
    block_lines = []
    found_cell = None  # store tuple of floats when parsed

    wrote_any = False

    with open(args.infile, "r", encoding="utf-8", errors="replace") as fin, \
         open(args.outfile, "w", encoding="utf-8") as fout:

        for line in fin:
            if not in_block:
                if BEGIN_RE.search(line):
                    in_block = True
                    block_lines = [line]
                    found_cell = None
                continue
            # in_block == True
            block_lines.append(line)

            # Try to parse Cell parameters when seen
            if found_cell is None:
                m = CELL_RE.search(line)
                if m:
                    a,b,c,al,be,ga = map(float, m.groups())
                    found_cell = (a,b,c,al,be,ga)

            if END_RE.search(line):
                # Decide whether to write the block
                if found_cell is not None and match_cell(
                    found_cell, targets, args.len_abs, args.ang_abs, args.len_rel, args.ang_rel
                ):
                    fout.writelines(block_lines)
                    if not block_lines[-1].endswith("\n"):
                        fout.write("\n")
                    wrote_any = True
                # reset for next block
                in_block = False
                block_lines = []
                found_cell = None

    if not wrote_any:
        # Gentle nudge if nothing passed the filter.
        print("No crystal blocks matched the specified tolerances.")

if __name__ == "__main__":
    main()
