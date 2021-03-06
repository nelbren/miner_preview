#!/usr/bin/python3
""" ethermine.py - get information from ethermine.org
    v0.0.6 - 2022-05-07 - nelbren@nelbren.com """
import os
import sys
import requests
import inspect

WD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PD = os.path.dirname(WD)
sys.path.insert(0, PD)

from config import get_config


class Error(Exception):
    """Base class for other exceptions"""


class CantGetUSDandETH(Error):
    """Raised when Can't get usd and eth"""


class ETMPanel:
    """Class to manage the access to Ethermine API"""

    url_base = "https://api.ethermine.org"

    def get_price(self):
        """Price"""
        url = self.url_base + "/poolStats"
        json = requests.get(url).json()
        return json["data"]["price"]["usd"]

    def wallet(self):
        """Get Miner information"""
        if not self.address:
            return -1, -1
            # print(f"{TAG[0]} Can't get crypto info")
            # raise CantGetUSDandETH
        url = self.url_base + f"/miner/{self.address}/currentStats"
        json = requests.get(url).json()
        unpaid = json["data"]["unpaid"]
        unpaid_eth = unpaid / 1000000000000000000
        price = self.get_price()
        unpaid_usd = round(unpaid_eth * price, 2)
        unpaid_eth = float(f"{unpaid_eth:0.8f}")
        return unpaid_eth, unpaid_usd

    def __init__(self):
        cfg = get_config()
        self.address = cfg["address"]


TAG = ["✖", "✔"]

if __name__ == "__main__":
    etmpanel = ETMPanel()
    try:
        eth, usd = etmpanel.wallet()
    except CantGetUSDandETH:
        sys.exit(1)
    else:
        print(f"ETH: {eth:1.8f} USD: {usd:05.2f}")
