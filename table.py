#!/usr/bin/python3
""" table.py - manage table
    v0.0.3 - 2022-05-14 - nelbren@nelbren.com"""
import os
import time
from rich import box
from rich.table import Table
from rich.progress import (
    BarColumn,
    SpinnerColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)


def get_columns_and_lines():
    """Get size of terminal"""
    try:
        columns, lines = os.get_terminal_size()
    # pylint: disable=unused-variable
    except OSError:
        # as exception:
        columns, lines = 80, 24  # Default
    return {"columns": columns, "lines": lines}


def add_columns(table):
    """'Header"""
    table.add_column(
        "ts", justify="center", style="white", no_wrap=True, max_width=10
    )
    table.add_column(
        "±ts", justify="right", style="magenta", no_wrap=False, max_width=8
    )
    table.add_column("value", justify="right", style="green", no_wrap=True)
    table.add_column("±value", justify="right", style="magenta", no_wrap=True)
    table.add_column(
        "±(±val)", justify="right", style="magenta", no_wrap=False
    )
    table.add_column("usd", justify="right", style="green", no_wrap=True)
    table.add_column("±usd", justify="right", style="magenta", no_wrap=True)


def make_table():
    """Make table"""
    table = Table(
        show_header=True,
        header_style="bold white",
        box=box.SIMPLE,
        show_edge=False,
        expand=True,
        row_styles=["bold", "none"],
        pad_edge=False,
    )
    add_columns(table)
    return table


def add_row_date(table, delta):
    """Row date"""
    cols = [7, 11, 11, 8, 7, 6]
    label = "─"
    color1 = "[black on white]"
    color2 = "[white on black]"
    if delta["~count"]:
        delta["~value"] /= delta["~count"]
    delta["±usd_diff"] = delta["usd_diff"] - delta["last_usd_diff"]
    table.add_row(
        f"{color1}{delta['date']}",
        f"{color2}{cols[0] * label}",
        f"{color1}{delta['btc_diff']:01.8f}",
        f"{color1}~{delta['~value']:01.8f}",
        f"{color2}{cols[3] * label}",
        f"{color1}{delta['usd_diff']:05.2f}",
        f"{color2}{delta['±usd_diff']:05.2f}",
    )
    delta["last_usd_diff"] = delta["usd_diff"]


def set_and_and_row_date(table, last_unpaid, unpaid, delta):
    """Set and add date"""
    delta["±usd_sum"] = 0
    if last_unpaid is None:
        delta["btc_first"], delta["usd_first"] = unpaid.value, unpaid.usd
    else:
        delta["btc_first"], delta["usd_first"] = (
            last_unpaid.value,
            last_unpaid.usd,
        )
    add_row_date(table, delta)
    delta["~count"] = 0


def add_row(table, tag, delta, unpaid):
    """Row detail"""
    table.add_row(
        f"{tag['time']}{delta['time']}",
        f"{tag['±timestamp']}{delta['ts_short']}",
        f"{tag['value']}{unpaid.value:1.8f}",
        f"{tag['±value']}{delta['±value']:1.8f}",
        f"{tag['±value']}{delta['±±value']:.0f}",
        f"{tag['usd']}{unpaid.usd:05.2f}",
        f"{tag['±usd']}{delta['±usd']:05.2f}",
    )


def add_last_row(table, delta, last_unpaid):
    """Add last summary"""
    delta["date"] = ""
    delta["btc_diff"] = last_unpaid.value - delta["btc_first"]
    delta["usd_diff"] = last_unpaid.usd - delta["usd_first"]
    delta["~count"] += 1
    add_row_date(table, delta)


def show_progress(seconds, next_update):
    """Show the progress bar"""
    with Progress(
        TextColumn(
            f"[magenta on black]Waiting "
            f"to update on [black on yellow]{next_update['timestamp']}",
            justify="right",
        ),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        SpinnerColumn(),
        TimeRemainingColumn(),
        expand=True,
    ) as progress:
        task1 = progress.add_task("waiting 4 hours", total=seconds)
        while not progress.finished:
            progress.update(task1, advance=1)
            time.sleep(1)
