""" lint.py v1.0 from:
    https://towardsdatascience.com/keep-your-code-clean-using-\
    black-pylint-git-hooks-pre-commit-baf6991f7376 """
import sys
import argparse
import logging
from pylint.lint import Run

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
    default=7,
    type=float,
)

args = parser.parse_args()
PATH = str(args.path)
threshold = float(args.threshold)

logging.info("PyLint Starting | Path: %s | Threshold: %s ", PATH, threshold)

results = Run([PATH], do_exit=False)
final_score = results.linter.stats["global_note"]

MESSAGE = f"Score: {final_score} | Threshold: {threshold} "
if final_score < threshold:
    MESSAGE = "PyLint Failed | " + MESSAGE
    logging.error(MESSAGE)
    raise Exception(MESSAGE)

MESSAGE = "PyLint Passed | " + MESSAGE
logging.info(MESSAGE)
sys.exit(0)
