#!/usr/bin/python3
""" mining_at_ethermine.py - get information from nicehash.com
    v0.0.2 - 2022-05-07 - nelbren@nelbren.com """
import os
import sys
import requests
import uuid
import hmac
import math
from time import mktime
from datetime import datetime, timedelta
from hashlib import sha256
from datetime import datetime
import inspect

WD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PD = os.path.dirname(WD)
sys.path.insert(0, PD)

from config import get_config


class Error(Exception):
    """Base class for other exceptions"""


class CantGetUSDandBTC(Error):
    """Raised when Can't get usd and btc"""


class NCHPanel:
    """Class to manage the access to Nicehash API"""

    host = "https://api2.nicehash.com"

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = (
            mktime(now.timetuple()) + now.microsecond / 1000000.0
        )
        return int(now_ec_since_epoch * 1000)

    def request(self, method, path, query, body):
        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(str(xtime), "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(xnonce, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(self.org, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(method, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(path, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(query, "utf-8")

        if body:
            body_json = json.dumps(body)
            message += bytearray("\x00", "utf-8")
            message += bytearray(body_json, "utf-8")

        digest = hmac.new(
            bytearray(self.secret, "utf-8"), message, sha256
        ).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            "X-Time": str(xtime),
            "X-Nonce": xnonce,
            "X-Auth": xauth,
            "Content-Type": "application/json",
            "X-Organization-Id": self.org,
            "X-Request-Id": str(uuid.uuid4()),
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += "?" + query

        if self.verbose:
            print(method, url)

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(
                str(response.status_code)
                + ": "
                + response.reason
                + ": "
                + str(response.content)
            )
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_accounts_for_currency(self, currency):
        return self.request(
            "GET", "/main/api/v2/accounting/account2/" + currency, "", None
        )

    def get_price(self):
        """Price"""
        data = self.request("GET", "/exchange/api/v2/info/prices", "", None)
        return data["BTCUSDC"]
        # url = self.url_base + "/poolStats"
        # json = requests.get(url).json()
        # return json["data"]["price"]["usd"]

    def datetime_from_utc_to_local(utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(
            now_timestamp
        ) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset

    def utc2local(self, utc):
        epoch = mktime(utc.timetuple())
        offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(
            epoch
        )
        return utc + offset

    def next_payout(self):
        data = self.request("GET", "/main/api/v2/mining/rigs2", "", None)
        utc_str = data["nextPayoutTimestamp"]
        utc_obj = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return self.utc2local(utc_obj)

    def unpaid(self):
        data = self.request("GET", "/main/api/v2/mining/algo/stats", "", None)
        return data["algorithms"]["DAGGERHASHIMOTO"]["unpaid"]

    def wallet(self):
        """Get Miner information"""
        # if not self.address:
        #    return -1, -1
        # print(f"{TAG[0]} Can't get crypto info")
        # raise CantGetUSDandETH
        # url = self.url_base + f"/miner/{self.address}/currentStats"
        # json = requests.get(url).json()
        # unpaid = json["data"]["unpaid"]
        # unpaid_eth = unpaid / 1000000000000000000
        # unpaid_usd = round(unpaid_eth * price, 2)
        # unpaid_eth = float(f"{unpaid_eth:0.8f}")
        price = self.get_price()
        pending_btc = float(self.unpaid())
        pending_usd = round(pending_btc * price, 2)
        next_payout = self.next_payout()
        unpaid_btc = float(
            self.get_accounts_for_currency("BTC")["totalBalance"]
        )
        unpaid_usd = round(unpaid_btc * price, 2)
        #return unpaid_btc, unpaid_usd, next_payout, pending_btc, pending_usd
        unpaid_btc = f'{unpaid_btc + pending_btc:1.8f}'
        unpaid_usd = f'{unpaid_usd + pending_usd:05.2f}'
        return float(unpaid_btc), float(unpaid_usd)

    def __init__(self):
        cfg = get_config()
        self.org = cfg["nch_org"]
        self.key = cfg["nch_key"]
        self.secret = cfg["nch_secret"]
        self.verbose = False


TAG = ["✖", "✔"]

if __name__ == "__main__":
    nchpanel = NCHPanel()
    try:
        btc, usd = nchpanel.wallet()
    except CantGetUSDandBTC:
        sys.exit(1)
    else:
        print(f"BTC: {btc:1.8f} USD: {usd:05.2f}", flush=True)
