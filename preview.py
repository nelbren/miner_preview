#!/usr/bin/python3
""" preview.py - show information from cryptoatcost.com and ethermine.org
    v0.3.6 - 2023-04-27 - nelbren@nelbren.com"""
import os
import re
import sys
import shutil
import socket
import argparse
import tempfile
import smtplib
import requests
import subprocess
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from argparse import RawTextHelpFormatter
from datetime import datetime, timedelta
from random import randint, uniform
import imgkit
import peewee
from rich.console import Console
import mining.cryptoatcost
import mining.ethermine
import mining.nicehash
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
from config import get_config
import big_text
import chart_text

TS_FMT = "%Y-%m-%d %H:%M:%S"
next_update = {}
PWD = os.path.dirname(os.path.realpath(__file__))
PWD_DIR = os.path.basename(PWD)


def setup_db():
    """Setup"""
    models = [Unpaid]
    db.connect()
    db.create_tables(models)


def setup_jpg(html):
    """Setup JPG"""
    html2 = os.path.splitext(html)[0] + "_temp.html"
    shutil.copyfile(html, html2)
    with open(html2, "r+", encoding="utf-8") as _file:
        text = _file.read()
        text = re.sub("⛏️", "&nbsp;", text)
        text = re.sub("🎯", "&nbsp;&nbsp;", text)
        _file.seek(0)
        _file.write(text)
        _file.truncate()
    options = {"encoding": "latin_1", "quiet": ""}
    img = os.path.splitext(html)[0] + ".jpg"
    imgkit.from_file(html2, img, options=options)
    os.unlink(html2)


def setup_html(html):
    """Setup HTML"""
    with open(html, "r+", encoding="utf-8") as _file:
        text = _file.read()
        pre1 = "pre { color: #ffffff; background-color: #000000; "
        pre2 = "font-size: 41px; }"
        pre = pre1 + pre2
        text = re.sub("</style>", f"{pre}\n</style>", text)
        _file.seek(0)
        _file.write(text)
        _file.truncate()
    setup_jpg(html)


def get_subject(numbers, tag):
    """get_subject"""
    subject = ""
    for mining, number in numbers.items():
        if mining == "ethermine":
            goal = f"{tag['ethermine_goal_pm_usd']:06.2f}%"
            # subject += f"ETM: ⛏️ E{number['usd']} 🎯{goal}"
            subject += f"ETM⛏️💵{number['usd']}🏦{number['val']}"
        if mining == "cryptoatcost":
            goal = f"{tag['cryptoatcost_goal_pm_usd']:06.2f}%"
            if subject != "":
                subject += " "
            # subject += f"CAC: ⛏️ B{number['usd']} 🎯{goal}"
            subject += f"CAC⛏️💵{number['usd']}🏦{number['val']}"
        if mining == "nicehash":
            goal = f"{tag['nicehash_goal_pm_usd']:06.2f}%"
            if subject != "":
                subject += " "
            # subject += f"NCH: ⛏️ B{number['usd']} 🎯{goal}"
            subject += f"NCH⛏️💵{number['usd']}🏦{number['val']}"
    return subject


def mail_data(params, numbers, tag):
    """mail_data"""
    cfg = get_config()
    if not cfg["mail_from"] or not cfg["mail_to"]:
        print("Please set the FROM and TO fields of MAIL!")
        sys.exit(0)
    msg = MIMEMultipart()
    msg["From"] = cfg["mail_from"]
    msg["To"] = cfg["mail_to"]
    msg["Subject"] = get_subject(numbers, tag)

    name = PWD_DIR + ".jpg"
    filename = params["save_dir"] + "/" + name
    with open(filename, "rb") as _file:
        part = MIMEApplication(_file.read(), Name=name)
    part["Content-Decomposition"] = f"attachment, filename={name}"
    msg.attach(part)

    smtp = smtplib.SMTP("localhost")
    smtp.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp.close()


def telegram_send_msg(cfg, msg):
    """telegram_send_msg"""
    send_text = (
        f"https://api.telegram.org/bot{cfg['telegram_token']}"
        f"/sendMessage?chat_id={cfg['telegram_id']}&parse_mode=Markdown&text={msg}"
    )
    # print(send_text)
    response = requests.get(send_text)
    # print(response)
    # return response.json()


def telegram_data(params, numbers, tag, next_update):
    cfg = get_config()
    if not cfg["telegram_token"] or not cfg["telegram_id"]:
        print("Please set the TOKEN and ID fields of TELEGRAM!")
    subject = get_subject(numbers, tag)
    telegram_send_msg(cfg, subject)
    name = PWD_DIR + ".jpg"
    image_path = params["save_dir"] + "/" + name
    data = {"chat_id": cfg["telegram_id"], "caption": ""}
    url = f"https://api.telegram.org/bot{cfg['telegram_token']}/sendPhoto"
    with open(image_path, "rb") as image_file:
        response = requests.post(url, data=data, files={"photo": image_file})
    # print(url, data, response.json())
    msg, count = "", 0
    msg += "✅"  # msg += '🔳'
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    msg += numbers[1]
    next_update_str = next_update["timestamp"]
    msg += f"🔜{next_update_str}xBTC"
    telegram_send_msg(cfg, msg)


def get_params():
    """Get params"""
    eth_addr = "0x0892c9b9b58ad5a7878d5dcd4da4ee72109c32c6"
    email = "nelbren@nelbren.com"
    parser = argparse.ArgumentParser(
        add_help=False,
        description=(
            "Get wallet balance from Ethermine, Crytoatcost & Nicehash"
            f" mining process.\nDonate ETH 👉 {eth_addr}"
            f"\nContact email 👉 {email}"
        ),
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--cryptoatcost",
        type=str,
        default="btc",
        #dest="cryptoatcost",
        help="Only show cryptoatcost info",
    )
    parser.add_argument(
        "-e",
        "--ethermine",
        action="store_true",
        default=False,
        dest="ethermine",
        help="Only show ethermine info",
    )
    parser.add_argument(
        "-n",
        "--nicehash",
        action="store_true",
        default=False,
        dest="nicehash",
        help="Only show nicehash info",
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
        "--columns",
        type=int,
        required=False,
        default=-1,
        help="The number of columns",
    )
    parser.add_argument(
        "-s",
        "--save_dir",
        required=False,
        default="",
        help="Directory to save the output (HTML and JPG)",
    )
    hours = "3,7,11,15,19,23"
    crontab = f"{hours} * * * /path/preview.py"
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        default=False,
        dest="update",
        help=(
            "Only update database, crontab 👇\n"
            "# Update data at minute 1 every 4 hours\n"
            f"1 {crontab} -u"
        ),
    )
    parser.add_argument(
        "-m",
        "--mail",
        action="store_true",
        default=False,
        dest="mail",
        help=(
            "Send an email with the image attachment, crontab 👇\n"
            "# Send mail with a picture at minute 2 every 4 hours \n"
            f"2 {crontab} -m"
        ),
    )
    parser.add_argument(
        "-t",
        "--telegram",
        action="store_true",
        default=False,
        dest="telegram",
        help="Send the data to telegram bot",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "-b",
        action="store_true",
        default=False,
        dest="big",
        help="Only show big text, like this 👇",
    )
    args = parser.parse_args()
    if args.help or (
        not args.ethermine and not args.cryptoatcost and not args.nicehash
    ):
        parser.print_help()
        console = Console()
        _number = uniform(1.0, 9999.99)
        if randint(0, 1):
            _tag, _color = "^", "green"
        else:
            _tag, _color = "v", "red"
        _fnumber = f"{_tag}${_number:5.2f}"
        big_text.big_line(console, _fnumber, _color)
        big_text.big_text(console, _fnumber, _color)
        sys.exit(0)
    cfg = get_config()
    hostname = cfg["hostname"]
    if args.mail or args.telegram:
        args.save_dir = tempfile.gettempdir()
    return {
        "big": args.big,
        "ethermine": args.ethermine,
        "cryptoatcost": args.cryptoatcost,
        "nicehash": args.nicehash,
        "hostname": hostname,
        "update": args.update,
        "records": args.records,
        "columns": args.columns,
        "save_dir": args.save_dir,
        "mail": args.mail,
        "telegram": args.telegram,
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


def set_missing():
    """Set Missing"""
    # AQUI
    timestamp = datetime.now().strftime(TS_FMT)
    timestamp_obj = datetime.strptime(timestamp, TS_FMT)
    if timestamp_obj > next_update["timestamp"]:
        set_next_update(timestamp_obj, 4)
    next_update["missing"] = next_update["timestamp"] - timestamp_obj
    next_update["total_seconds"] = next_update["missing"].total_seconds()


def set_next_update(timestamp_obj, hours):
    """Set Next Update"""
    next_update["timestamp"] = timestamp_obj + timedelta(hours=hours)
    next_update["timestamp"] = next_update["timestamp"].replace(
        minute=2, second=0
    )


def iterate_on_records(source, currency, table, params, data):
    """Iterate on records"""

    tag = {}
    tag["currency"] = "[cyan]"
    params[f"records_{source}"], unpaids = get_records(
        params[f"records_{source}"], source, currency
    )
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
            set_next_update(timestamp_obj, 4)
        data["last_unpaid"] = unpaid

    add_last_row(table, delta, data["last_unpaid"])
    data["lines_show"] -= 4  # 1 Summary + 3 Header


def show_data(console, params, unpaid_save, size_term):
    """Show time"""
    if params["records"] == -1:
        params["records"] = size_term["lines"]
        if params["ethermine"] and params["cryptoatcost"]:
            params["records"] = int(params["records"] / 2)  # Sharing
        params["records"] -= 4  # 3 Lines of header + 1 of Footer
    sources = []
    if params["ethermine"]:
        sources.append("ethermine")
        params["records_ethermine"] = params["records"]
    if params["cryptoatcost"]:
        sources.append("cryptoatcost")
        params["records_cryptoatcost"] = params["records"]
    if params["nicehash"]:
        sources.append("nicehash")
        params["records_nicehash"] = params["records"]

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
    tag = {}
    for source in sources:
        if source == "cryptoatcost":
            currency = params["cryptoatcost"]
        elif source == "nicehash":
            currency = "btc"
        else:
            currency = "eth"
        table = make_table()
        iterate_on_records(source, currency, table, params, data)
        timestamp = datetime.now().strftime(TS_FMT)
        tags_title(tag, data["last_unpaid"], timestamp)
        size_term = get_columns_and_lines(params)
        msg = get_goal_msg(
            source, currency, tag, data["last_unpaid"], size_term
        )
        console.print(
            f"{tag['title']} ⛏️ {currency.upper()}@"
            f"[bold white]{timestamp}[not bold black] "
            f"{tag['ok']}{msg}",
            style=tag["style"],
            justify="center",
        )
        console.print(table)
    if params["records"] != 0:
        while data["lines_show"] > 0:
            data["lines_show"] -= 1
            console.print("")
    if params["save_dir"]:
        html = params["save_dir"] + "/" + PWD_DIR + ".html"
        console.save_html(html)
        setup_html(html)
    if "timestamp" not in next_update:
        print("Nothing to do.")
        sys.exit(0)
    set_missing()
    return next_update["total_seconds"], tag


def save_data(source, currency, value, usd):
    """Save record"""
    if value == -1:
        return 0
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


def show_big(params, size_term):
    """Show big"""
    datas = []
    if params["ethermine"]:
        datas.append(
            {"source": "ethermine", "currency": "eth", "color": "white"}
        )
    if params["cryptoatcost"]:
        datas.append(
            {"source": "cryptoatcost", "currency": params["cryptoatcost"], "color": "white"}
        )
    if params["nicehash"]:
        datas.append(
            {"source": "nicehash", "currency": "btc", "color": "white"}
        )
    for data in datas:
        source = data["source"]
        currency = data["currency"]
        unpaids = (
            Unpaid.select()
            .where((Unpaid.source == source) & (Unpaid.currency == currency))
            .order_by(Unpaid.work.desc(), Unpaid.step.desc())
            .limit(2)
        )
        if len(unpaids) >= 1:
            data["usd_" + source] = unpaids[0].usd
            data["val_" + source] = unpaids[0].value
        if len(unpaids) == 2:
            if unpaids[0].usd == unpaids[1].usd:
                data["tag_usd"] = "="
                data["color_usd"] = "white"
            elif unpaids[0].usd > unpaids[1].usd:
                data["tag_usd"] = "^"
                data["color_usd"] = "green"
            else:
                data["tag_usd"] = "v"
                data["color_usd"] = "red"
            if unpaids[0].value == unpaids[1].value:
                data["tag_val"] = "="
                data["color_val"] = "white"
            elif unpaids[0].value > unpaids[1].value:
                data["tag_val"] = "^"
                data["color_val"] = "green"
            else:
                data["tag_val"] = "v"
                data["color_val"] = "red"
        else:
            data["tag_usd"] =  data["tag_val"] = "="
            data["color_usd"] = data["color_val"] = "white"
    tags, colors, usds, vals = {}, {}, {}, {}
    colors["normal"] = "black"
    items = 0
    if params["ethermine"]:
        tags["usd_ethermine"] = datas[items]["tag_usd"]
        tags["val_ethermine"] = datas[items]["tag_val"]
        colors["usd_ethermine"] = datas[items]["color_usd"]
        colors["val_ethermine"] = datas[items]["color_val"]
        usds["usd_ethermine"] = datas[items]["usd_ethermine"]
        vals["val_ethermine"] = datas[items]["val_ethermine"]
        items += 1
    if params["cryptoatcost"]:
        tags["usd_cryptoatcost"] = datas[items]["tag_usd"]
        tags["val_cryptoatcost"] = datas[items]["tag_val"]
        colors["usd_cryptoatcost"] = datas[items]["color_usd"]
        colors["val_cryptoatcost"] = datas[items]["color_val"]
        usds["usd_cryptoatcost"] = datas[items]["usd_cryptoatcost"]
        vals["val_cryptoatcost"] = datas[items]["val_cryptoatcost"]
        items += 1
    if params["nicehash"]:
        tags["usd_nicehash"] = datas[items]["tag_usd"]
        tags["val_nicehash"] = datas[items]["tag_val"]
        colors["usd_nicehash"] = datas[items]["color_usd"]
        colors["val_nicehash"] = datas[items]["color_val"]
        usds["usd_nicehash"] = datas[items]["usd_nicehash"]
        vals["val_nicehash"] = datas[items]["val_nicehash"]
    # print(vals)
    console, numbers = big_text.show_big(usds, vals, tags, colors, size_term)
    # if params["cryptoatcost"]:
    #    big_text.show_big2(console, data["val_cryptoatcost"])
    # if params["nicehash"]:
    #    big_text.show_big2(console, data["val_nicehash"])
    return console, numbers


def show_chart(console, params, size_term):
    sources = []
    if params["cryptoatcost"]:
        sources.append({ "source": "cryptoatcost", "crypto": params["cryptoatcost"] })
    if params["nicehash"]:
        sources.append({ "source": "nicehash", "crypto": "btc" })
    for source in sources:
        text = chart_text.show_chart(source["source"], source["crypto"], size_term)
        # print(text)
        colors = ["cyan", "magenta"]
        c = 0
        line = ""
        lines = []
        for char in text:
            line += char if not char == "\n" else ""
            if char == "\n":
                lines.append(line)
                line = ""
        chart = 0
        tag_color = ""
        for line in lines:
            if "Mining" in line:
                color = colors[chart]
                tag_color = f"[{color} on black]"
                chart += 1
            console.print(f"{tag_color}{line}")


def get_data_remote(params):
    """Get data using another host"""
    pwd = os.path.dirname(os.path.realpath(__file__))
    cmd = f"{pwd}/mining/cryptoatcost.py"
    crypto = params['cryptoatcost'].upper()
    result = subprocess.Popen(
        f"ssh {params['hostname']} {cmd} {crypto}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    data = result[0].decode("utf-8").rstrip("\n")
    lst_data = data.split(" ")
    val_cac, usd_cac = float(lst_data[1]), float(lst_data[3])
    return val_cac, usd_cac


def get_data_local(crypto):
    """Get data using this host"""
    cacpanel =  mining.cryptoatcost.CACPanel()
    val_cac, usd_cac = cacpanel.wallet(crypto.upper())
    return val_cac, usd_cac


def get_data(params, size_term):
    """Get data from miner"""
    if params["ethermine"]:
        source, currency = "ethermine", "eth"
        etmpanel = mining.ethermine.ETMPanel()
        eth, usd_etm = etmpanel.wallet()
        unpaid_save_etm = save_data(source, currency, eth, usd_etm)
    else:
        unpaid_save_etm = 0
    if params["cryptoatcost"]:
        source, currency = "cryptoatcost", params['cryptoatcost']
        try:
            if (
                params["hostname"]
                and params["hostname"] != socket.gethostname()
            ):
                val_cac, usd_cac = get_data_remote(params)
            else:
                val_cac, usd_cac = get_data_local(params['cryptoatcost'])
            print(source, currency, val_cac, usd_cac)
            unpaid_save_cac = save_data(source, currency, val_cac, usd_cac)
            print(unpaid_save_cac)
        except mining.cryptoatcost.MaintenanceMode:
            unpaid_save_cac = 0
    else:
        unpaid_save_cac = 0
    if params["nicehash"]:
        source, currency = "nicehash", "btc"
        nchpanel = mining.nicehash.NCHPanel()
        btc, usd_nsh = nchpanel.wallet()
        unpaid_save_nsh = save_data(source, currency, btc, usd_nsh)
    else:
        unpaid_save_nhs = 0
    console, numbers = show_big(params, size_term)
    return console, numbers, {"etm": unpaid_save_etm, "cac": unpaid_save_cac}


def do_loop():
    """Eternal Loop 4 forever & ever"""
    setup_db()
    params = get_params()
    size_term = get_columns_and_lines(params)
    while True:
        console, numbers, unpaid_save = get_data(params, size_term)
        if params["big"]:
            return
        if params["update"]:
            timestamp = datetime.now().strftime(TS_FMT)
            id_save = unpaid_save
            print(f"{timestamp} => {id_save}")
            return
        show_chart(console, params, size_term)
        seconds, tag = show_data(console, params, unpaid_save, size_term)
        if params["telegram"]:
            telegram_data(params, numbers, tag, next_update)
        if params["mail"]:
            mail_data(params, numbers, tag)
        if params["records"] == 0 or params["save_dir"] or params["mail"]:
            return
        try:
            show_progress(seconds, next_update)

        except KeyboardInterrupt:
            sys.exit(0)


do_loop()
