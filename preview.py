#!/usr/bin/python3
""" preview.py - show information from CAC
    v0.1.5 - 2021-10-24 - nelbren@nelbren.com"""
import os
import sys
import time
import argparse
from datetime import (
        datetime,
        timedelta
    )
import configparser
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
from database import (
        db,
        Unpaid
    )

TS_FMT = '%Y-%m-%d %H:%M:%S'
SOURCE = 'cloudatcost'
CURRENCY = 'btc'
unpaid_save = {}
next_update = {}

def get_goals():
    '''Get goals from config'''
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    filename = '.secret.cfg'
    minercac.check_config(path, filename)
    config.read_file(open(path + '/' + filename))
    goal_usd = config.get('CAC_WALLET', 'GOAL_USD', fallback=None)
    goal_btc = config.get('CAC_WALLET', 'GOAL_BTC', fallback=None)
    return goal_usd, goal_btc

def setup():
    '''Setup'''
    models = [ Unpaid ]
    db.connect()
    db.create_tables(models)
    try:
        _columns, _lines = os.get_terminal_size()
    # pylint: disable=unused-variable
    except OSError as exception:
        _columns, _lines = 80, 24
    _records = _lines - 5
    return _columns, _lines, _records

def add_columns(table):
    ''''Header'''
    table.add_column('timestamp', justify='center', style='white', no_wrap=True)
    table.add_column('±ts', justify='right', style='magenta', no_wrap=True)
    table.add_column('value', justify='right', style='green', no_wrap=True)
    table.add_column('±value', justify='right', style='magenta', no_wrap=True)
    table.add_column('usd', justify='right', style='green', no_wrap=True)
    table.add_column('±usd', justify='right', style='magenta', no_wrap=True)

def ts_to_int(timediff):
    '''Timestamp to int'''
    ts_str = str(timediff)
    if isinstance(timediff, timedelta):
        if timediff.days > 0:
            ts_str = ts_str.replace(' days, ', ':')
        ts_str = ts_str.replace(':', '')
    return int(ts_str)

def set_tag_delta(value1, value2):
    '''Set tag delta'''
    if value1 == value2:
        return '[black on white]=[white on black]'
    if value1 > value2:
        return '[black on green]^[green on black]'
    return '[black on red]v[red on black]'

def set_option_value(value1, value2):
    '''Set tag value'''
    if value1 == 0:
        color, label = 'white', '='
    elif value1 > value2:
        color, label = 'green', '^'
    else:
        color, label = 'red', 'v'
    return f'[black on {color}]{label}[{color} on black]'

def tags_row(tag, last_unpaid, unpaid, last_delta, delta):
    '''Set tag colors to row'''
    if unpaid_save[SOURCE] == unpaid.id:
        tag['timestamp'] = '[black on white]'
    else:
        tag['timestamp'] = '[white on black]'

    if ts_to_int(last_delta['timestamp']) == 0:
        if ts_to_int(delta['timestamp']) == 0:
            color, label = 'white', '='
        else:
            color, label = 'green', '^'
    elif ts_to_int(delta['timestamp']) > ts_to_int(last_delta['timestamp']):
        color, label = 'green', '^'
    else:
        color, label = 'red', 'v'
    tag['±timestamp'] = f'[black on {color}]{label}[{color} on black]'

    if last_unpaid is None:
        last_value, last_usd = 0, 0
    else:
        last_value, last_usd = last_unpaid.value, last_unpaid.usd
    tag['value'] = set_option_value(unpaid.value, last_value)
    tag['±value'] = set_tag_delta(delta['±value'], last_delta['±value'])
    tag['usd'] = set_option_value(unpaid.usd, last_usd)
    tag['±usd'] = set_tag_delta(delta['±usd'], last_delta['±usd'])

def tags_title(tag, diff_ts_now):
    '''Set tag colors to title'''
    tag['style'] = 'black on '
    if diff_ts_now > timedelta(hours=4):
        color, tag['ok'] = 'red', '✖'
    else:
        color, tag['ok'] = 'green', '✔'
    tag['style'] += color
    tag['title'] = f"[{tag['style']}][not bold]"

def tag_pm(tag, goal_pm):
    '''Set tag colors to pm'''
    tag['pm'] = '[bold]'
    if goal_pm > 75:
        tag['pm'] += '[white]'
    elif goal_pm > 50:
        tag['pm'] += '[cyan]'
    elif goal_pm > 25:
        tag['pm'] += '[yellow]'
    else:
        tag['pm'] += '[white]'

def get_goal_msg_item(tag, label, goal, value, item_cols):
    '''Goal USD'''
    if not goal:
        return ''
    if item_cols < 5:
        return ''
    bars = item_cols - 10 # 051.03%USD
    goal_pm = round((float(value) / float(goal)) * 100, 2)
    show_bars = int((goal_pm / 100) * bars)
    if show_bars >= bars:
        show_bars = bars
        rest_bars = 0
        missing = ''
    else:
        rest_bars = bars - show_bars
        missing = '[not bold][red]' + rest_bars * '■'
    progress = '[bold][green]' + show_bars * '■'
    progress_bar = f'{progress}{missing}'
    tag_pm(tag, goal_pm)
    goal_msg = (
                    f"🎯{tag['pm']}{goal_pm:06.2f}%{label}"
                    f"{tag['title']}[{progress_bar}{tag['title']}]"
                )
    return goal_msg

def get_goal_msg(tag, unpaid):
    '''Goal Message'''
    goal_usd, goal_btc = get_goals()
    if not goal_usd and not goal_btc:
        return ''
    rest_cols = columns - 37
    items = 0
    if goal_usd:
        items += 1
    if goal_btc:
        items += 1
    items_cols = int(rest_cols / items)
    goal_msg_detail = get_goal_msg_item(tag, 'USD', goal_usd, unpaid.usd, items_cols)
    goal_msg_detail += get_goal_msg_item(tag, 'BTC', goal_btc, unpaid.value, items_cols)
    return f'|{goal_msg_detail} '

def show_data():
    '''Show time'''
    timestamp = datetime.now().strftime(TS_FMT)
    table = Table(show_header=True, header_style='bold white',
                    box=box.SIMPLE, show_edge=False, expand=True)
    add_columns(table)
    tag = {}
    lines_show = lines - 5
    tag['currency'] = '[cyan]'
    try:
        if records == 0:
            unpaids = Unpaid.select().where(
                            (Unpaid.source == SOURCE) &
                            (Unpaid.currency == CURRENCY)
                        ).order_by(Unpaid.work.desc(),
                        Unpaid.step.desc())
        else:
            unpaids = Unpaid.select().where(
                            (Unpaid.source == SOURCE) &
                            (Unpaid.currency == CURRENCY)
                        ).order_by(Unpaid.work.desc(),
                        Unpaid.step.desc()).limit(records)
    except peewee.DoesNotExist:
        print('do-something')
    else:
        last_unpaid = None
        item = 0
        delta = {}
        for unpaid in reversed(unpaids):
            item += 1

            if last_unpaid is None:
                delta['timestamp'] = '0'
                delta['±value'] = 0
                delta['±usd'] = 0
                last_delta = delta.copy()
            else:
                last_delta = delta.copy()
                delta['timestamp'] = (
                                datetime.strptime(unpaid.timestamp, TS_FMT) -
                                datetime.strptime(last_unpaid.timestamp, TS_FMT)
                            )
                delta['±value'] = unpaid.value - last_unpaid.value
                delta['±usd'] = unpaid.usd - last_unpaid.usd

            tags_row(tag, last_unpaid, unpaid, last_delta, delta)
            table.add_row(  f"{tag['timestamp']}{unpaid.timestamp}",
                            f"{tag['±timestamp']}{delta['timestamp']}",
                            f"{tag['value']}{unpaid.value:1.8f}",
                            f"{tag['±value']}{delta['±value']:1.8f}",
                            f"{tag['usd']}{unpaid.usd:05.2f}",
                            f"{tag['±usd']}{delta['±usd']:05.2f}")
            lines_show -= 1
            if item == unpaids.count():
                diff_ts_now = (
                                datetime.strptime(timestamp, TS_FMT) -
                                datetime.strptime(unpaid.timestamp, TS_FMT)
                            )
                timestamp_obj = datetime.strptime(unpaid.timestamp, TS_FMT)
                next_update['timestamp'] = timestamp_obj + timedelta(hours=4)
                next_update['timestamp'] = next_update['timestamp'].replace(minute=1, second=0)
            last_unpaid = unpaid

    print(chr(27) + "[2J")
    console = Console(record=True)
    tags_title(tag, diff_ts_now)
    goal_msg = get_goal_msg(tag, last_unpaid)
    console.print(
            f"{tag['title']} ⛏️ BTC@"
            f"[bold white]{timestamp}[not bold black] {tag['ok']}{goal_msg}",
            style=tag['style'], justify='center'
        )
    console.print(table)
    if records != 0:
        console.print()
        while lines_show:
            lines_show -= 1
            console.print()
    next_update['missing'] = next_update['timestamp'] - datetime.now()
    return next_update['missing'].total_seconds()

def show_progress(seconds):
    '''Show the progress bar'''
    with Progress(
            TextColumn(
                f"[magenta on black]Waiting "
                f"to update on [black on yellow]{next_update['timestamp']}",
                justify="right"
            ),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            SpinnerColumn(), TimeRemainingColumn(), expand=True
        ) as progress:
        #task1 = progress.add_task('waiting 4 hours', total=60 * 60 * 4)
        task1 = progress.add_task('waiting 4 hours', total=seconds)
        while not progress.finished:
            progress.update(task1, advance=1)
            time.sleep(1)

def save_data(value, usd):
    '''Save record'''
    try:
        unpaid = Unpaid.select().where(
                    (Unpaid.source == SOURCE) &
                    (Unpaid.currency == CURRENCY)
                ).order_by(Unpaid.work.desc(), Unpaid.step.desc()).get()
    except peewee.DoesNotExist:
        last_value, work, step = 0, 1, 1
    else:
        last_value, work, step = unpaid.value, unpaid.work, unpaid.step + 1
        timestamp = unpaid.timestamp

    if last_value != value:
        timestamp = f'{datetime.now()}'
        timestamp_obj = datetime.strptime(timestamp, TS_FMT + '.%f')
        timestamp = timestamp_obj.strftime(TS_FMT)
        unpaid = Unpaid(source=SOURCE, currency=CURRENCY, work=work,
            step=step, timestamp=timestamp, value=value, usd=usd)
        unpaid.save()
        # pylint: disable=no-member
        unpaid_save[SOURCE] = unpaid.id
    else:
        unpaid_save[SOURCE] = 0

def get_data():
    '''Get data from miner'''
    cacpanel = minercac.CACPanel()
    btc, usd = cacpanel.wallet()
    #if goal:
    #    goal_pm = round((float(usd) / goal) * 100, 2)
    #else:
    #    goal_pm = 0
    save_data(btc, usd)

def do_loop():
    '''Eternal Loop 4 forever & ever'''
    while True:
        get_data()
        seconds = show_data()
        if records == 0:
            return
        try:
            show_progress(seconds)
        except KeyboardInterrupt:
            sys.exit(0)

def params():
    '''Set params'''
    parser = argparse.ArgumentParser(
        description='Get wallet balance from Cloudatcost mining process.'
    )
    parser.add_argument('-r', '--records', type=int, required=False,
        default=-1, help='The number of last records to get (0 = All)')
    args = parser.parse_args()
    if args.records == -1:
        _records = records
    else:
        _records = args.records
    return _records

columns, lines, records = setup()
records = params()
do_loop()
