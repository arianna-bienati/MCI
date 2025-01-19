import argparse
import argcomplete
from pathlib import Path

import mci.process as process

# TODO: make a command line interface for extracting exponents
# functionalities: 
# a) runs stanza given the 'input_files' and 'language' parameter,
# b) activates the MorphologicalAnalyzer with corresponding json files given the 'language' parameter,
# c) analyzes conllu texts, 
# d) returns csv or tsv files with form, lemma, pos, exponents, flags.

def _exp(args):
    pass

def _mci(args):
    print("filename\toverall_mci\tnoun_mci\tverb_mci")
    for input_file in args.input_files:
        input_path = Path(input_file).resolve()
        overall_mci, noun_mci, verb_mci = process.calculate_index(input_path, args.n_samples, args.size, args.seed) 
        print(f"{input_path.stem}\t{overall_mci:.4f}\t{noun_mci:.4f}\t{verb_mci:.4f}")

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
    
    # TODO: relate json files to language
    parser_exp.add_argument("-lang", "--language",
        type=str,
        required=True,
        help="Input language of the texts")

    parser_exp.set_defaults(func=_exp)

    parser_mci = subparsers.add_parser('mci',
          description='Compute MCI from csv files',
          help='Compute MCI from csv files')
    
    parser_mci.add_argument("-i", "--input_files",
         type=str,
         nargs="+",
         required=True,
         help="Input csv files with at least the following columns: N_exp, V_exp")
    
    parser_mci.add_argument("--n_samples",
         type=int,
         default=100,
         help="Input a number of random samples")
    
    parser_mci.add_argument("--size",
         type=int,
         default=10,
         help="Input the size of the exponent samples")
    
    parser_mci.add_argument("--seed",
         type=int,
         required=False,
         help="Optional: make the run deterministic")

    parser_mci.set_defaults(func=_mci)

    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_usage()
        exit(1)

    args.func(args)

if __name__ == "__main__":
    main()