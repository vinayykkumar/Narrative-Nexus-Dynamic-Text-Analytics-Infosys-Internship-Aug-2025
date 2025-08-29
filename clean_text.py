import json
import re
import os

input_file = r"C:\Users\Chethan\PycharmProjects\infosys_project_trial_2\data_set\arxiv.json"
output_file = r"C:\Users\Chethan\PycharmProjects\infosys_project_trial_2\processed_datasets\clean_text.json"

os.makedirs(os.path.dirname(output_file), exist_ok=True)

cleaned = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        text = record.get("abstract", "") + " " + record.get("title", "")
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        record["clean_text"] = text
        cleaned.append(record)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)
