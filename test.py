from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-b", nargs='*', action='append')
args = parser.parse_args()
print(args.b)