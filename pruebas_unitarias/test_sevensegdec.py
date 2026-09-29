# -*- coding: utf-8 -*-
"""
Pruebas unitarias (pytest) del decodificador de 7 segmentos.

Reemplazan el chequeo ad-hoc del testbench original. Ejecutar desde la raíz del repositorio:

    python -m pytest -v pruebas_unitarias
"""

from pathlib import Path

import pytest

import sevensegdec_mod as ssd

TABLE_FILE = Path(__file__).resolve().parent.parent / "tabla.txt"

# Especificación escrita a mano, independiente de tabla.txt: valor -> (nombre, segmentos encendidos).
# Así las pruebas detectan errores de digitación en la tabla, cosa que el testbench original no
# podía hacer porque comparaba la salida contra la misma tabla que usaba el decodificador.
SPEC = {
    0: ("0", "abcdef"),
    1: ("1", "bc"),          # 1 a la derecha
    2: ("2", "abdeg"),
    3: ("3", "abcdg"),
    4: ("4", "bcfg"),
    5: ("5", "acdfg"),
    6: ("6", "acdefg"),      # 6 cerrado: enciende a
    7: ("7", "abc"),
    8: ("8", "abcdefg"),
    9: ("9", "abcdfg"),      # 9 cerrado: enciende d
    10: ("NOT", "cg"),       # ¬  negación
    11: ("AND", "abcef"),    # ∩  intersección / conjunción
    12: ("OR", "bcdef"),     # ∪  unión / disyunción
    13: ("nivel0", "d"),     # _  nivel lógico bajo
    14: ("nivelZ", "g"),     # −  alta impedancia
    15: ("nivel1", "a"),     # ‾  nivel lógico alto
}

CASES = [
    pytest.param(value, ssd.segments_to_bits(segments), id=f"{value:02d}-{name}")
    for value, (name, segments) in SPEC.items()
]

# Letras hexadecimales usadas en las diapositivas del curso (prohibidas para 10-15)
HEX_LETTERS = {"A": "abcefg", "b": "cdefg", "C": "adef", "c": "deg", "d": "bcdeg", "E": "adefg", "F": "aefg"}


@pytest.fixture(scope="module")
def table():
    return ssd.read_table(TABLE_FILE)


# 1. Los 16 casos: la tabla, la salida del decodificador y la salida invertida

@pytest.mark.parametrize("value, expected", CASES)
def test_table_file_matches_spec(table, value, expected):
    assert table[value] == expected, f"tabla.txt, valor {value}: {table[value]:07b} != {expected:07b}"


@pytest.mark.parametrize("value, expected", CASES)
def test_decoder_output(table, value, expected):
    assert ssd.simulate(table, value) == expected


@pytest.mark.parametrize("value, expected", CASES)
def test_decoder_inverted_output(table, value, expected):
    # Con invert=True cada segmento se complementa (display de ánodo común, activo en bajo)
    assert ssd.simulate(table, value, invert=True) == expected ^ 0b1111111


# 2. Reglas de diseño del taller

def test_one_is_drawn_on_the_right(table):
    assert table[1] == ssd.segments_to_bits("bc")


def test_six_and_nine_are_closed(table):
    assert table[6] & ssd.segments_to_bits("a"), "el 6 cerrado debe encender el segmento a"
    assert table[9] & ssd.segments_to_bits("d"), "el 9 cerrado debe encender el segmento d"


def test_all_patterns_are_different(table):
    assert len(set(table)) == ssd.N_ENTRIES


@pytest.mark.parametrize("letter, segments", HEX_LETTERS.items())
def test_symbols_10_15_are_not_hex_letters(table, letter, segments):
    assert ssd.segments_to_bits(segments) not in table[10:], f"un símbolo 10-15 repite la letra {letter}"


# 3. Lectura de la tabla

@pytest.mark.parametrize("content, message", [
    pytest.param("1111110\n" * 15, "16 lineas", id="15-lineas"),
    pytest.param("1111110\n" * 17, "16 lineas", id="17-lineas"),
    pytest.param("1111110\n" * 15 + "111111\n", "7 bits", id="6-bits"),
    pytest.param("1111110\n" * 15 + "11111102\n", "7 bits", id="8-caracteres"),
    pytest.param("1111110\n" * 15 + "abcdefg\n", "7 bits", id="no-binario"),
])
def test_read_table_rejects_bad_files(tmp_path, content, message):
    bad = tmp_path / "bad.txt"
    bad.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        ssd.read_table(bad)


def test_read_table_ignores_blank_lines(tmp_path, table):
    # En el script original una línea en blanco al final convertía toda la tabla en ceros
    padded = tmp_path / "padded.txt"
    padded.write_text("\n" + TABLE_FILE.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    assert ssd.read_table(padded) == table


# 4. Conversión a HDL

@pytest.mark.parametrize("hdl, filename, literal", [
    pytest.param("VHDL", "sevensegdec_nexys.vhd", lambda p: f'"{p:07b}"', id="VHDL"),
    pytest.param("Verilog", "sevensegdec_nexys.v", lambda p: f"= {p};", id="Verilog"),
])
def test_hdl_conversion_contains_every_pattern(table, tmp_path, hdl, filename, literal):
    ssd.convert(table, hdl, tmp_path)
    code = (tmp_path / filename).read_text()
    assert "case" in code
    for pattern in table:
        assert literal(pattern) in code
