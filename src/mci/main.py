import argparse
import argcomplete
from pathlib import Path

import pandas as pd

import mci.process as process
import mci.run_stanza as run_stanza
from mci.procedure import MorphologicalAnalyzer

LANGUAGE_TO_JSON = {
    "en": {
        "nouns": "source/dictionaries/en_nouns.json",
        "verbs": "source/dictionaries/en_verbs.json",
        "adjs": "source/dictionaries/placeholder_adjs.json",
    },
    "it": {
        "nouns": "source/dictionaries/placeholder_nouns.json",
        "verbs": "source/dictionaries/placeholder_verbs.json",
        "adjectives": "source/dictionaries/placeholder_adjs.json",
    },
    "de": {
        "nouns": "source/dictionaries/placeholder_nouns.json",
        "verbs": "source/dictionaries/placeholder_verbs.json",
        "adjectives": "source/dictionaries/placeholder_adjs.json",
    },
    "fr": {
        "nouns": "source/dictionaries/placeholder_nouns.json",
        "verbs": "source/dictionaries/placeholder_verbs.json",
        "adjectives": "source/dictionaries/placeholder_adjs.json",
    },
    "es": {
        "nouns": "source/dictionaries/placeholder_nouns.json",
        "verbs": "source/dictionaries/placeholder_verbs.json",
        "adjectives": "source/dictionaries/placeholder_adjs.json",
    },
}

def _exp(args):
    for input_file in args.input_files:
        input_path = Path(input_file).resolve()
        output_path = Path(args.output_dir).resolve() / f"{input_path.stem}_exponents.tsv"
        
        # Run stanza to process the input file
        with open(input_path, "r", encoding="utf-8") as fh:
            text = fh.read()
            stanza_output = run_stanza.run_stanza(text, args.language)
        
        lang_files = LANGUAGE_TO_JSON[args.language]

        analyzer_nouns = MorphologicalAnalyzer(lang_files["nouns"])
        analyzer_verbs = MorphologicalAnalyzer(lang_files["verbs"])

        forms, lemmas, poss, exp_nouns, exp_verbs, checks = [], [], [], [], [], []

        for sentence in stanza_output:
            sentence_data = process.process_sentence(sentence, (analyzer_nouns, analyzer_verbs))
            for col, sentence_col in zip([forms, lemmas, poss, exp_nouns, exp_verbs, checks], sentence_data):
                col.extend(sentence_col)

        df = pd.DataFrame({
            "form": forms,
            "lemma": lemmas,
            "pos": poss,
            "V_exp": exp_verbs,
            "N_exp": exp_nouns,
            "check": checks
        })
        df.to_csv(output_path, index=False)

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
    parser_exp.add_argument("-l", "--language",
        choices=["en", "de", "it", "fr", "es"],
        type=str,
        required=True,
        help="Input language. Supported languages: en, de, it, fr, es")

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