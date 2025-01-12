import random
import re
from typing import List

from textcomplexity.utils import conllu
from textcomplexity.utils.text import Text
from textcomplexity.utils.token import Token

# functions to read conllu tokens
def read_conllu_tokens(f, *, ignore_case=False):
    for sentence, _ in conllu._read_conllu(f, ignore_case):
        for token in get_tokens(sentence):
            yield token

def get_tokens(sentence):
    # NOTE: this ignores range tokens and keeps splits multiword lemmas
    simple_id = re.compile(r"^\d+$")
    return [token for token in sentence if simple_id.search(token.id)]

# this function needs to be fixed
def compute_exponent(form: str, lemma: str) -> str:
    if form == lemma:
        return "Ø"
    else:
        # Check for suffixes or differences at the end of the form
        if form.startswith(lemma):
            return form[len(lemma):] or "∅"
        # Otherwise, identify the full difference
        return form.replace(lemma, "", 1) or "∅"

# Function to extract random samples of exponents
def random_samples(exponents: List[str], x: int, y: int) -> List[List[str]]:
    return [random.sample(exponents, y) for _ in range(x)]

# Function to calculate the mean length of unique exponents in samples
def mean_unique_lengths(samples: List[List[str]]) -> float:
    unique_lengths = [len(set(sample)) for sample in samples]
    return sum(unique_lengths) / len(unique_lengths)

# Function to compute symmetric difference across samples
def symmetric_difference(samples: List[List[str]]) -> float:
    total_difference = 0
    for i, sample_i in enumerate(samples):
        for j, sample_j in enumerate(samples):
            if i != j:
                total_difference += len(set(sample_i).symmetric_difference(set(sample_j)))

    num_comparisons = len(samples) * (len(samples) - 1)
    return total_difference / num_comparisons if num_comparisons > 0 else 0