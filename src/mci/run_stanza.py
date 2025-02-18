#!/usr/bin/env python3

import os

import stanza
import stanza.resources.common

def init_stanza(language):
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
    return nlp

def run_stanza(text, language):
    nlp = init_stanza(language)
    doc = nlp(text)
    dicts = doc.to_dict()
    return dicts
