from pathlib import Path
import conllu
import pandas as pd

from eng_procedure import MorphologicalAnalyzer

def extract_regular_exponent_v2(form, lemma):
    if form == lemma:
        return "Ø"
    elif form.startswith(lemma):
        return form[len(lemma):] or "Ø"
    else:
        return form.replace(lemma, "", 1) or "Ø"

input_file = Path("source/001_BGSU1004.txt.conllu")
analyzer_nouns = MorphologicalAnalyzer("source/dictionaries/en_nouns.json")
analyzer_verbs = MorphologicalAnalyzer("source/dictionaries/en_verbs.json")

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
        if isinstance(token.get('id'), int):
            lemma = token.get("lemma")
            lemmas.append(lemma)
            lemma = lemma.lower()
            form = token.get("form")
            forms.append(form)
            form = form.lower()
            upos = token.get("upos") or ""
            xpos = token.get("xpos") or ""
            pos = '_'.join((upos, xpos))
            poss.append(pos)
            if token["upos"] in ["NOUN"]:
                exp_noun = analyzer_nouns.extract_exponent(form, lemma, upos)
                exp_nouns.append(exp_noun)
            else:
                exp = ""
                exp_nouns.append(exp)
            if token["upos"] in ["VERB", "AUX"]:
                exp_verb = analyzer_verbs.extract_exponent(form, lemma, upos)
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

target = Path("target/")
target.mkdir(parents=True, exist_ok=True)
df.to_csv('target/out.csv', index=False)