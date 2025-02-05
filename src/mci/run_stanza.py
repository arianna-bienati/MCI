#!/usr/bin/env python3

import os

import stanza
from stanza.utils.conll import CoNLL
import stanza.resources.common

def run_stanza(text, language):
    """
    Process text using Stanza and return conllu data.

    Args:
        text (str): input text.
        language (str): language of the input texts.

    Returns:
        processed CoNLL-U format as a list of lists.
    """
    # Ensure Stanza resources are downloaded
    stanza_resources_path = os.path.join(stanza.resources.common.DEFAULT_MODEL_DIR, "resources.json")
    if not os.path.isfile(stanza_resources_path):
        stanza.resources.common.download_resources_json(
            stanza.resources.common.DEFAULT_MODEL_DIR,
            stanza.resources.common.DEFAULT_RESOURCES_URL,
            None,
            stanza.resources.common.DEFAULT_RESOURCES_VERSION,
        )
    stanza.download(language)
    nlp = stanza.Pipeline(language, processors="tokenize,mwt,pos,lemma,depparse")
    doc = nlp(text)
    dicts = doc.to_dict()
    return dicts
