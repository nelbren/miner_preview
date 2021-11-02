#!/usr/bin/python3
""" deltas_and_tags.py - set deltas and tags
    v0.0.3 - 2021-11-02 - nelbren@nelbren.com"""

from datetime import datetime, timedelta
from config import get_config

TS_FMT = "%Y-%m-%d %H:%M:%S"
SOURCE = "cloudatcost"


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
    if value1 in [0, value2]:
        color, label = "white", "="
    elif value1 > value2:
        color, label = "green", "^"
    else:
        color, label = "red", "v"
    return f"[black on {color}]{label}[{color} on black]"


def tags_row(tag, last_unpaid, unpaid, last_delta, delta):
    """Set tag colors to row"""
    tag["date"] = "[black on white]"
    # if delta[SOURCE] == unpaid.id:
    #    tag["time"] = "[black on yellow]"
    # else:
    #    tag["time"] = "[white on black]"
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
    tag["goal_pm"] = goal_pm
    goal_msg = (
        f"🎯{tag['pm']}{goal_pm:06.2f}%{label}"
        f"{tag['title']}[{progress_bar}{tag['title']}]"
    )
    return goal_msg


def get_goals(miner):
    """Get goals from config"""
    cfg = get_config()
    if miner == "cloudatcost":
        return cfg["cac_goal_usd"], cfg["cac_goal_btc"]
    return cfg["etm_goal_usd"], cfg["etm_goal_btc"]


def get_goal_msg(source, currency, tag, unpaid, size_term):
    """Goal Message"""
    goal_usd, goal_val = get_goals(source)
    if not goal_usd and not goal_val:
        return ""

    rest_cols = size_term["columns"] - 37
    items = 0
    if goal_usd:
        items += 1
    if goal_val:
        items += 1
    items_cols = int(rest_cols / items)
    goal_msg_detail = get_goal_msg_item(
        tag, "USD", goal_usd, unpaid.usd, items_cols
    )
    tag[f"{source}_goal_pm_usd"] = tag["goal_pm"]
    goal_msg_detail += get_goal_msg_item(
        tag, currency.upper(), goal_val, unpaid.value, items_cols
    )
    tag[f"{source}_goal_pm_val"] = tag["goal_pm"]
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
