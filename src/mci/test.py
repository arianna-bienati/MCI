import sys
from pathlib import Path
import conllu
import pandas as pd
from eng_procedure import MorphologicalAnalyzer

def process_sentence(sentence, analyzers):
    """Process a single sentence and extract required data."""
    forms, lemmas, poss, exp_nouns, exp_verbs, checks = ["[S_START]"], [""], [""], [""], [""], [""]
    analyzer_nouns, analyzer_verbs = analyzers

    for token in sentence:
        if isinstance(token.get('id'), int):
            lemma = token.get("lemma", "").lower()
            form = token.get("form", "").lower()
            upos = token.get("upos", "")
            xpos = token.get("xpos", "")
            pos = '_'.join(filter(None, [upos, xpos]))

            forms.append(token.get("form", ""))
            lemmas.append(token.get("lemma", ""))
            poss.append(pos)

            deprel = token.get("deprel", "")
            deps = [dep.get("form", "").lower() for dep in sentence if dep.get("head") == token.get("id")]
            
            # Check conditions for verbs
            check = "*" if (upos == "VERB" and (deprel == "amod" or any(dep == "det" for dep in deps))) else ""
            checks.append(check)

            exp_nouns.append(analyzer_nouns.extract_exponent(form, lemma, upos) if upos == "NOUN" else "")
            exp_verbs.append(analyzer_verbs.extract_exponent(form, lemma, upos) if (upos in ["VERB", "AUX"] and check == "") else "")

    # Add sentence end markers
    forms.append("[S_END]")
    lemmas.append("")
    poss.append("")
    exp_nouns.append("")
    exp_verbs.append("")
    checks.append("")

    return forms, lemmas, poss, exp_nouns, exp_verbs, checks

def main():
    input_file = sys.argv[1]
    target_dir = Path("target/")
    target_dir.mkdir(parents=True, exist_ok=True)

    analyzer_nouns = MorphologicalAnalyzer("source/dictionaries/en_nouns.json")
    analyzer_verbs = MorphologicalAnalyzer("source/dictionaries/en_verbs.json")

    with open(input_file, "r", encoding="utf-8") as f:
        data = conllu.parse(f.read())

    # Prepare columns
    forms, lemmas, poss, exp_nouns, exp_verbs, checks = [], [], [], [], [], []

    for sentence in data:
        sentence_data = process_sentence(sentence, (analyzer_nouns, analyzer_verbs))
        for col, sentence_col in zip([forms, lemmas, poss, exp_nouns, exp_verbs, checks], sentence_data):
            col.extend(sentence_col)

    # Create DataFrame and save to CSV
    df = pd.DataFrame({
        "form": forms,
        "lemma": lemmas,
        "pos": poss,
        "V_exp": exp_verbs,
        "N_exp": exp_nouns,
        "check": checks
    })
    df.to_csv(target_dir / 'out.csv', index=False)

if __name__ == "__main__":
    main()
