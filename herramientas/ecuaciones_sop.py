#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obtiene, para cada segmento, los minitérminos y la suma de productos mínima (Quine-McCluskey,
con sympy.logic.SOPform) a partir de tabla.txt. Muestra la lógica combinacional equivalente a la LUT.

Uso (desde la raíz del repositorio):
    pip install sympy
    python herramientas/ecuaciones_sop.py
"""

import sys
from pathlib import Path

from sympy import symbols
from sympy.logic import SOPform

ROOT = Path(__file__).resolve().parent.parent
SEGMENTS = "abcdefg"
D3, D2, D1, D0 = VARS = symbols("D3 D2 D1 D0")


def fmt_term(term):
    """D3 & ~D1 -> D3·D1'"""
    literals = term.args if term.func.__name__ == "And" else (term,)
    names = []
    for lit in literals:
        negated = lit.func.__name__ == "Not"
        names.append((str(lit.args[0]) if negated else str(lit)) + ("'" if negated else ""))
    return "·".join(sorted(names, key=lambda s: -int(s[1])))


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Σ y · en consolas de Windows
    table =[int(line, 2) for line in (ROOT / "tabla.txt").read_text(encoding="utf-8").split()]
    for i, seg in enumerate(SEGMENTS):
        bit = 6 - i
        minterms = [n for n in range(16) if table[n] >> bit & 1]
        sop = SOPform(list(VARS), [[n >> k & 1 for k in (3, 2, 1, 0)] for n in minterms])
        terms = sop.args if sop.func.__name__ == "Or" else (sop,)
        print(f"{seg} = Σm({', '.join(map(str, minterms))})")
        print(f"  = {' + '.join(fmt_term(t) for t in terms)}")


if __name__ == "__main__":
    main()
