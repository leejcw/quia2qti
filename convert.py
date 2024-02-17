import argparse
from enum import Enum
import json

import md
import quia
import qti

class InputMode(Enum):
    quia = "quia"
    json = "json"

class OutputMode(Enum):
    test = "test"
    json = "json"
    qti = "qti"
    markdown = "markdown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_format", type=InputMode, help="Input file format")
    parser.add_argument("in_file", type=str, help="Source file name")
    parser.add_argument("out_format", type=OutputMode, help="Output file format")
    parser.add_argument("out_file", type=str, help="Output file name", nargs='?')
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.out_format != "test":
        assert args.out_file, "Output file must be specified"

    if args.in_format == InputMode.quia:
        extracted_assessment = quia.html_to_json(args.in_file, args.verbose)
    if args.in_format == InputMode.json:
        with open(args.in_file) as f:
            extracted_assessment = json.load(f)
    assert extracted_assessment

    if args.out_format == OutputMode.json:
        with open(args.out_file, "w") as f:
            f.write(json.dumps(extracted_assessment))

    if args.out_format == OutputMode.qti:
        # TODO: package multiple assessments at once
        qti.json_to_qti_zip([extracted_assessment], args.out_file)

    if args.out_format == OutputMode.markdown:
        with open(args.out_file, "w") as f:
            f.write(md.transform(extracted_assessment))

if __name__ == "__main__":
    main()
