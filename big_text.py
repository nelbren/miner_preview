#!/usr/bin/python3
""" big_text.py - show custom big numbers
    v0.0.3 - 2021-11-06 - nelbren@nelbren.com"""
from rich.console import Console

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
    [2, 1, 1, 1, 1, 2, 0, 0],
    [1, 3, 0, 0, 3, 1, 0, 0],
    [0, 0, 0, 0, 2, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 3, 1, 0, 0],
    [1, 2, 0, 0, 2, 1, 0, 0],
    [3, 1, 1, 1, 1, 3, 0, 0],
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
}


def big_text(console, text, color):
    """Show big text"""
    style1 = f"[black on {color}]"
    style2 = f"[{color} on black]"
    for row in range(8):
        for char in text:
            for index, j in enumerate(numbers[char][row]):
                if j == 1:
                    draw = "█"
                elif j == 2:
                    draw = "▄"
                elif j == 3:
                    draw = "▀"
                else:
                    draw = " "
                if char in ["^", "v", "=", "B", "E"]:
                    style = style1
                    if index == 0:
                        console.print(f"{style2} ", end="")
                        console.print(f"{style} ", end="")
                elif char == "$":
                    style = style2
                    if index == 0:
                        console.print(f"{style} ", end="")
                else:
                    style = style2
                console.print(f"{style}{draw}", end="")
        console.print()


def big_line(console, text, color):
    """Show big line"""
    style1 = f"[black on {color}]"
    style2 = f"[{color} on black]"
    for char in text:
        line = " " * 8
        if char in ["^", "v", "=", "B", "E"]:
            style = style1
            console.print(f"{style2} ", end="")
            console.print(f"{style} ", end="")
        elif char == "$":
            style = style2
            console.print(f"{style} ", end="")
        else:
            style = style2
        console.print(f"{style}{line}", end="")
    console.print()


def show_big(usd, tags, colors):
    """Show big numbers"""
    console = Console(record=True)
    color0 = colors["normal"]

    if "usd_ethermine" in usd:
        tag1 = tags["usd_ethermine"]
        color1 = colors["usd_ethermine"]
        n1_formated = f"{tag1}${usd['usd_ethermine']:7.2f}"
        big_line(console, n1_formated, color0)
        big_line(console, n1_formated, color1)
        big_text(console, n1_formated, color1)
    else:
        n1_formated = ""

    if "usd_cloudatcost" in usd:
        tag2 = tags["usd_cloudatcost"]
        color2 = colors["usd_cloudatcost"]
        n2_formated = f"{tag2}${usd['usd_cloudatcost']:7.2f}"
        big_line(console, n2_formated, color0)
        big_line(console, n2_formated, color2)
        big_text(console, n2_formated, color2)
        big_line(console, n2_formated, color0)
    else:
        n2_formated = ""

    return console, [n1_formated, n2_formated]


if __name__ == "__main__":
    from random import randint

    _usd = {}
    _usd["usd_ethermine"] = 10.97
    _usd["usd_cloudatcost"] = 140.99
    _tags = {"usd_cloudatcost": "^"}
    _colors = {"normal": "black", "usd_cloudatcost": "green"}
    if randint(0, 1):
        _tags["usd_ethermine"] = "="
        _colors["usd_ethermine"] = "white"
    else:
        _tags["usd_ethermine"] = "v"
        _colors["usd_ethermine"] = "red"
    _console, _numbers = show_big(_usd, _tags, _colors)
    # print(_numbers)
