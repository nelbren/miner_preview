#!/usr/bin/python3
""" preview.py - show information from cloudatcost.com and ethermine.org
    v0.1.9 - 2021-10-31 - nelbren@nelbren.com"""
import os
import re
import sys
import shutil
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timedelta
import imgkit
from rich.console import Console
import peewee
import mining_at_cloudatcost
import mining_at_ethermine
from database import db, Unpaid
from deltas_and_tags import (
    tags_row,
    tags_title,
    get_goal_msg,
    set_deltas_empty,
    set_deltas,
)
from table import (
    get_columns_and_lines,
    make_table,
    set_and_and_row_date,
    add_row,
    add_last_row,
    show_progress,
)

TS_FMT = "%Y-%m-%d %H:%M:%S"
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


def get_params():
    """Get params"""
    eth_addr = "0x0892c9b9b58ad5a7878d5dcd4da4ee72109c32c6"
    parser = argparse.ArgumentParser(
        description=f"Get wallet balance from Cloudatcost mining process.\nDonate ETH 👉 {eth_addr}",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "-only-cac",
        "--only-cloudatcost",
        action="store_true",
        default=False,
        dest="cloudatcost",
        help="Only show cloudatcost info",
    )
    parser.add_argument(
        "-only-etm",
        "--only-ethermine",
        action="store_true",
        default=False,
        dest="ethermine",
        help="Only show ethermine info",
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
    crontab = "1 2,6,10,14,18,22 * * * /usr/local/miner_preview/preview.py -ou"
    parser.add_argument(
        "-ou",
        "--only_update",
        action="store_true",
        default=False,
        dest="only_update",
        help=f"Only update database, useful with crontab config 👇\n{crontab}",
    )
    args = parser.parse_args()
    if not args.ethermine and not args.cloudatcost:
        args.ethermine = args.cloudatcost = True
    return {
        "ethermine": args.ethermine,
        "cloudatcost": args.cloudatcost,
        "only_update": args.only_update,
        "records": args.records,
        "save": args.save,
    }


def get_records(records, source, currency):
    """Get records and recalculate number of records"""
    try:
        if records == 0:
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == source) & (Unpaid.currency == currency)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
            )
        else:
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == source) & (Unpaid.currency == currency)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
                .limit(records)
            )
            last_unpaid = unpaids[-1]
            count, item = records - 1, 0
            for unpaid in unpaids:  # reversed(unpaids):
                count -= 1
                if count <= 0:
                    break
                if unpaid.timestamp[:10] != last_unpaid.timestamp[:10]:
                    last_unpaid = unpaid
                    item += 1

            item += 1  # First and Last
            records -= item  # Extra line of summary
            unpaids = (
                Unpaid.select()
                .where(
                    (Unpaid.source == source) & (Unpaid.currency == currency)
                )
                .order_by(Unpaid.work.desc(), Unpaid.step.desc())
                .limit(records)
            )

    except peewee.DoesNotExist:
        print("do-something")
    return records, unpaids


def iterate_on_records(source, currency, table, params, data):
    """Iterate on records"""

    # print('LS: ', data["lines_show"])
    tag = {}
    tag["currency"] = "[cyan]"
    # print('ANTES: ', params["records"])
    params[f"records_{currency}"], unpaids = get_records(
        params[f"records_{currency}"], source, currency
    )
    # print('DESPUES: ', params[f"records_{currency}"])
    data["last_unpaid"] = None
    delta = last_delta = {}
    delta[source] = data["unpaid_save"]

    item = 0
    for unpaid in reversed(unpaids):
        item += 1
        if data["last_unpaid"] is None:
            set_deltas_empty(unpaid, delta)
            last_delta = delta.copy()
        else:
            last_delta = delta.copy()
            set_deltas(data["last_unpaid"], unpaid, last_delta, delta)
        tags_row(tag, data["last_unpaid"], unpaid, last_delta, delta)
        if last_delta["date"] != delta["date"] or item == 1:
            set_and_and_row_date(table, data["last_unpaid"], unpaid, delta)
            data["lines_show"] -= 1
        add_row(table, tag, delta, unpaid)
        data["lines_show"] -= 1
        if item == unpaids.count():
            timestamp_obj = datetime.strptime(unpaid.timestamp, TS_FMT)
            next_update["timestamp"] = timestamp_obj + timedelta(hours=4)
            next_update["timestamp"] = next_update["timestamp"].replace(
                minute=1, second=0
            )
        data["last_unpaid"] = unpaid

    add_last_row(table, delta, data["last_unpaid"])
    data["lines_show"] -= 4  # 1 Summary + 3 Header


def show_data(params, unpaid_save, size_term):
    """Show time"""
    if params["records"] == -1:
        params["records"] = size_term["lines"]
        if params["ethermine"] and params["cloudatcost"]:
            params["records"] = int(params["records"] / 2)  # Sharing
        params["records"] -= 4  # 3 Lines of header + 1 of Footer
    sources = []
    if params["ethermine"]:
        sources.append("ethermine")
        params["records_eth"] = params["records"]
    if params["cloudatcost"]:
        sources.append("cloudatcost")
        params["records_btc"] = params["records"]

    lines_show = size_term["lines"] - 1
    if lines_show < 3 and params["records"]:
        print("Too small to show")
        sys.exit(0)
    print(chr(27) + "[2J")

    data = {
        "lines_show": lines_show,
        "next_update": next_update,
        "last_unpaid": None,
        "unpaid_save": unpaid_save,
    }
    for source in sources:
        if source == "cloudatcost":
            currency = "btc"
        else:
            currency = "eth"
        table = make_table()
        iterate_on_records(source, currency, table, params, data)
        console = Console(record=True)
        timestamp = datetime.now().strftime(TS_FMT)
        tag = {}
        tags_title(tag, data["last_unpaid"], timestamp)
        size_term = get_columns_and_lines()
        console.print(
            f"{tag['title']} ⛏️ {currency.upper()}@"
            f"[bold white]{timestamp}[not bold black] "
            f"{tag['ok']}{get_goal_msg(source, currency, tag, data['last_unpaid'], size_term)}",
            style=tag["style"],
            justify="center",
        )
        console.print(table)
    if params["records"] != 0:
        while data["lines_show"] > 0:
            data["lines_show"] -= 1
            console.print("")
    if params["save"]:
        console.save_html(params["save"])
        setup_html(params["save"])
    next_update["missing"] = next_update["timestamp"] - datetime.now()
    return next_update["missing"].total_seconds()


def save_data(source, currency, value, usd):
    """Save record"""
    try:
        unpaid = (
            Unpaid.select()
            .where((Unpaid.source == source) & (Unpaid.currency == currency))
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
            source=source,
            currency=currency,
            work=work,
            step=step,
            timestamp=timestamp,
            value=value,
            usd=usd,
        )
        unpaid.save()
        # pylint: disable=no-member
        unpaid_save = unpaid.id
    else:
        unpaid_save = 0
    return unpaid_save


def get_data():
    """Get data from miner"""
    source, currency = "ethermine", "eth"
    etmpanel = mining_at_ethermine.ETMPanel()
    eth, usd = etmpanel.wallet()
    unpaid_save_etm = save_data(source, currency, eth, usd)
    source, currency = "cloudatcost", "btc"
    cacpanel = mining_at_cloudatcost.CACPanel()
    btc, usd = cacpanel.wallet()
    unpaid_save_cac = save_data(source, currency, btc, usd)

    return {"etm": unpaid_save_etm, "cac": unpaid_save_cac}


def do_loop():
    """Eternal Loop 4 forever & ever"""
    setup_db()
    size_term = get_columns_and_lines()
    params = get_params()
    while True:
        unpaid_save = get_data()
        if params["only_update"]:
            timestamp = datetime.now().strftime(TS_FMT)
            id_save = unpaid_save
            print(f"{timestamp} => {id_save}")
            return
        seconds = show_data(params, unpaid_save, size_term)
        if params["records"] == 0 or params["save"]:
            return
        try:
            show_progress(seconds, next_update)
        except KeyboardInterrupt:
            sys.exit(0)


do_loop()
