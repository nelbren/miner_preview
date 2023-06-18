#!/usr/bin/python3
""" big_text.py - show custom big numbers
    v0.1.3 - 2023-06-18 - nelbren@nelbren.com"""
import sys
from random import randint
from rich.console import Console
from table import get_columns_and_lines


no0 = [
    [2, 1, 1, 1, 1, 2, 0, 0],
    [1, 3, 0, 0, 2, 1, 0, 0],
    [1, 0, 0, 2, 1, 1, 0, 0],
    [1, 0, 2, 1, 3, 1, 0, 0],
    [1, 2, 1, 3, 0, 1, 0, 0],
    [1, 1, 0, 0, 2, 1, 0, 0],
    [3, 1, 1, 1, 1, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no0 = [
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 2, 1, 1, 0],
    [1, 0, 0, 2, 1, 0, 1, 0],
    [1, 0, 2, 1, 0, 0, 1, 0],
    [1, 2, 1, 0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no1 = [
    [0, 0, 2, 1, 0, 0, 0, 0],
    [2, 1, 3, 1, 0, 0, 0, 0],
    [3, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no2 = [
    [2, 1, 1, 1, 1, 2, 0, 0],
    [1, 3, 0, 0, 3, 1, 0, 0],
    [0, 0, 0, 0, 2, 1, 0, 0],
    [2, 1, 1, 1, 1, 3, 0, 0],
    [1, 3, 0, 0, 0, 0, 0, 0],
    [1, 2, 0, 0, 0, 2, 0, 0],
    [1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no3 = [
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [0, 0, 0, 0, 0, 2, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no4 = [
    [0, 0, 0, 0, 2, 1, 0, 0],
    [0, 0, 2, 1, 3, 1, 0, 0],
    [2, 1, 3, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no5 = [
    [1, 1, 1, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 3, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 2, 0],
    [0, 0, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no6 = [
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 2, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no7 = [
    [1, 1, 1, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 2, 1, 0],
    [0, 0, 0, 0, 2, 1, 3, 0],
    [0, 0, 0, 2, 1, 3, 0, 0],
    [0, 0, 0, 1, 3, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no8 = [
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [0, 1, 1, 1, 1, 1, 0, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
no9 = [
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 3, 0, 0, 0, 3, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 2, 0, 0, 0, 2, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
dot = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 1, 1, 2, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 3, 1, 1, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
spc = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
dol = [
    [0, 0, 0, 1, 0, 0, 0, 0],
    [2, 1, 1, 1, 1, 1, 2, 0],
    [1, 0, 0, 1, 0, 0, 3, 0],
    [3, 1, 1, 1, 1, 1, 2, 0],
    [2, 0, 0, 1, 0, 0, 1, 0],
    [3, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
up = [
    [0, 0, 2, 1, 2, 0, 0, 0],
    [2, 1, 3, 1, 3, 1, 2, 0],
    [3, 0, 0, 1, 0, 0, 3, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
dn = [
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [2, 0, 0, 1, 0, 0, 2, 0],
    [3, 1, 2, 1, 2, 1, 3, 0],
    [0, 0, 3, 1, 3, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
eq = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
btc = [
    [0, 0, 1, 0, 1, 0, 0, 0],
    [3, 1, 1, 1, 1, 1, 2, 0],
    [0, 1, 0, 0, 0, 3, 1, 0],
    [0, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 2, 1, 0],
    [2, 1, 1, 1, 1, 1, 3, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
eth = [
    [0, 0, 2, 1, 2, 0, 0, 0],
    [0, 2, 1, 3, 1, 2, 0, 0],
    [2, 1, 3, 0, 3, 1, 2, 0],
    [3, 2, 2, 2, 2, 2, 3, 0],
    [2, 0, 3, 3, 3, 0, 2, 0],
    [0, 3, 1, 0, 1, 3, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
cct = [
    [0, 0, 1, 0, 0, 1, 0, 0],
    [0, 2, 1, 1, 1, 1, 2, 0],
    [0, 1, 3, 0, 0, 3, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 2, 0, 0, 2, 1, 0],
    [0, 3, 1, 1, 1, 1, 3, 0],
    [0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

numbers = {
    "0": no0,
    "1": no1,
    "2": no2,
    "3": no3,
    "4": no4,
    "5": no5,
    "6": no6,
    "7": no7,
    "8": no8,
    "9": no9,
    ".": dot,
    "$": dol,
    "^": up,
    "v": dn,
    "=": eq,
    "B": btc,
    "E": eth,
    " ": spc,
    "C": cct,
}


def big_text(console, text, color, scale = [1, 1]):
    """Show big text"""
    style1 = f"[black on {color}]"
    style2 = f"[{color} on black]"
    draws = [" ", "█", "▄", "▀"]
    for row in range(8):
        for i in range(scale[1]):
            for char in text:
                for index, j in enumerate(numbers[char][row]):
                    draw = draws[j]*scale[0]
                    if char in ["^", "v", "="]:
                        style = style1
                        if index == 0:
                            console.print(f"{style2} ", end="")
                            console.print(f"{style} ", end="")
                    elif char in ["$", "B", "E"]:
                        style = style2
                        if index == 0:
                            console.print(f"{style} ", end="")
                    else:
                        style = style2
                    console.print(f"{style}{draw}", end="")
            console.print()


def big_line(console, text, color, scale = [1, 1]):
    """Show big line"""
    style1 = f"[black on {color}]"
    style2 = f"[{color} on black]"
    for char in text:
        line = " " * 8 * scale[0]
        if char in ["^", "v", "="]:
            style = style1
            console.print(f"{style2} ", end="")
            console.print(f"{style} ", end="")
        elif char in ["$", "B", "E"]:
            style = style2
            console.print(f"{style} ", end="")
        else:
            style = style2
        console.print(f"{style}{line}", end="")
    console.print()


def add_big_usd(console, source, usd, tags, colors, scale):
    """Add big usd"""
    usd_source = f"usd_{source}"
    tag1 = tags[usd_source]
    color0 = colors["normal"]
    color1 = colors[usd_source]
    n_formated = f"{tag1}${usd:07.2f}"
    big_line(console, n_formated, color0, scale)
    big_line(console, n_formated, color1, scale)
    big_text(console, n_formated, color1, scale)
    big_line(console, n_formated, color0, scale)
    return n_formated


def add_big_val(console, source, currency, val, tags, colors, scale):
    """Add big val"""
    val_source = f"val_{source}"
    crypto = currency[0:1]
    tag1 = tags[val_source]
    color0 = colors["normal"]
    color1 = colors[val_source]
    n_formated = f"{tag1}{crypto}{val:10.8f}"
    big_line(console, n_formated, color0, scale)
    big_line(console, n_formated, color1, scale)
    big_text(console, n_formated, color1, scale)
    big_line(console, n_formated, color0, scale)
    #big_line(console, n_formated, color0)
    return n_formated


def add_title(console, source):
    console.print(
        f"[bold black on white][not bold black] {source}",
        style="black on white",
        justify="center",
    )


def show_big(usds, cryptos, vals, tags, colors, size_term):
    """Show big numbers"""
    console = Console(record=True, width=size_term["columns"])
    numbers = {}
    scale_usd = [2, 1]
    scale_val = [1, 1]

    if "usd_ethermine" in usds:
        add_title(console, "ETHERMINE")
        format_usd = add_big_usd(
            console, "ethermine", usds["usd_ethermine"], tags, colors, scale_usd
        )
        format_val = add_big_val(
            console, "ethermine", cryptos["val_ethermine"], vals["val_ethermine"], tags, colors, scale_val
        )
        numbers["ethermine"] = {"usd": format_usd, "val": format_val}
    if "usd_cryptoatcost" in usds:
        add_title(console, "CRYPTOATCOST")
        format_usd = add_big_usd(
            console, "cryptoatcost", usds["usd_cryptoatcost"], tags, colors, scale_usd
        )
        format_val = add_big_val(
            console, "cryptoatcost", cryptos["val_cryptoatcost"], vals["val_cryptoatcost"], tags, colors, scale_val
        )
        numbers["cryptoatcost"] = {"usd": format_usd, "val": format_val}
    if "usd_nicehash" in usds:
        add_title(console, "NICEHASH")
        format_usd = add_big_usd(
            console, "nicehash", usds["usd_nicehash"], tags, colors, scale_usd
        )
        format_val = add_big_val(
            console, "nicehash", cryptos["val_nicehash"], vals["val_nicehash"], tags, colors, scale_val
        )
        numbers["nicehash"] = {"usd": format_usd, "val": format_val}
    return console, numbers


def show_big2(console, btc):
    """Show big numbers"""
    color0, color2 = "black", "white"
    n1_formated = f"{btc:10.8f}"
    # big_line(console, n1_formated, color0)
    # big_line(console, n1_formated, color2)
    big_text(console, n1_formated, color2, 1)
    big_line(console, n1_formated, color0, 1)
    return console


if __name__ == "__main__":
    _usd = {}
    _vals = {}
    if len(sys.argv) == 3:
        _usd["usd_cryptoatcost"] = float(sys.argv[1])
        _vals["val_cryptoatcost"] = float(sys.argv[2])
    else:
        _usd["usd_cryptoatcost"] = 145.99
        _vals["val_cryptoatcost"] = 167.38609324
    _size_term = get_columns_and_lines({"columns": -1})
    _cryptos = {}
    _cryptos["val_cryptoatcost"] = "C"
    _colors = {"normal": "black"}
    _tags = {}
    if randint(0, 1):
        _tags["usd_cryptoatcost"] = "^"
        _tags["val_cryptoatcost"] = "^"
        _colors["usd_cryptoatcost"] = "green"
        _colors["val_cryptoatcost"] = "green"
    else:
        _tags["usd_cryptoatcost"] = "v"
        _tags["val_cryptoatcost"] = "v"
        _colors["usd_cryptoatcost"] = "red"
        _colors["val_cryptoatcost"] = "red"
    _console, _numbers = show_big(_usd, _cryptos, _vals, _tags, _colors, _size_term)
    _btc = 0.01494931
    _btc = 167.38609324
    #show_big2(_console, _btc)
    # print(_numbers)
