"""Command-line interface for the Vocaloid integrity checker."""

import argparse
import json
import ntpath
import sys

from .checker import check


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vocaloid-integrity-check",
        description="Vocaloid integrity checker. Checks the integrity of a Vocaloid voicebank.",
    )
    parser.add_argument("ddi", help="path to the .ddi file")
    parser.add_argument("--ddb", help="the .ddb filename or path in the same voicebank")
    parser.add_argument("--json", action="store_true", help="output JSON")
    args = parser.parse_args(argv)

    stem = ntpath.splitext(ntpath.basename(args.ddb or args.ddi))[0]
    try:
        with open(args.ddi, "rb") as fh:
            result = check(fh.read(), stem)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["status"])
        if result.get("stored"):
            print(f'  name   : {result["stem"]}  (root {result["root"]})')
            print(f'  stored : {result["stored"]}')
        if result.get("computed"):
            print(f'  expect : {result["computed"]}')
        if result.get("note"):
            print(f'  note   : {result["note"]}')
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
