import argparse
import argcomplete
import csv

from pathlib import Path
from tqdm import tqdm

import mci.process as process
from mci.run_stanza import init_stanza
from mci.procedure import MorphologicalAnalyzer, LemmaNormalizer

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LANGUAGE_TO_JSON = {
    "en": {
        "nouns": str(BASE_DIR / "source/dictionaries/en_nouns.json"),
        "verbs": str(BASE_DIR / "source/dictionaries/en_verbs.json"),
        "adjs": str(BASE_DIR / "source/dictionaries/placeholder.json")
    },
    "it": {
        "nouns": str(BASE_DIR / "source/dictionaries/it_nouns.json"),
        "verbs": str(BASE_DIR / "source/dictionaries/it_verbs.json"),
        "adjs": str(BASE_DIR / "source/dictionaries/it_adj.json")
    },
    "de": {
        "nouns": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "verbs": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "adjs": str(BASE_DIR / "source/dictionaries/placeholder.json")
    },
    "fr": {
        "nouns": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "verbs": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "adjs": str(BASE_DIR / "source/dictionaries/placeholder.json")
    },
    "es": {
        "nouns": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "verbs": str(BASE_DIR / "source/dictionaries/placeholder.json"),
        "adjs": str(BASE_DIR / "source/dictionaries/placeholder.json")
    },
}

def _exp(args):
    nlp = init_stanza(args.language)

    for input_file in tqdm(args.input_files):
        input_path = Path(input_file).resolve()
        target_dir = Path(args.output_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / f"{input_path.stem}_exponents.csv"
        
        # Run stanza to process the input file
        with open(input_path, "r", encoding="utf-8") as fh:
            text = fh.read()
            doc = nlp(text)
            stanza_output = doc.to_dict()
        
        lang_files = LANGUAGE_TO_JSON[args.language]

        normalizer = LemmaNormalizer(BASE_DIR / "source/dictionaries/norm_lemma.json")

        analyzer_verbs = MorphologicalAnalyzer(lang_files["verbs"])
        analyzer_nouns = MorphologicalAnalyzer(lang_files["nouns"])
        analyzer_adj = MorphologicalAnalyzer(lang_files["adjs"])

        with open(output_path, "w", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["form", "lemma", "pos", "V_exp", "N_exp", "A_exp", "check"])  # Header

            for sentence in stanza_output:
                sentence_data = process.process_sentence(sentence, (analyzer_verbs, analyzer_nouns, analyzer_adj), args.language, normalizer)
                rows = zip(*sentence_data)  # Transpose sentence_data to match columns
                writer.writerows(rows)

def _mci(args):
    print("filename\toverall_mci\tnoun_mci\tverb_mci")
    for input_file in args.input_files:
        input_path = Path(input_file).resolve()
        overall_mci, noun_mci, verb_mci, adj_mci = process.calculate_index(input_path, args.n_samples, args.size, args.seed) 
        print(f"{input_path.stem}\t{overall_mci:.4f}\t{verb_mci:.4f}\t{noun_mci:.4f}\t{adj_mci:.4f}")

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
         help="Input a number of random samples. Default is 100.")
    
    parser_mci.add_argument("--size",
         type=int,
         default=10,
         help="Input the size of the exponent samples. Default is 10.")
    
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