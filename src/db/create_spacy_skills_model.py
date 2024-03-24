
import json
import spacy

tech_list = ['C++', 'C', 'Javascript', 'Java', 'SQL', 'R', 'Python']

patterns = []
for x in tech_list:
    patterns.append({"label": "PROG_LANG", "pattern": x, "id": "SKILLS"})

nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns(patterns)
ruler.to_disk("tech_lang_patterns.jsonl")