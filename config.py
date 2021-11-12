#!/usr/bin/python3
""" config.py - get configuration
    v0.0.3 - 2021-11-06 - nelbren@nelbren.com """
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
    section = "CLOUDATCOST"
    username = config.get(section, "USERNAME", fallback=None)
    password = config.get(section, "PASSWORD", fallback=None)
    code_2fa = config.get(section, "CODE_2FA", fallback=None)
    cac_goal_usd = config.get(section, "GOAL_USD", fallback=None)
    cac_goal_btc = config.get(section, "GOAL_BTC", fallback=None)
    section = "ETHERMINE"
    address = config.get(section, "ADDRESS", fallback=None)
    etm_goal_usd = config.get(section, "GOAL_USD", fallback=None)
    etm_goal_btc = config.get(section, "GOAL_ETH", fallback=None)
    section = "MAIL"
    mail_from = config.get(section, "FROM", fallback=None)
    mail_to = config.get(section, "TO", fallback=None)
    return {
        "username": username,
        "password": password,
        "code_2fa": code_2fa,
        "cac_goal_usd": cac_goal_usd,
        "cac_goal_btc": cac_goal_btc,
        "address": address,
        "etm_goal_usd": etm_goal_usd,
        "etm_goal_btc": etm_goal_btc,
        "mail_from": mail_from,
        "mail_to": mail_to,
    }
