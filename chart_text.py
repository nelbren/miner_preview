#!/usr/bin/python3
""" chart_text.py - display information as a chart
    v0.0.8 - 2023-07-04 - nelbren@nelbren.com"""
from database import db, Unpaid
import plotext as plt
#from plotext._utility.color import uncolorize


def show_chart(source, currency, size_term, show=False):
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
    plt.plot_size(size_term["columns"], 30)
    plt.limit_size(False)
    plt.subplots(2, 1)

    plt.subplot(1, 1)
    plt.clc()
    plt.date_form("Y-m-d H:M:S")
    plt.plot(timestamps, usds, fillx=False, color="bright-cyan")
    plt.title(f"{title} USD")
    plt.ticks_color("cyan")

    plt.subplot(2, 1)
    plt.clc()
    plt.date_form("Y-m-d H:M:S")
    plt.plot(timestamps, values, color="bright-magenta")
    plt.title(f"{title} {currency.upper()}")
    plt.ticks_color("magenta")
    if show:
        plt.show()
    else:
        return plt.uncolorize(plt.build())


if __name__ == "__main__":
    show_chart(True)
