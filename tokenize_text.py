import spacy
import ijson
import json

def lemmatize_json(input_file, output_file, batch_size=500):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("[\n")
        objects = ijson.items(f_in, "item")
        texts = (" ".join(obj["tokens"]) for obj in objects)
        for i, (doc, obj) in enumerate(zip(
            nlp.pipe(texts, n_process=-1, batch_size=batch_size),
            ijson.items(open(input_file, "r", encoding="utf-8"), "item")
        )):
            obj["lemmas"] = [tok.lemma_ for tok in doc if tok.is_alpha]
            json.dump(obj, f_out, ensure_ascii=False)
            f_out.write(",\n")
        f_out.write("\n]")

if __name__ == "__main__":
    input_file = r"C:\Users\Chethan\PycharmProjects\infosys_project_trial_2\processed_datasets\tokenized.json"
    output_file = r"C:\Users\Chethan\PycharmProjects\infosys_project_trial_2\processed_datasets\lemmatized.json"
    lemmatize_json(input_file, output_file, batch_size=500)
