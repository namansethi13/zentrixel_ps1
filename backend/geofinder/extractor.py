import spacy

nlp = spacy.load("en_core_web_sm")

def extract_locations(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")]