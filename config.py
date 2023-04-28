#!/usr/bin/python3
""" config.py - get configuration
    v0.0.7 - 2023-04-28 - nelbren@nelbren.com """
import os
import sys
import configparser


def check_config(path, filename):
    """Check if config file exist"""
    if not os.path.exists(path + "/" + filename):
        print(
            f'Create the file "{filename}" using the '
            'template "secret.cfg.EXAMPLE"!'
        )
        sys.exit(1)


def get_config():
    """Get config"""
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    filename = ".secret.cfg"
    check_config(path, filename)
    config.read(path + "/" + filename)
    section = "CRYPTOATCOST"
    hostname = config.get(section, "HOSTNAME", fallback=None)
    username = config.get(section, "USERNAME", fallback=None)
    password = config.get(section, "PASSWORD", fallback=None)
    code_2fa = config.get(section, "CODE_2FA", fallback=None)
    cac_goal_usd = config.get(section, "GOAL_USD", fallback=None)
    cac_goal_btc = config.get(section, "GOAL_BTC", fallback=None)
    cac_goal_cct = config.get(section, "GOAL_CCT", fallback=None)
    section = "ETHERMINE"
    address = config.get(section, "ADDRESS", fallback=None)
    etm_goal_usd = config.get(section, "GOAL_USD", fallback=None)
    etm_goal_btc = config.get(section, "GOAL_ETH", fallback=None)
    section = "NICEHASH"
    nch_org = config.get(section, "ORG", fallback=None)
    nch_key = config.get(section, "KEY", fallback=None)
    nch_secret = config.get(section, "SECRET", fallback=None)
    nch_goal_usd = config.get(section, "GOAL_USD", fallback=None)
    nch_goal_btc = config.get(section, "GOAL_BTC", fallback=None)
    section = "MAIL"
    mail_from = config.get(section, "FROM", fallback=None)
    mail_to = config.get(section, "TO", fallback=None)
    section = "TELEGRAM"
    telegram_token = config.get(section, "TOKEN", fallback=None)
    telegram_id = config.get(section, "ID", fallback=None)
    return {
        "hostname": hostname,
        "username": username,
        "password": password,
        "code_2fa": code_2fa,
        "cac_goal_usd": cac_goal_usd,
        "cac_goal_btc": cac_goal_btc,
        "cac_goal_cct": cac_goal_cct,
        "address": address,
        "etm_goal_usd": etm_goal_usd,
        "etm_goal_btc": etm_goal_btc,
        "nch_org": nch_org,
        "nch_key": nch_key,
        "nch_secret": nch_secret,
        "nch_goal_usd": nch_goal_usd,
        "nch_goal_btc": nch_goal_btc,
        "mail_from": mail_from,
        "mail_to": mail_to,
        "telegram_token": telegram_token,
        "telegram_id": telegram_id,
    }
