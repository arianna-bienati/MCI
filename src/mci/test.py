# import json
from pathlib import Path
# import mci.process as process
import conllu
import pandas as pd

def extract_regular_exponent_v1(form: str, lemma: str) -> str:
    """Extract regular exponent by comparing form and lemma."""
    # Check if form exactly matches lemma
    if form == lemma:
         return 'Ø'

    # Find the longest common prefix
    i = 0
    min_len = min(len(form), len(lemma))
    while i < min_len and form[i] == lemma[i]:
         i += 1

    # If we found a common prefix, the exponent is the remaining part of the form
    if i > 0:
         return form[i:]

    # If no match found, return the whole form as exponent
    return form

def extract_regular_exponent_v2(form, lemma):
    if form == lemma:
        return "Ø"
    elif form.startswith(lemma):
        return form[len(lemma):] or "Ø"
    else:
        return form.replace(lemma, "", 1) or "Ø"

input_file = Path("/Users/ariannabienati/git/ICLE500/texts_conllu/001_BGSU1004.txt.conllu")

with open(input_file, "r", encoding="utf-8") as f:
        data = conllu.parse(f.read())

forms = []
lemmas = []
poss = []
exp_nouns = []
exp_verbs = []

for sentence in data:
    forms.append("[S_START]")
    lemmas.append("")
    poss.append("")
    exp_nouns.append("")
    exp_verbs.append("")
    for token in sentence:
        lemma = token.get("lemma")
        lemmas.append(lemma)
        form = token.get("form")
        forms.append(form)
        form = form.lower()
        upos = token.get("upos") or ""
        xpos = token.get("xpos") or ""
        pos = '_'.join((upos, xpos))
        poss.append(pos)
        if token["upos"] in ["NOUN"]:
            exp_noun = extract_regular_exponent_v2(form, lemma)
            exp_nouns.append(exp_noun)
        else:
             exp = ""
             exp_nouns.append(exp)
        if token["upos"] in ["VERB", "AUX"]:
            exp_verb = extract_regular_exponent_v2(form, lemma)
            exp_verbs.append(exp_verb)
        else:
            exp = ""
            exp_verbs.append(exp)
    forms.append("[S_END]")
    lemmas.append("")
    poss.append("")
    exp_nouns.append("")
    exp_verbs.append("")

df = pd.DataFrame({
    "form": forms,
    "lemma": lemmas,
    "pos": poss,
    "V_exp": exp_verbs,
    "N_exp": exp_nouns
})

df.to_csv('target/out.csv', index=False)