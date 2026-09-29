#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seven segment decoder (versión modificada del script del curso sevensegdec.py).

Cambios respecto al original:
  * Este módulo contiene solo la LÓGICA: los bloques MyHDL, la lectura de la
    tabla, una función para simular una entrada y la conversión a HDL.
    Las pruebas están en test_sevensegdec.py y se ejecutan con pytest.
  * El testbench ad-hoc (comparar y hacer print("ERROR ...")) se reemplazó por
    un estímulo que solo recorre los 16 valores para generar el VCD.
  * read_table valida el archivo (16 líneas de 7 bits) y lanza ValueError, en
    vez de devolver en silencio una tabla de ceros cuando algo falla.
"""

import argparse
from pathlib import Path

from myhdl import Signal, always_comb, block, delay, instance, instances, intbv, now

SEGMENTS = "abcdefg"  # a es el bit 6 (MSB), g es el bit 0 (LSB)
N_ENTRIES = 16        # 4 bits de entrada

# implementation

@block
def sevensegdec(bcd, sseg, decod_table, invert=False):
    """Seven segment decoder"""

    # internal signal for optional bit inversion
    ssegout = Signal(intbv(0)[7:])

    @always_comb
    def logic():
        """LUT implementation: based on a decoder table"""
        ssegout.next = decod_table[int(bcd)]

    @always_comb
    def invertproc():
        """Inverting process for output"""
        if invert:
            sseg.next = ~ssegout
        else:
            sseg.next = ssegout

    # this will include logic and invertproc
    return instances()

@block
def sevensegdec_nexys(bcd, sseg, bcdled, ssanodes, decod_table, invert=False):
    """Envelope for running a demo in the Nexys4 DDR board for the Seven segment decoder"""

    # Main decoder instance
    ssdec = sevensegdec(bcd, sseg, decod_table, invert)

    @always_comb
    def logic():
        """Process to fill the LEDs for switches and display anodes"""
        bcdled.next = bcd
        ssanodes.next = intbv(0xfe)[8:] # only turn on first display, it is turned on with 0.

    # this will include ssdec and logic
    return instances()

# simulation helpers (sin verificación: las comprobaciones están en test_sevensegdec.py)

@block
def sevensegdec_probe(decod_table, value, result, invert=False):
    """Aplica una sola entrada al decodificador y guarda la salida en result["sseg"]"""

    bcd = Signal(intbv(0)[4:])
    sseg = Signal(intbv(0)[7:])

    uut = sevensegdec(bcd, sseg, decod_table, invert)

    @instance
    def stimulus():
        bcd.next = value
        yield delay(10)
        result["sseg"] = int(sseg.val)

    return instances()

@block
def sevensegdec_stim(decod_table, invert=False, verbose=True):
    """Estímulo: recorre las 16 entradas (10 ns cada una) para generar el VCD"""

    bcd_tb = Signal(intbv(0)[4:])
    sseg_tb = Signal(intbv(0)[7:])

    uut = sevensegdec(bcd_tb, sseg_tb, decod_table, invert)

    @instance
    def stimulus():
        for bcd_in in range(len(decod_table)):
            bcd_tb.next = bcd_in
            yield delay(10)
            if verbose:
                print(f"t={now():3d} ns  bcd={bcd_in:2d} ({bcd_in:04b})  sseg(abcdefg)={int(sseg_tb.val):07b}")

    return instances()

def simulate(decod_table: tuple, value: int, invert: bool = False) -> int:
    """Simula el decodificador para una entrada y devuelve el valor de sseg"""
    result = {}
    sim = sevensegdec_probe(decod_table, value, result, invert)
    sim.run_sim(quiet=1)
    sim.quit_sim()
    return result["sseg"]

# table and conversion

def segments_to_bits(segments: str) -> int:
    """Convierte segmentos encendidos a bits: "bc" -> 0b0110000"""
    return sum(1 << (len(SEGMENTS) - 1 - SEGMENTS.index(s)) for s in segments)

def read_table(table_file) -> tuple:
    """Read the decoder table from text file:
        * Each line contains a string with 0s and 1s, in order "abcdefg"
        * It must contain 16 lines, one for each 4-bit digit
        * Blank lines are ignored; any other problem raises ValueError
    """
    lines = Path(table_file).read_text(encoding="utf-8").splitlines()
    rows = [line.strip() for line in lines if line.strip()]
    if len(rows) != N_ENTRIES:
        raise ValueError(f"{table_file}: se esperaban {N_ENTRIES} lineas con datos, hay {len(rows)}")
    for value, row in enumerate(rows):
        if len(row) != len(SEGMENTS) or set(row) - {"0", "1"}:
            raise ValueError(f"{table_file}: el valor {value} ('{row}') no son 7 bits en orden abcdefg")
    return tuple(int(row, base=2) for row in rows)

def convert(decod_table: tuple, hdl: str = "VHDL", path="") -> None:
    """Genera el HDL de sevensegdec_nexys en la carpeta path (por defecto, la actual)"""
    ss_sig = {
        "bcd": Signal(intbv(0)[4:]),
        "sseg": Signal(intbv(0)[7:]),
        "bcdled": Signal(intbv(0)[4:]),
        "ssanodes": Signal(intbv(0)[8:]),
        "invert": Signal(False),
        "decod_table": decod_table
        }
    sevensegdec_nexys(**ss_sig).convert(hdl=hdl, path=str(path))

def run():
    """Entrypoint"""
    parser = argparse.ArgumentParser(description="Seven segment decoder (versión con pruebas en pytest)")
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Recorre los 16 valores y genera el VCD (la verificación se hace con pytest)",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert the outputs (simulation only)",
    )
    parser.add_argument(
        "--verilog",
        action="store_true",
        help="Convert to verilog instead of VHDL",
    )
    parser.add_argument(
        "--table",
        type=str,
        required=True,
        help="Decoder table to include")
    args = parser.parse_args()

    try:
        table = read_table(args.table)
    except (OSError, ValueError) as ex:
        parser.error(str(ex))

    if args.simulation:
        tb = sevensegdec_stim(table, args.invert)
        tb.config_sim(trace=True)
        tb.run_sim(quiet=1)
        tb.quit_sim()
        print("Simulation done.")

    langout = "Verilog" if args.verilog else "VHDL"
    convert(table, langout)
    print(f"Conversion done ({langout}).")

if __name__ == "__main__":
    run()
