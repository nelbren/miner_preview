#!/usr/bin/python3
""" preview.py - show information from CAC
    v0.1.8 - 2021-10-27 - nelbren@nelbren.com"""
import os
import re
import sys
import time
import shutil
import configparser
import argparse
from datetime import datetime, timedelta
import imgkit
from rich import box
from rich.table import Table
from rich.console import Console
from rich.progress import (
    BarColumn,
    SpinnerColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
import peewee
import minercac
from database import db, Unpaid

TS_FMT = "%Y-%m-%d %H:%M:%S"
SOURCE = "cloudatcost"
CURRENCY = "btc"
unpaid_save = {}
next_update = {}


def setup_db():
    """Setup"""
    models = [Unpaid]
    db.connect()
    db.create_tables(models)


def setup_jpg(save):
    """Setup JPG"""
    save_html2 = os.path.splitext(save)[0] + "_temp.html"
    shutil.copyfile(save, save_html2)
    with open(save_html2, "r+") as _file:
        text = _file.read()
        text = re.sub("⛏️", "&nbsp;", text)
        text = re.sub("🎯", "&nbsp;&nbsp;", text)
        _file.seek(0)
        _file.write(text)
        _file.truncate()
    options = {"encoding": "latin_1", "quiet": ""}
    save_img = os.path.splitext(save)[0] + ".jpg"
    imgkit.from_file(save_html2, save_img, options=options)
    os.unlink(save_html2)


def setup_html(save):
    """Setup HTML"""
    with open(save, "r+") as _file:
        text = _file.read()
        pre = "pre { color: #ffffff; background-color: #000000; font-size: 41px; }"
        text = re.sub("</style>", f"{pre}\n</style>", text)
        _file.seek(0)
        _file.write(text)
        _file.truncate()
    setup_jpg(save)


def params():
    """Set params"""
    parser = argparse.ArgumentParser(
        description="Get wallet balance from Cloudatcost mining process."
    )
    parser.add_argument(
        "-r",
        "--records",
        type=int,
        required=False,
        default=-1,
        help="The number of last records to get (0 = All)",
    )
    parser.add_argument(
        "-s",
        "--save",
        required=False,
        default="",
        help="HTML and JPG file to save the output",
    )
    parser.add_argument(
        "-ou",
        "--only_update",
        action="store_true",
        default=False,
        dest="update",
        help="Only update database (useful with crontab)",
    )
    args = parser.parse_args()
    return args.update, args.records, args.save


def get_goals():
    """Get goals from config"""
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    filename = ".secret.cfg"
    minercac.check_config(path, filename)
    config.read_file(open(path + "/" + filename))
    goal_usd = config.get("CAC_WALLET", "GOAL_USD", fallback=None)
    goal_btc = config.get("CAC_WALLET", "GOAL_BTC", fallback=None)
    return goal_usd, goal_btc


def get_columns_and_lines():
    """Get size of terminal"""
    try:
        columns, lines = os.get_terminal_size()
    # pylint: disable=unused-variable
    except OSError as exception:
        columns, lines = 80, 24  # Default
    return {"columns": columns, "lines": lines}


def add_columns(table):
    """'Header"""
    table.add_column(
        "ts", justify="center", style="white", no_wrap=True, max_width=10
    )
    table.add_column(
        "±ts", justify="right", style="magenta", no_wrap=True, max_width=8
    )
    table.add_column("value", justify="right", style="green", no_wrap=True)
    table.add_column("±value", justify="right", style="magenta", no_wrap=True)
    table.add_column("±(±val)", justify="right", style="magenta", no_wrap=True)
    table.add_column("usd", justify="right", style="green", no_wrap=True)
    table.add_column("±usd", justify="right", style="magenta", no_wrap=True)


def ts_to_int(timediff):
    """Timestamp to int"""
    ts_str = str(timediff)
    if isinstance(timediff, timedelta):
        if timediff.days > 0:
            ts_str = ts_str.replace(" days, ", ":")
        pos_seconds = ts_str.rfind(":")
        ts_str = ts_str[:pos_seconds]
        ts_str = ts_str.replace(":", "")
    return int(ts_str)


def set_tag_delta(value1, value2, color):
    """Set tag delta"""
    if value1 == value2:
        return "[black on white]=[white on black]"
    if value1 > value2:
        return "[black on green]^[green on black]"
    return f"[black on {color}]v[{color} on black]"


def set_option_value(value1, value2):
    """Set tag value"""
    if value1 == 0:
        color, label = "white", "="
    elif value1 > value2:
        color, label = "green", "^"
    else:
        color, label = "red", "v"
    return f"[black on {color}]{label}[{color} on black]"


def tags_row(tag, last_unpaid, unpaid, last_delta, delta):
    """Set tag colors to row"""
    tag["date"] = "[black on white]"
    if unpaid_save[SOURCE] == unpaid.id:
        tag["time"] = "[black on yellow]"
    else:
        tag["time"] = "[white on black]"

    if ts_to_int(last_delta["timestamp"]) == 0:
        if ts_to_int(delta["timestamp"]) == 0:
            color, label = "white", "="
        else:
            color, label = "green", "^"
    elif ts_to_int(delta["timestamp"]) == ts_to_int(last_delta["timestamp"]):
        color, label = "white", "="
    elif ts_to_int(delta["timestamp"]) > ts_to_int(last_delta["timestamp"]):
        color, label = "green", "^"
    else:
        color, label = "yellow", "v"
    tag["±timestamp"] = f"[black on {color}]{label}[{color} on black]"

    if last_unpaid is None:
        last_value, last_usd = 0, 0
    else:
        last_value, last_usd = last_unpaid.value, last_unpaid.usd
    tag["value"] = set_option_value(unpaid.value, last_value)
    tag["±value"] = set_tag_delta(delta["±value"], last_delta["±value"], "red")
    tag["usd"] = set_option_value(unpaid.usd, last_usd)
    tag["±usd"] = set_tag_delta(delta["±usd"], last_delta["±usd"], "cyan")


def tags_title(tag, last_unpaid, timestamp):
    """Set tag colors to title"""
    diff_ts_now = datetime.strptime(timestamp, TS_FMT) - datetime.strptime(
        last_unpaid.timestamp, TS_FMT
    )
    tag["style"] = "black on "
    if diff_ts_now > timedelta(hours=4):
        color, tag["ok"] = "red", "✖"
    else:
        color, tag["ok"] = "green", "✔"
    tag["style"] += color
    tag["title"] = f"[{tag['style']}][not bold]"


def tag_pm(tag, goal_pm):
    """Set tag colors to pm"""
    tag["pm"] = "[bold]"
    if goal_pm > 75:
        tag["pm"] += "[white]"
    elif goal_pm > 50:
        tag["pm"] += "[cyan]"
    elif goal_pm > 25:
        tag["pm"] += "[yellow]"
    else:
        tag["pm"] += "[white]"


def get_goal_msg_item(tag, label, goal, value, item_cols):
    """Goal USD"""
    if not goal:
        return ""
    if item_cols < 5:
        return ""
    bars = item_cols - 10  # 051.03%USD
    goal_pm = round((float(value) / float(goal)) * 100, 2)
    show_bars = int((goal_pm / 100) * bars)
    if show_bars >= bars:
        show_bars = bars
        rest_bars = 0
        missing = ""
    else:
        rest_bars = bars - show_bars
        missing = "[not bold][red]" + rest_bars * "■"
    progress = "[bold][white]" + show_bars * "■"
    progress_bar = f"{progress}{missing}"
    tag_pm(tag, goal_pm)
    goal_msg = (
        f"🎯{tag['pm']}{goal_pm:06.2f}%{label}"
        f"{tag['title']}[{progress_bar}{tag['title']}]"
    )
    return goal_msg


def get_goal_msg(tag, unpaid, size_term):
    """Goal Message"""
    goal_usd, goal_btc = get_goals()
    if not goal_usd and not goal_btc:
        return ""

    rest_cols = size_term["columns"] - 37
    items = 0
    if goal_usd:
        items += 1
    if goal_btc:
        items += 1
    items_cols = int(rest_cols / items)
    goal_msg_detail = get_goal_msg_item(
        tag, "USD", goal_usd, unpaid.usd, items_cols
    )
    goal_msg_detail += get_goal_msg_item(
        tag, "BTC", goal_btc, unpaid.value, items_cols
    )
    return f"|{goal_msg_detail} "


def set_deltas_empty(unpaid, delta):
    """Delta empty"""
    delta["timestamp"] = "0"
    delta["date"], delta["time"] = unpaid.timestamp.split(" ")
    delta["±value"] = delta["±±value"] = 0
    delta["±usd"] = delta["±usd_sum"] = 0
    delta["btc_diff"] = delta["usd_diff"] = 0
    delta["~value"] = delta["~count"] = 0
    delta["ts_short"] = "00:00"


def set_deltas(last_unpaid, unpaid, last_delta, delta):
    """Delta"""
    delta["timestamp"] = datetime.strptime(
        unpaid.timestamp, TS_FMT
    ) - datetime.strptime(last_unpaid.timestamp, TS_FMT)
    if delta["timestamp"] != "0":
        ts_str = str(delta["timestamp"])
        if delta["timestamp"].days > 0:
            ts_str = ts_str.replace(" days, ", ":")
        ts_lst = ts_str.split(":")
        if len(ts_lst) > 3:
            delta["ts_short"] = ts_lst[0] + ":" + ts_lst[1] + ":" + ts_lst[2]
        else:
            delta["ts_short"] = ts_lst[0] + ":" + ts_lst[1]
    delta["date"], delta["time"] = unpaid.timestamp.split(" ")
    delta["±value"] = unpaid.value - last_unpaid.value
    delta["~value"] += delta["±value"]
    delta["~count"] += 1
    delta["±±value"] = (
        delta["±value"] * 100000000 - last_delta["±value"] * 100000000
    )
    delta["±usd"] = unpaid.usd - last_unpaid.usd
    delta["±usd_sum"] += delta["±usd"]
    if unpaid.timestamp[:10] != last_unpaid.timestamp[:10]:
        delta["btc_diff"] = unpaid.value - delta["btc_first"]
        delta["usd_diff"] = unpaid.usd - delta["usd_first"]


def get_records(records):
    """Get records and recalculate number of records"""
    try:
        if records == 0:
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == SOURCE) & (Unpaid.currency == CURRENCY)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
            )
        else:
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == SOURCE) & (Unpaid.currency == CURRENCY)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
                .limit(records)
            )
            last_unpaid = None
            item = 0
            for unpaid in reversed(unpaids):
                if (
                    last_unpaid is None
                    or unpaid.timestamp[:10] != last_unpaid.timestamp[:10]
                ):
                    last_unpaid = unpaid
                    item += 1
            records -= item + 1  # Extra line of sumary
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == SOURCE) & (Unpaid.currency == CURRENCY)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
                .limit(records)
            )

    except peewee.DoesNotExist:
        print("do-something")
    return records, unpaids


def add_row_date(table, delta):
    """Row date"""
    cols = [7, 11, 11, 8, 7, 6]
    label = "─"
    color1 = "[black on white]"
    color2 = "[white on black]"
    if delta["~count"]:
        delta["~value"] /= delta["~count"]
    table.add_row(
        f"{color1}{delta['date']}",
        f"{color2}{cols[0] * label}",
        f"{color1}{delta['btc_diff']:01.8f}",
        f"{color1}~{delta['~value']:01.8f}",
        f"{color2}{cols[3] * label}",
        f"{color1}{delta['usd_diff']:05.2f}",
        f"{color2}{cols[5] * label}",
    )


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


def show_data(records, save, size_term):
    """Show time"""
    timestamp = datetime.now().strftime(TS_FMT)
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
    tag = {}
    if records == -1:
        records = size_term["lines"] - 4  # 3 Lines of header + 1 of Footer
    lines_show = records
    if lines_show < 3 and records:
        print("Too small to show")
        sys.exit(0)
    tag["currency"] = "[cyan]"
    records, unpaids = get_records(records)
    last_unpaid = None
    item = 0
    delta = last_delta = {}
    for unpaid in reversed(unpaids):
        item += 1
        if last_unpaid is None:
            set_deltas_empty(unpaid, delta)
            last_delta = delta.copy()
        else:
            last_delta = delta.copy()
            set_deltas(last_unpaid, unpaid, last_delta, delta)
        tags_row(tag, last_unpaid, unpaid, last_delta, delta)
        if last_delta["date"] != delta["date"] or item == 1:
            set_and_and_row_date(table, last_unpaid, unpaid, delta)
            lines_show -= 1
        add_row(table, tag, delta, unpaid)
        lines_show -= 1
        if item == unpaids.count():
            timestamp_obj = datetime.strptime(unpaid.timestamp, TS_FMT)
            next_update["timestamp"] = timestamp_obj + timedelta(hours=4)
            next_update["timestamp"] = next_update["timestamp"].replace(
                minute=1, second=0
            )
        last_unpaid = unpaid
    add_last_row(table, delta, last_unpaid)
    lines_show -= 1
    print(chr(27) + "[2J")
    console = Console(record=True)
    # tags_title(tag, diff_ts_now)
    tags_title(tag, last_unpaid, timestamp)
    console.print(
        f"{tag['title']} ⛏️ BTC@"
        f"[bold white]{timestamp}[not bold black] "
        f"{tag['ok']}{get_goal_msg(tag, last_unpaid, size_term)}",
        style=tag["style"],
        justify="center",
    )
    console.print(table)
    if records != 0:
        while lines_show > 0:
            lines_show -= 1
            console.print("")
    next_update["missing"] = next_update["timestamp"] - datetime.now()
    if save:
        console.save_html(save)
        setup_html(save)
    return next_update["missing"].total_seconds()


def show_progress(seconds):
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


def save_data(value, usd):
    """Save record"""
    try:
        unpaid = (
            Unpaid.select()
            .where((Unpaid.source == SOURCE) & (Unpaid.currency == CURRENCY))
            .order_by(Unpaid.work.desc(), Unpaid.step.desc())
            .get()
        )
    except peewee.DoesNotExist:
        last_value, work, step = 0, 1, 1
    else:
        last_value, work, step = unpaid.value, unpaid.work, unpaid.step + 1
        timestamp = unpaid.timestamp

    if last_value != value:
        timestamp = f"{datetime.now()}"
        timestamp_obj = datetime.strptime(timestamp, TS_FMT + ".%f")
        timestamp = timestamp_obj.strftime(TS_FMT)
        unpaid = Unpaid(
            source=SOURCE,
            currency=CURRENCY,
            work=work,
            step=step,
            timestamp=timestamp,
            value=value,
            usd=usd,
        )
        unpaid.save()
        # pylint: disable=no-member
        unpaid_save[SOURCE] = unpaid.id
    else:
        unpaid_save[SOURCE] = 0


def get_data():
    """Get data from miner"""
    cacpanel = minercac.CACPanel()
    btc, usd = cacpanel.wallet()
    save_data(btc, usd)


def do_loop():
    """Eternal Loop 4 forever & ever"""
    setup_db()
    size_term = get_columns_and_lines()
    only_update, records, save = params()
    while True:
        get_data()
        if only_update:
            timestamp = datetime.now().strftime(TS_FMT)
            id_save = unpaid_save[SOURCE]
            print(f"{timestamp} => {id_save}")
            return
        seconds = show_data(records, save, size_term)
        if records == 0 or save:
            return
        try:
            show_progress(seconds)
        except KeyboardInterrupt:
            sys.exit(0)


do_loop()
