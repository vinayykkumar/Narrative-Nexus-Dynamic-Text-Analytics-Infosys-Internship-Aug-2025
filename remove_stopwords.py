import json
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

input_file = r"C:\Users\Chethan\PycharmProjects\infosys_project_trial_2\processed_datasets\clean_text.json"
output_file = input_file.replace("clean_text.json", "remove_stopwords.json")

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

processed = []
for item in data:
    text = item.get("clean_text", "")
    filtered = " ".join([w for w in text.split() if w.lower() not in stop_words])
    item["clean_text"] = filtered
    processed.append(item)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)
