import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--silent', action='store_true', type=bool)
args = parser.parse_args()
silent = args.silent
print(silent)
