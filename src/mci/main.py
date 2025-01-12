import argparse
import argcomplete
from pathlib import Path

from tqdm.auto import tqdm

import mci.process as process

def _exp(args):
	# Create output dir if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Use tqdm for progress tracking if there are multiple files
    for input_file in tqdm(args.input_files, desc="Analysing files"):
        input_path = Path(input_file).resolve()
        output_file = output_dir / f"{input_path.stem}_{input_path.suffix}"
        process.annotate_pii(input_path, output_file)
        print(f"Annotated and saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Extract morphological exponents and compute the Morphological Complexity Index (MCI)",
        add_help=True)
    
    argcomplete.autocomplete(parser)

    subparsers = parser.add_subparsers(title="actions", dest="actions")
    
    parser_exp = subparsers.add_parser('exp',
        description='Extract morphological exponents from conllu files',
        help='Extract morphological exponents from conllu files')
    
    parser_exp.add_argument("-o", "--output_dir",
        type=str,
        default=".",
        help="Output directory. Default: Current directory.")
    
    parser_exp.add_argument("-i", "--input_files",
        type=str,
        nargs="+",
        required=True,
        help="Input text files.")

    parser_exp.set_defaults(func=_exp)

    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_usage()
        exit(1)

    args.func(args)

if __name__ == "__main__":
    main()