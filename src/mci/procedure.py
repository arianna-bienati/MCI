import json
import re

class LemmaNormalizer:
    def __init__(self, json_file_path):
        with open(json_file_path, 'r', encoding="utf-8") as f:
            self.normalization_rules = json.load(f)
    
    def normalize_lemma(self, lemma, language):
        """
        Normalize the lemma based on language-specific rules.
        """
        if language not in self.normalization_rules:
            return lemma  # No normalization rules for this language

        for rule in self.normalization_rules[language]:
            pattern = rule["pattern"]
            replacement = rule["replacement"]
            # Replace {1} with \1 for capturing groups
            replacement = replacement.replace("{1}", r"\1")
            lemma = re.sub(pattern, replacement, lemma)

        return lemma

class MorphologicalAnalyzer:
    def __init__(self, json_file_path):
        # Load rules from the JSON file
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.rules = data["rules"]
        if "placeholder" in json_file_path:
            print(f"Warning: Using placeholder file {json_file_path}. Data may be incomplete.")
        
        self.sorted_rules = sorted(
            [rule for rule in self.rules if rule["enabled"]],
            key=lambda rule: rule["priority"]
        )

    def parse_feats(self, feats):
        """
        Parses the 'feats' string from CoNLL-U format into a dictionary.
        Example: "Case=Nom|Number=Sing" -> {"Case": "Nom", "Number": "Sing"}
        """
        if not feats or feats == "_":
            return {}
        return dict(item.split("=") for item in feats.split("|"))
    
    def extract_irregular_exponent(self, form, lemma, pos, feats=None):
        """
        Tries to extract the morphological exponent using irregular rules.
        """
        feats_dict = self.parse_feats(feats) if feats else {}

        for rule in self.sorted_rules:
            # Check conditions: wordForm, lemma, and posTag
            conditions = rule["conditions"]

            # Match word form
            word_form_match = re.match(
                conditions["wordForm"]["pattern"],
                form,
                flags=re.IGNORECASE if "i" in conditions["wordForm"]["flags"] else 0
            )
            
            # Match lemma
            lemma_match = re.match(
                conditions["lemma"]["pattern"],
                lemma,
                flags=re.IGNORECASE if "i" in conditions["lemma"]["flags"] else 0
            )
            
            # Match pos
            pos_match = pos in conditions["posTag"]

            # Match feats if provided in rule
            feats_match = True
            if "feats" in conditions:
                rule_feats = conditions["feats"]
                for feat, value in rule_feats.items():
                    if feat not in feats_dict or feats_dict[feat] != value:
                        feats_match = False
                        break

            if word_form_match and lemma_match and pos_match and feats_match:
                template = rule["morphological_exponent"]["template"]
                template = re.sub(r"\{(\d+)\}", r"\\\1", template)
                result = word_form_match.expand(template)
                
                return result

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

    def extract_exponent(self, form, lemma, pos, feats):
        """
        Extracts the morphological exponent, prioritizing irregular rules.
        """
        # Try irregular rules first
        irregular_exponent = self.extract_irregular_exponent(form, lemma, pos, feats)
        if irregular_exponent:
            return irregular_exponent

        # Fall back to the standard procedure
        return self.extract_regular_exponent(form, lemma)
