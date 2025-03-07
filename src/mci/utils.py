import json
import csv
import sys

def tsv_to_json(tsv_file, json_file):
    rules = []
    
    with open(tsv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        
        for row in reader:
            rule = {
                "name": "",
                "type": "",
                "conditions": {
                    "wordForm": {
                        "pattern": f"^{row['form']}$",
                        "flags": "i"
                    },
                    "lemma": {
                        "pattern": f"^{row['lemma']}$",
                        "flags": "i"
                    },
                    "posTag": row['pos'].split(',')
                },
                "morphological_exponent": {
                    "template": row['exponent']
                },
                "priority": row['step'],
                "enabled": True
            }
            rules.append(rule)
    
    output = {"rules": rules}
    
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

def json_to_tsv(json_file, tsv_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    fieldnames = ["step", "form", "lemma", "pos", "exponent"]
    
    with open(tsv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        
        for rule in data.get("rules", []):
            writer.writerow({
                "step": rule.get("priority", ""),
                "form": rule["conditions"]["wordForm"]["pattern"].strip('^$'),
                "lemma": rule["conditions"]["lemma"]["pattern"].strip('^$'),
                "pos": ','.join(rule["conditions"].get("posTag", [])),
                "exponent": rule["morphological_exponent"].get("template", "")
            })


if __name__ == "__main__":
    if "--tsv_to_json" in sys.argv:
        input_tsv = sys.argv[2]
        output_json = sys.argv[3]
        tsv_to_json(input_tsv, output_json)
    elif "--json_to_tsv" in sys.argv:
        input_json = sys.argv[2]
        output_tsv = sys.argv[3]
        json_to_tsv(input_json, output_tsv)
    else:
        print("Usage: script.py --tsv_to_json input.tsv output.json | --json_to_tsv input.json output.tsv")