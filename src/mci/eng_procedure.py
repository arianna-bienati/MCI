from typing import Dict, Tuple, Optional
import re

class EnglishMorphExtractor:
    def __init__(self):
        # Suffix patterns
        self.suffix_patterns = {
            # Verbs
            ('ed', 'e', 'V'): 'ed',    # moved -> move
            ('ied', 'y', 'V'): 'ed',   # tried -> try
            ('ing', 'e', 'V'): 'ing',  # moving -> move
            ('ies', 'y', 'V'): 's',    # flies -> fly
        }
        
        # Double letter patterns
        self.regex_patterns = {
            (r'([a-z])\1ed$', 'V'): 'ed',    # stopped -> stop
            (r'([a-z])\1ing$', 'V'): 'ing',  # stopping -> stop
            (r'[a-z]+ies', 'N'): 's',
            (r'said', 'V'): '_y/id',     # say -> said
            (r'left', 'V'): '_eave/eft'  # leave -> left
        }
    
    def _check_irregular_pattern(self, form: str, lemma: str, pos: str) -> Optional[str]:
        """Check if the form-lemma pair matches any irregular pattern."""
        for pattern, required_pos, exponent in self.regex_patterns:
            if pos.startswith(required_pos) and re.search(pattern, form):
                return exponent
        
        # Finally check basic patterns
        for (suffix, lemma_end, required_pos), exponent in self.irregular_patterns.items():
            if (form.endswith(suffix) and 
                lemma.endswith(lemma_end) and 
                pos.startswith(required_pos)):
                return exponent
        return None
    
    def _extract_regular_exponent(self, form: str, lemma: str) -> str:
        """Extract regular exponent by comparing form and lemma."""
        if form == lemma:
            return 'Ø'
        
        # Find the longest common prefix
        i = 0
        min_len = min(len(form), len(lemma))
        while i < min_len and form[i] == lemma[i]:
            i += 1
        
        if i > 0:
            return form[i:]
        
        return form
    
    def extract_exponent(self, token: dict) -> Tuple[str, str, str, str]:
        """
        Extract morphological exponent from a CoNLL-U token.
        Returns tuple of (form, lemma, pos, exponent)
        """
        form = token.get('form', '').lower()
        lemma = token.get('lemma', '').lower()
        pos = token.get('upos', '')
        
        irregular_exponent = self._check_patterns(form, lemma, pos)
        if irregular_exponent is not None:
            return form, lemma, pos, irregular_exponent
        
        regular_exponent = self._extract_regular_exponent(form, lemma)
        return form, lemma, pos, regular_exponent