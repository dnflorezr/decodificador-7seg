#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera las figuras SVG del README:
  * img/patrones.svg -> los 16 patrones de tabla.txt dibujados como un display de 7 segmentos
  * img/ondas_vcd.svg -> las formas de onda de simulacion/sevensegdec_tb.vcd (estilo GTKWave)

Uso (desde la raíz del repositorio):
    python herramientas/generar_figuras.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEGMENTS = "abcdefg"
NAMES = ["0", "1 (derecha)", "2", "3", "4", "5", "6 (cerrado)", "7", "8", "9 (cerrado)",
         "¬ NOT", "∩ AND", "∪ OR", "_ nivel 0", "− nivel Z", "‾ nivel 1"]
FONT = "Consolas, 'DejaVu Sans Mono', monospace"

# Colores (cada figura trae su propio fondo oscuro, así se ve igual en tema claro u oscuro)
BG, PANEL, TEXT, SUBTEXT = "#0f1115", "#181b21", "#e6e6e6", "#9aa0a6"
LED_ON, LED_OFF = "#ff3b30", "#2c3038"
TRACE, GRID, MARK = "#3ddc84", "#2a3340", "#f2cc60"


def read_table(path):
    return [int(line, 2) for line in path.read_text(encoding="utf-8").split()]


def is_lit(pattern, seg):
    return pattern >> (6 - SEGMENTS.index(seg)) & 1


# ---------------------------------------------------------------- display de 7 segmentos

def hseg(x0, x1, y, t):
    h = t / 2
    return [(x0, y), (x0 + h, y - h), (x1 - h, y - h), (x1, y), (x1 - h, y + h), (x0 + h, y + h)]


def vseg(x, y0, y1, t):
    h = t / 2
    return [(x, y0), (x + h, y0 + h), (x + h, y1 - h), (x, y1), (x - h, y1 - h), (x - h, y0 + h)]


def segment_polygons(ox, oy, w, h, t):
    """Polígonos de los segmentos a-g de un dígito con esquina superior izquierda (ox, oy)"""
    left, right, top, mid, bottom = ox, ox + w, oy, oy + h / 2, oy + h
    g = t * 0.6
    return {
        "a": hseg(left + g, right - g, top, t),
        "b": vseg(right, top + g, mid - g, t),
        "c": vseg(right, mid + g, bottom - g, t),
        "d": hseg(left + g, right - g, bottom, t),
        "e": vseg(left, mid + g, bottom - g, t),
        "f": vseg(left, top + g, mid - g, t),
        "g": hseg(left + g, right - g, mid, t),
    }


def digit(pattern, ox, oy, w, h, t):
    out = []
    for seg, pts in segment_polygons(ox, oy, w, h, t).items():
        points = " ".join(f"{x:g},{y:g}" for x, y in pts)
        out.append(f'<polygon points="{points}" fill="{LED_ON if is_lit(pattern, seg) else LED_OFF}"/>')
    return "".join(out)


def text(x, y, s, size=14, color=TEXT, anchor="middle", weight="normal"):
    attrs = f' fill="{color}"' if color != TEXT else ""
    attrs += f' text-anchor="{anchor}"' if anchor != "middle" else ""
    attrs += f' font-weight="{weight}"' if weight != "normal" else ""
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}"{attrs}>{s}</text>'


def svg_open(width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">',
            f'<style>text{{font-family:{FONT};fill:{TEXT};text-anchor:middle}}</style>',
            f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>']


def patterns_svg(table):
    cell_w, cell_h, ref_w, pad = 116, 196, 170, 16
    width = pad * 2 + ref_w + 8 * cell_w
    height = pad * 2 + 2 * cell_h
    out = svg_open(width, height)

    # referencia: dígito grande con el nombre de cada segmento
    x, y = pad, pad
    out.append(f'<rect x="{x + 4}" y="{y + 4}" width="{ref_w - 16}" height="{2 * cell_h - 8}" rx="10" fill="{PANEL}"/>')
    ox, oy, w, h = x + 45, y + 70, 70, 130
    out.append(digit(0b1111111, ox, oy, w, h, 14))
    labels = {"a": (w / 2, -16), "b": (w + 20, h / 4), "c": (w + 20, 3 * h / 4), "d": (w / 2, h + 28),
              "e": (-20, 3 * h / 4), "f": (-20, h / 4), "g": (w / 2, h / 2 - 22)}
    for seg, (dx, dy) in labels.items():
        out.append(text(ox + dx, oy + dy + 5, seg, 18, TEXT, weight="bold"))
    out.append(text(x + ref_w / 2 - 6, y + 36, "segmentos", 14, SUBTEXT))
    out.append(text(x + ref_w / 2 - 6, y + 290, "bit 6 … bit 0", 13, SUBTEXT))
    out.append(text(x + ref_w / 2 - 6, y + 310, "a b c d e f g", 13, SUBTEXT))

    for value, pattern in enumerate(table):
        col, row = value % 8, value // 8
        x, y = pad + ref_w + col * cell_w, pad + row * cell_h
        out.append(f'<rect x="{x + 4}" y="{y + 4}" width="{cell_w - 8}" height="{cell_h - 8}" rx="10" fill="{PANEL}"/>')
        out.append(digit(pattern, x + 33, y + 22, 50, 90, 10))
        out.append(text(x + cell_w / 2, y + 138, f"{value}", 18, TEXT, weight="bold"))
        out.append(text(x + cell_w / 2, y + 158, f"{pattern:07b}", 13, SUBTEXT))
        out.append(text(x + cell_w / 2, y + 178, NAMES[value], 13, TEXT))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- formas de onda del VCD

def parse_vcd(path):
    """Devuelve ({señal: [(t, valor), ...]}, t_final) para un VCD de MyHDL con vectores"""
    ids, now, end, values = {}, 0, 0, {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("$var"):
            _, _, _, ident, name, *_ = s.split()
            ids.setdefault(ident, name)          # el primer nombre (nivel superior) gana
        elif s.startswith("#"):
            now = end = int(s[1:])
        elif s.startswith("b"):
            bits, ident = s[1:].split()
            values.setdefault(ids[ident], {})[now] = int(bits, 2)   # último valor en cada instante
    return {name: sorted(v.items()) for name, v in values.items()}, end


def intervals(changes, end):
    return [(t, changes[i + 1][0] if i + 1 < len(changes) else end, v) for i, (t, v) in enumerate(changes)]


def waves_svg(signals, end):
    x0, scale, pad, row_h = 170, 6, 16, 34
    bcd = intervals(signals["bcd_tb"], end)
    sseg = intervals(signals["sseg_tb"], end)
    rows = ["bcd_tb[3:0]", "sseg_tb[6:0]"] + [f"{s}  sseg[{6 - i}]" for i, s in enumerate(SEGMENTS)]
    top = pad + 110
    width = x0 + end * scale + 40
    height = top + len(rows) * row_h + 70
    X = lambda t: x0 + t * scale
    out = svg_open(width, height)
    out.append(text(pad, pad + 14, "sevensegdec_tb.vcd  (timescale 1 ns)", 14, SUBTEXT, "start"))

    # fila de displays: cómo se vería el dígito en cada intervalo
    out.append(text(pad, pad + 62, "display", 14, TEXT, "start"))
    for t0, t1, v in sseg:
        out.append(digit(v, X((t0 + t1) / 2) - 13, pad + 34, 26, 46, 6))

    # rejilla y marcas de muestreo del testbench (t = 10, 20, ... 160)
    for t in range(0, end + 1, 10):
        out.append(f'<line x1="{X(t)}" y1="{top - 8}" x2="{X(t)}" y2="{top + len(rows) * row_h}" stroke="{GRID}"/>')
        out.append(text(X(t), top + len(rows) * row_h + 18, str(t), 11, SUBTEXT))
        if t > 0:
            yb = top + len(rows) * row_h + 26
            out.append(f'<polygon points="{X(t)},{yb} {X(t) - 5},{yb + 8} {X(t) + 5},{yb + 8}" fill="{MARK}"/>')
    out.append(text(x0, height - 14, "▲ instantes en que el testbench compara sseg_tb con la tabla (justo antes del siguiente cambio)",
                    12, MARK, "start"))

    for r, name in enumerate(rows):
        y = top + r * row_h
        hi, lo, mid = y + 6, y + row_h - 8, y + row_h / 2 - 1
        out.append(text(pad, mid + 5, name, 14, TEXT, "start"))
        if r < 2:  # buses: hexágonos con el valor dentro, como en GTKWave
            for t0, t1, v in (bcd if r == 0 else sseg):
                a, b, s = X(t0), X(t1), 4
                out.append(f'<polygon points="{a},{mid} {a + s},{hi} {b - s},{hi} {b},{mid} {b - s},{lo} {a + s},{lo}" '
                           f'fill="none" stroke="{TRACE}" stroke-width="1.5"/>')
                label = str(v) if r == 0 else f"{v:07b}"
                out.append(text((a + b) / 2, mid + 4, label, 12 if r == 0 else 9.5, TEXT))
        else:      # un bit por segmento: a = sseg[6] ... g = sseg[0]
            bit = 6 - (r - 2)
            pts = []
            for t0, t1, v in sseg:
                yv = hi if v >> bit & 1 else lo
                pts += [(X(t0), yv), (X(t1), yv)]
            out.append(f'<polyline points="{" ".join(f"{px:g},{py:g}" for px, py in pts)}" '
                       f'fill="none" stroke="{TRACE}" stroke-width="1.8"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    (ROOT / "img").mkdir(exist_ok=True)
    table = read_table(ROOT / "tabla.txt")
    (ROOT / "img" / "patrones.svg").write_text(patterns_svg(table), encoding="utf-8", newline="\n")
    signals, end = parse_vcd(ROOT / "simulacion" / "sevensegdec_tb.vcd")
    (ROOT / "img" / "ondas_vcd.svg").write_text(waves_svg(signals, end), encoding="utf-8", newline="\n")
    print("Figuras generadas en img/")


if __name__ == "__main__":
    main()
