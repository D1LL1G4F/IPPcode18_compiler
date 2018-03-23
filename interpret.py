import sys
import argparse


def argumentsHadling():
    parser = argparse.ArgumentParser(prog="interpret.py", add_help=True)
    parser.add_argument("--source", required=True, nargs=1, metavar="FILE",
                        help="input file with XML representation of src code")
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(10)

    return args


def main():
    args = argumentsHadling()
    print(args.source)


if __name__ == '__main__':
    main()
