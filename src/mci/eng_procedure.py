import json
import re

class MorphologicalAnalyzer:
    def __init__(self, json_file_path):
        # Load rules from the JSON file
        with open(json_file_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

    def extract_irregular_exponent(self, form, lemma, pos):
        """
        Tries to extract the morphological exponent using irregular rules.
        """
        # Sort rules by priority
        sorted_rules = sorted(
            [rule for rule in self.rules if rule["enabled"]],
            key=lambda rule: rule["priority"]
        )

        for rule in sorted_rules:
            # Check conditions: wordForm, lemma, and posTag
            conditions = rule["conditions"]
            word_form_match = re.match(
                conditions["wordForm"]["pattern"],
                form,
                flags=re.IGNORECASE if "i" in conditions["wordForm"]["flags"] else 0
            )
            lemma_match = re.match(
                conditions["lemma"]["pattern"],
                lemma,
                flags=re.IGNORECASE if "i" in conditions["lemma"]["flags"] else 0
            )
            pos_match = pos in conditions["posTag"]

            if word_form_match and lemma_match and pos_match:
                return rule["morphological_exponent"]["template"]

        # If no irregular rule matches, return None
        return None

    @staticmethod
    def extract_regular_exponent(form, lemma):
        """
        Extracts the morphological exponent using the regular procedure.
        """
        if form == lemma:
            return "Ø"
        elif form.startswith(lemma):
            return form[len(lemma):] or "Ø"
        else:
            return form.replace(lemma, "", 1) or "Ø"

    def extract_exponent(self, form, lemma, pos):
        """
        Extracts the morphological exponent, prioritizing irregular rules.
        """
        # Try irregular rules first
        irregular_exponent = self.extract_irregular_exponent(form, lemma, pos)
        if irregular_exponent:
            return irregular_exponent

        # Fall back to the standard procedure
        return self.extract_regular_exponent(form, lemma)
