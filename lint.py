""" lint.py v1.0 from:
    https://towardsdatascience.com/keep-your-code-clean-using-\
    black-pylint-git-hooks-pre-commit-baf6991f7376 """
import sys
import argparse
import logging
import subprocess
import anybadge
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

# Define thresholds: <2=red, <4=orange <8=yellow <10=green
thresholds = {2: "red", 4: "orange", 6: "yellow", 10: "green"}

badge = anybadge.Badge(
    "pylint", final_score, thresholds=thresholds, value_format="%.2f"
)
badge.write_badge("images/pylint.svg", overwrite=True)

result = subprocess.run(["python", "-V"], stdout=subprocess.PIPE, check=True)
version = result.stdout.decode().split()[1]
badge = anybadge.Badge("python", version, default_color="green")
badge.write_badge("images/python.svg", overwrite=True)

sys.exit(0)
