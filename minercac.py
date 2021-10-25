#!/usr/bin/python3
""" miner.py - get information from CAC
    v0.1.1 - 2021-10-24 - nelbren@nelbren.com"""
import re
import os
import sys
import pickle
import configparser
import tempfile
import requests

class Error(Exception):
    '''Base class for other exceptions'''

class CantGetCsrf(Error):
    '''Raised when Can't get _csrf'''

class CantGetUSDandBTC(Error):
    '''Raised when Can't get usd and btc'''

def debug(is_ok):
    '''Show tag'''
    if DEBUG:
        tag = 1 if is_ok else 0
        print(f'{TAG[tag]} ', end='')

def check_config(path, filename):
    '''Check if config file exist'''
    if not os.path.exists(path + '/' + filename):
        print(f'Create the file "{filename}" using the template "secret.cfg.EXAMPLE"!')
        sys.exit(1)

class CACPanel:
    '''Class to manage the access to CAC Panel'''
    url_base = 'https://wallet.cloudatcost.com'
    cookie = '.wallet_cloudatcost.cookie'
    logged = False

    def login(self):
        '''Login process'''
        if DEBUG:
            print('Login -> ', end='')
        data = { 'email': self.username, 'password': self.password, '_csrf': self._csrf }
        headers = {
            'accept-language':'en-US,en;q=0.9,es;q=0.8',
            'accept-encoding':'gzip, deflate, br',
            'content-type':'application/x-www-form-urlencoded',
            'connection':'keep-alive',
            'origin':'https://wallet.cloudatcost.com',
            'referer':'https://wallet.cloudatcost.com/login',
            'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36'
        }
        url = self.url_base + '/login'
        self.session.post(url, data=data, headers=headers)
        with open(self.cookie, 'wb') as _file:
            pickle.dump(self.session.cookies, _file)
        page = self.session.get(self.url_base)
        reg = r'>(Miners)<'
        match = re.findall(reg, page.content.decode('utf-8'))
        self.logged = match
        debug(self.logged)

    def pre_login(self):
        '''Pre-login process'''
        if DEBUG:
            print('Pre-login -> ', end='')
        url = self.url_base + '/login'
        page = self.session.get(url)
        reg = r'_csrf" value="([^"]+)"'
        match = re.findall(reg, page.content.decode('utf-8'))
        debug(match)
        if match:
            self._csrf = match[0]
            self.login()
        else:
            print(f'{TAG[0]} Can\'t get _csrf')
            raise CantGetCsrf

    def __init__(self):
        config = configparser.ConfigParser()
        path = os.path.dirname(os.path.realpath(__file__))
        filename = '.secret.cfg'
        check_config(path, filename)
        config.read_file(open(path + '/' + filename))
        self.username = config.get('CAC_WALLET', 'USERNAME')
        self.password = config.get('CAC_WALLET', 'PASSWORD')
        self.session = requests.session()
        self.cookie = tempfile.gettempdir() + '/' + self.cookie
        if os.path.exists(self.cookie):
            if DEBUG:
                print('Reusing 🍪-> ', end='')
            with open(self.cookie, 'rb') as _file:
                self.session.cookies.update(pickle.load(_file))
            page = self.session.get(self.url_base)
            reg = r'>(Miners)<'
            match = re.findall(reg, page.content.decode('utf-8'))
            debug(match)
            if match:
                return
        self.pre_login()

    def wallet(self):
        '''Get Wallet information'''
        if DEBUG:
            print('Wallet 💰-> ', end='')
        url = self.url_base + '/wallet'
        page = self.session.get(url)
        reg = r'font-30">\$(?P<usd>.+)&nbsp;USD</h1>\n.*font-30">(?P<btc>.+)&nbsp;BTC<'
        parse = re.search(reg, page.content.decode('utf-8'))
        debug(parse)
        if parse:
            _usd = float(parse.groupdict()['usd'])
            _btc = float(parse.groupdict()['btc'])
        else:
            print(f'{TAG[0]} Can\'t get get crypto info')
            raise CantGetUSDandBTC
        return _btc, _usd

DEBUG = 0
TAG = ['✖', '✔']

if __name__ == '__main__':
    cacpanel = CACPanel()
    try:
        btc, usd = cacpanel.wallet()
    except CantGetCsrf:
        print(f'{TAG[0]} Can\'t get _csrf')
    except CantGetUSDandBTC:
        print(f'{TAG[0]} Can\'t get crypto info')
    else:
        print(f'BTC: {btc:1.8f} USD: {usd:05.2f}')
