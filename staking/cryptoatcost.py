#!/usr/bin/python3
""" cryptoatcost.py - get information from cryptoatcost.com
    v0.0.1 - 2023-06-03 - nelbren@nelbren.com
    NOTE: 2FA code thanks to Isonium """
import re
import os
import sys
import pickle
import tempfile
import requests
import pyotp
import inspect

WD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PD = os.path.dirname(WD)
sys.path.insert(0, PD)

from config import get_config

# import ipdb; ipdb.set_trace()
# import logging; logging.basicConfig(level=logging.DEBUG)


class Error(Exception):
    """Base class for other exceptions"""


class CantGetCsrf(Error):
    """Raised when Can't get _csrf"""


class MaintenanceMode(Error):
    """Raised when is in maintenance mode"""


class CantGetAuth2FA(Error):
    """Raised when Can't get Auth 2FA"""


class MissingAuth2FA(Error):
    """Raised when Missing Auth 2FA"""


class CantGetUSDandBTC(Error):
    """Raised when Can't get usd and btc"""


def debug(is_ok):
    """Show tag"""
    if DEBUG:
        tag = 1 if is_ok else 0
        print(f"{TAG[tag]} ", end="", flush=True)


class CACPanel:
    """Class to manage the access to CAC Panel"""

    url_base = "https://wallet.cryptoatcost.com"
    cookie = ".wallet_cryptoatcost.cookie"
    headers = {
        "accept-language": "en-US,en;q=0.9,es;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded",
        "connection": "keep-alive",
        "origin": "https://wallet.cryptoatcost.com",
        "referer": "https://wallet.cryptoatcost.com/login",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 "
        + "Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/90.0.4430.212 Mobile Safari/537.36",
    }
    logged = False

    def auth_2fa(self, page):
        """Auth 2FA process"""
        reg = r"(Two Factor Auth)"
        match = re.findall(reg, page.content.decode("utf-8"))
        if match:
            if not self.code_2fa:
                print(f"{TAG[0]} Missing CODE_2FA", flush=True)
                raise MissingAuth2FA
            if DEBUG:
                print("2FA -> ", end="", flush=True)
            url = self.url_base + "/auth"
            totp = pyotp.TOTP(self.code_2fa)
            data = {"authCode": totp.now(), "_csrf": self._csrf}
            if DEBUG > 1:
                print("\n\ndata=", data, flush=True)
                print(
                    "\n\nauth_2fa:PAGE-BEFORE-2FA:\n\n",
                    page.content.decode("utf-8"),
                    flush=True,
                )
            self.session.post(url, data=data, headers=self.headers)
            page = self.session.get(self.url_base)
            if DEBUG > 1:
                print(
                    "\nauth_2fa:PAGE-SESSION-GET:\n\n",
                    page.content.decode("utf-8"),
                    flush=True,
                )
            return page
        if not self.code_2fa:
            return page
        print(f"{TAG[0]} Can't get Auth 2FA", flush=True)
        raise CantGetAuth2FA

    def login(self):
        """Login process"""
        if DEBUG:
            print("Login -> ", end="", flush=True)
        data = {
            "email": self.username,
            "password": self.password,
            "_csrf": self._csrf,
        }
        url = self.url_base + "/login"
        self.session.post(url, data=data, headers=self.headers)
        with open(self.cookie, "wb") as _file:
            pickle.dump(self.session.cookies, _file)
        page = self.session.get(self.url_base)
        if self.code_2fa:
            try:
                page = self.auth_2fa(page)
            except MissingAuth2FA:
                sys.exit(4)
        reg = r">(Miners)<"
        match = re.findall(reg, page.content.decode("utf-8"))
        self.logged = match
        debug(self.logged)

    def pre_login(self):
        """Pre-login process"""
        if DEBUG:
            print("Pre-login -> ", end="", flush=True)
        url = self.url_base + "/login"
        if DEBUG:
            print(url, flush=True)
        page = self.session.get(url, headers=self.headers)
        if DEBUG > 1:
            print(
                "\npre_login:PAGE-SESSION-GET:\n\n",
                page.content.decode("utf-8"),
                flush=True,
            )
        reg = r'_csrf" value="([^"]+)"'
        match = re.findall(reg, page.content.decode("utf-8"))
        if DEBUG > 1:
            print(f" match {reg} => {match}", flush=True)
        debug(match)
        if match:
            self._csrf = match[0]
            self.login()
        else:
            msg = "Maintenance in progress"
            reg = fr"{msg}"
            match = re.findall(reg, page.content.decode("utf-8"))
            if match:
                print(f"cryptoatcost: {msg}", flush=True)
                raise MaintenanceMode
            print(f"{TAG[0]} Can't get _csrf", flush=True)
            raise CantGetCsrf

    def __init__(self):
        cfg = get_config()
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.code_2fa = cfg["code_2fa"]
        self.session = requests.session()
        self.cookie = (
            tempfile.gettempdir() + "/" + self.cookie + "_" + self.username
        )
        if os.path.exists(self.cookie):
            if DEBUG:
                print(f"Reusing 🍪 ({self.cookie})-> ", end="", flush=True)
            with open(self.cookie, "rb") as _file:
                self.session.cookies.update(pickle.load(_file))
            try:
                page = self.session.get(self.url_base)
            except requests.exceptions.ConnectionError:
                print(f"Connection problem to {self.url_base}!", flush=True)
                sys.exit(2)
            reg = r">(Miners)<"
            match = re.findall(reg, page.content.decode("utf-8"))
            self.logged = match
            debug(match)
            if match:
                return
        self.pre_login()

    def wallet(self, crypto):
        """Get Wallet information"""
        if not self.logged:
            return -1, -1
        if DEBUG:
            print("Wallet 💰-> ", end="", flush=True)
        url = self.url_base + "/wallet/stake/" + crypto.lower()
        page = self.session.get(url)
        reg1 = rf'<h1 class="color-white font-30">(\d+.\d+).*<\/h1>'
        reg2 = r'<h1 class="color-white font-30">\$(.+)<\/h1>'
        reg = reg1 + r"\n.*" + reg2
        parse = re.findall(reg, page.content.decode("utf-8"))
        if DEBUG > 1:
            print(
                "\nwallet-PAGE-SESSION-GET:\n\n",
                page.content.decode("utf-8"),
                flush=True,
            )
        debug(parse)
        if parse:
            _val = float(parse[0][0])
            _usd = float(parse[0][1].replace(',', ''))
        else:
            print(f"{TAG[0]} Can't get crypto info", flush=True)
            raise CantGetUSDandBTC
        return _val, _usd


DEBUG = 0
TAG = ["✖", "✔"]

if __name__ == "__main__":
    crypto = sys.argv[1] if len(sys.argv) == 2 else 'BTC'
    try:
        cacpanel = CACPanel()
        val, usd = cacpanel.wallet(crypto)
    except CantGetCsrf:
        sys.exit(3)
    except CantGetUSDandBTC:
        sys.exit(5)
    except MaintenanceMode:
        sys.exit(6)
    else:
        print(f"{crypto}: {val:1.8f} USD: {usd:05.2f}", flush=True)
