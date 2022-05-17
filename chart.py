#!/usr/bin/python3
""" chart.py - display information as a chart
    v0.0.2 - 2022-05-07 - nelbren@nelbren.com"""
import asciichartpy
from math import cos
from math import pi
from database import db, Unpaid
import random
import plotext as plt


def asciichartpy():
    # width = 120
    width = 10
    records = width
    source, currency = "cryptoatcost", "btc"
    unpaids = (
        Unpaid.select()
        .where((Unpaid.source == source) & (Unpaid.currency == currency))
        .order_by(Unpaid.timestamp.desc())
        .limit(records)
    )
    print(unpaids)
    values = []
    usds = []
    for unpaid in reversed(unpaids):
        values.append(unpaid.value)
        usds.append(unpaid.usd)
        print(unpaid)
    test = [
        random.randint(1, 15) * cos(i * ((pi * 4) / width))
        for i in range(width)
    ]
    print(test)
    print(values)
    config = {
        "colors": [
            asciichartpy.magenta,
            asciichartpy.green,
        ]
    }
    chart = asciichartpy.plot(series=[usds], cfg=config)
    # series=[[random.randint(1, 15) * cos(i * ((pi * 4) / width)) for i in range(width)],
    #        [random.randint(1, 15) * cos(i * ((pi * 9) / width)) for i in range(width)]],
    print(chart)


def show_chart(source, currency):
    days = 7
    measure_per_day = 6
    width = days * measure_per_day
    records = width
    # source, currency = 'cryptoatcost', 'btc'
    unpaids = (
        Unpaid.select()
        .where((Unpaid.source == source) & (Unpaid.currency == currency))
        .order_by(Unpaid.timestamp.desc())
        .limit(records)
    )
    print(unpaids)
    values = []
    usds = []
    timestamps = []
    for unpaid in reversed(unpaids):
        values.append(unpaid.value)
        usds.append(unpaid.usd)
        timestamps.append(unpaid.timestamp)
    plt.subplots(2, 1)

    plt.subplot(1, 1)
    plt.clc()
    plt.ticks_color("green")
    plt.datetime.set_datetime_form(date_form="%Y-%m-%d %H:%M:%S")
    # plt.bar(timestamps, usds, color = "bright-green")
    # plt.plot_date(timestamps, usds, fillx = True, color = "bright-green")
    plt.plot_date(timestamps, usds, color="bright-green")
    plt.title(
        f"Mining {currency.upper()} at {source.upper()} represented in USD"
    )

    plt.subplot(2, 1)
    plt.title(
        f"Mining {currency.upper()} at {source.upper()} represented in BTC"
    )
    plt.clc()
    plt.plot_date(timestamps, values, color="bright-magenta")
    # plt.canvas_color(254)
    # plt.axes_color((20, 40, 100)) # rgb coloring
    plt.ticks_color("magenta")
    # plt.xlabel("Timestamp")
    # plt.ylabel("Value")

    plt.show()


if __name__ == "__main__":
    show_chart()
