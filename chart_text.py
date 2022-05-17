#!/usr/bin/python3
""" chart.py - display information as a chart
    v0.0.5 - 2022-05-07 - nelbren@nelbren.com"""
from database import db, Unpaid
import plotext as plt
from plotext._utility.color import uncolorize


def show_chart(source, currency, show=False):
    """Show Chart"""
    days = 7
    measure_per_day = 6
    width = days * measure_per_day
    records = width
    # source, currency = "cryptoatcost", "btc"
    unpaids = (
        Unpaid.select()
        .where((Unpaid.source == source) & (Unpaid.currency == currency))
        .order_by(Unpaid.timestamp.desc())
        .limit(records)
    )
    # print(unpaids)
    values = []
    usds = []
    timestamps = []
    for unpaid in reversed(unpaids):
        values.append(unpaid.value)
        usds.append(unpaid.usd)
        timestamps.append(unpaid.timestamp)
    title = f"Mining {currency.upper()} at {source.upper()} represented in"
    plt.subplots(2, 1)

    plt.subplot(1, 1)
    plt.clc()
    plt.ticks_color("cyan")
    plt.datetime.set_datetime_form(date_form="%Y-%m-%d %H:%M:%S")
    plt.plot_date(timestamps, usds, fillx=False, color="bright-cyan")
    plt.title(f"{title} USD")

    plt.subplot(2, 1)
    plt.title(f"{title} BTC")
    plt.clc()
    plt.plot_date(timestamps, values, color="bright-magenta")
    plt.ticks_color("magenta")
    if show:
        plt.show()
    else:
        return uncolorize(plt.build())


if __name__ == "__main__":
    show_chart(True)
