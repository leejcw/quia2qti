import argparse
import json
import os
import pathlib
import subprocess
import tqdm
import traceback

import md
import quia
import qti


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", type=str, help="Quia HTML file")
    group.add_argument("-d", "--dir", type=str, help="Directory of Quia HTML files")
    
    parser.add_argument("--debug_json", action="store_true", help="Save the intermediate json")
    parser.add_argument("--debug_markdown", action="store_true", help="Save the intermediate markdown")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print the parsed assessments")
    args = parser.parse_args()

    assert args.file or args.dir, "Input files must be provided"

    if args.file:
        file_path = os.path.splitext(args.file)[0]
        try:
            extracted = quia.html_to_json(args.file, args.verbose)
        except Exception:
            print(f"Failed to extract {args.file}\n", traceback.format_exc())
            exit(1)
        process_assessment(file_path, extracted, args)

    if args.dir:
        html_files = []
        for path, _, files in os.walk(args.dir):
            html_files.extend([os.path.join(path, f) for f in files if f.endswith(".html") and not f.endswith("saved_resource.html")])

        for f in tqdm.tqdm(html_files):
            try:
                extracted = quia.html_to_json(f, args.verbose)
            except Exception:
                print(f"Failed to extract {f}\n", traceback.format_exc())
                continue
            process_assessment(f, extracted, args)


def process_assessment(file_path, extracted_assessment, args):
    if args.debug_json:
        with open(file_path + ".json", "w") as f:
            f.write(json.dumps(extracted_assessment))

    with open(file_path + ".md", "w") as f:
        f.write(md.transform(extracted_assessment))

    try:
        subprocess.check_call(["text2qti", file_path + ".md"])
    except:
        print(f"Failed to convert {file_path}.html to QTI")

    if not args.debug_markdown:
        os.remove(file_path + ".md")


if __name__ == "__main__":
    main()
