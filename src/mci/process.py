import random
import csv
from typing import List, Tuple

def process_sentence(sentence, analyzers, language, normalizer):
    """Process a single sentence and extract required data."""
    forms, lemmas, poss, exp_verbs, exp_nouns, exp_adj, checks = ["[S_START]"], [""], [""], [""], [""], [""], [""]
    analyzer_verbs, analyzer_nouns, analyzer_adj = analyzers

    for token in sentence:
        if isinstance(token.get('id'), int):
            lemma = token.get("lemma", "").lower()
            form = token.get("text", "").lower()
            upos = token.get("upos", "")
            xpos = token.get("xpos", "")
            pos = '_'.join(filter(None, [upos, xpos]))
            feat = token.get("feats", "")

            lemma = normalizer.normalize_lemma(lemma, language)

            forms.append(token.get("text", ""))
            lemmas.append(token.get("lemma", ""))
            poss.append(pos)

            deprel = token.get("deprel", "")
            deps = [dep.get("text", "").lower() for dep in sentence if dep.get("head") == token.get("id")]
            
            # Check conditions for verbs
            check = "*" if (upos == "VERB" and (deprel == "amod" or any(dep in ["det", "det:poss", "det:predet"] for dep in deps))) else ""
            checks.append(check)

            exp_verbs.append(analyzer_verbs.extract_exponent(form, lemma, upos, feat) if (upos in ["VERB", "AUX"] and check == "") else "")
            exp_nouns.append(analyzer_nouns.extract_exponent(form, lemma, upos, feat) if upos == "NOUN" else "")
            exp_adj.append(analyzer_adj.extract_exponent(form, lemma, upos, feat) if upos == "ADJ" else "")


    # Add sentence end markers
    forms.append("[S_END]")
    lemmas.append("")
    poss.append("")
    exp_verbs.append("")
    exp_nouns.append("")
    exp_adj.append("")
    checks.append("")

    return forms, lemmas, poss, exp_verbs, exp_nouns, exp_adj, checks

def read_csv(file_path: str) -> Tuple[List[str], List[str]]:
    """
    Reads a CSV file and extracts the columns 'N_exp' and 'V_exp' as lists of strings.
    Empty strings are discarded.

    :param file_path: Path to the CSV file.
    :return: Tuple containing two lists of strings (N_exp and V_exp).
    """
    v_exp, n_exp, a_exp = [], [], []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['V_exp']:
                v_exp.append(row['V_exp'])
            if row['N_exp']:
                n_exp.append(row['N_exp'])
            if row['A_exp']:
                v_exp.append(row['A_exp'])
    return v_exp, n_exp, a_exp

def random_samples(exponents: List[str], n_samples: int, size: int, seed: int = None) -> List[List[str]]:
    """
    Extracts random samples of exponents with a deterministic seed.

    :param exponents: List of exponents.
    :param n_samples: Number of samples.
    :param size: Size of each sample.
    :param seed: Seed for random sampling.
    :return: List of sampled exponents.
    """
    if seed is not None:
        random.seed(seed)
    return [[random.choice(exponents) for _ in range(size)] for _ in range(n_samples)]

def mean_unique_lengths(samples: List[List[str]]) -> float:
    """
    Calculates the mean length of unique exponents in samples.

    :param samples: List of samples.
    :return: Mean length of unique exponents.
    """
    unique_lengths = [len(set(sample)) for sample in samples]
    return sum(unique_lengths) / len(unique_lengths)

def symmetric_difference(samples: List[List[str]]) -> float:
    """
    Computes the symmetric difference across samples.

    :param samples: List of samples.
    :return: Average symmetric difference.
    """
    total_difference = 0
    for i, sample_i in enumerate(samples):
        for j, sample_j in enumerate(samples):
            if i != j:
                total_difference += len(set(sample_i).symmetric_difference(set(sample_j)))

    num_comparisons = len(samples) * (len(samples) - 1)
    return total_difference / num_comparisons if num_comparisons > 0 else 0

def calculate_index(file_path: str, n_samples: int, size: int, seed: int = None) -> float:
    """
    Calculates the final index based on the chained functions.

    :param file_path: Path to the CSV file.
    :param n_samples: Number of samples.
    :param size: Size of each sample.
    :param seed: Seed for random sampling.
    :return: Computed index value.
    """
    # Step 1: Read the CSV file
    v_exp, n_exp, a_exp = read_csv(file_path)

    # Step 2: Combine the two lists
    exponents = v_exp + n_exp + a_exp

    # Step 3: Generate random samples
    v_exp_samples = random_samples(v_exp, n_samples, size, seed)
    n_exp_samples = random_samples(n_exp, n_samples, size, seed)
    a_exp_samples = random_samples(a_exp, n_samples, size, seed)
    samples = random_samples(exponents, n_samples, size, seed)

    # Step 4: Calculate mean unique lengths and symmetric difference
    v_exp_mean_len = mean_unique_lengths(v_exp_samples)
    n_exp_mean_len = mean_unique_lengths(n_exp_samples)
    a_exp_mean_len = mean_unique_lengths(a_exp_samples)
    mean_len = mean_unique_lengths(samples)
    v_exp_sym_diff = symmetric_difference(v_exp_samples)
    n_exp_sym_diff = symmetric_difference(n_exp_samples)
    a_exp_sym_diff = symmetric_difference(a_exp_samples)
    sym_diff = symmetric_difference(samples)

    # Step 5: Compute the final index
    v_exp_index = (v_exp_mean_len + (v_exp_sym_diff / 2)) - 1
    n_exp_index = (n_exp_mean_len + (n_exp_sym_diff / 2)) - 1
    a_exp_index = (a_exp_mean_len + (a_exp_sym_diff / 2)) - 1
    index = (mean_len + (sym_diff / 2)) - 1
    return index, v_exp_index, n_exp_index, a_exp_index