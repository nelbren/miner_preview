#!/usr/bin/python3
""" lint.py v1.1 from:
    https://towardsdatascience.com/keep-your-code-clean-using-\
    black-pylint-git-hooks-pre-commit-baf6991f7376 """
import sys
import argparse
import logging
import subprocess

# from datetime import datetime
import anybadge
from pylint.lint import Run


def lint():
    """Lint"""
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(prog="LINT")

    parser.add_argument(
        "-p",
        "--path",
        help="path to directory you want to run pylint | "
        "Default: %(default)s | Type: %(type)s ",
        default="./src",
        type=str,
    )

    parser.add_argument(
        "-t",
        "--threshold",
        help="score threshold to fail pylint runner | "
        "Default: %(default)s | Type: %(type)s ",
        default=10,
        type=float,
    )

    args = parser.parse_args()
    path = str(args.path)
    threshold = float(args.threshold)

    logging.info("PyLint | Path: %s | Threshold: %s ", path, threshold)

    results = Run([path], do_exit=False)
    final_score = results.linter.stats["global_note"]

    message = f"Score: {final_score} | Threshold: {threshold} "
    if final_score < threshold:
        message = "PyLint Failed | " + message
        logging.error(message)
        raise Exception(message)

    message = "PyLint Passed | " + message
    logging.info(message)

    # Define thresholds: <2=red, <4=orange <8=yellow <10=green
    thresholds = {2: "red", 4: "orange", 6: "yellow", 10: "green"}

    badge = anybadge.Badge(
        "pylint", final_score, thresholds=thresholds, value_format="%.2f"
    )
    badge.write_badge("images/pylint.svg", overwrite=True)

    result = subprocess.run(
        ["python3", "-V"], stdout=subprocess.PIPE, check=True
    )
    version = result.stdout.decode().split()[1]
    badge = anybadge.Badge("python", version, default_color="green")
    badge.write_badge("images/python.svg", overwrite=True)

    # TS_FMT = "%Y-%m-%d %H:%M:%S"
    # timestamp = datetime.now().strftime(TS_FMT)
    # badge = anybadge.Badge("updated", timestamp, default_color="green")
    # badge.write_badge("images/updated.svg", overwrite=True)

    sys.exit(0)


if __name__ == "__main__":
    lint()
