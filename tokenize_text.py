import spacy
import json

def tokenize_json(input_file, output_file, batch_size=500):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    
    with open(input_file, "r", encoding="utf-8") as f_in:
        data = json.load(f_in)
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("[\n")
        first = True
        
        for item in data:
            text = item.get("clean_text", "")
            doc = nlp(text)
            tokens = [tok.text for tok in doc if tok.is_alpha]
            item["tokens"] = tokens
            
            if not first:
                f_out.write(",\n")
            json.dump(item, f_out, ensure_ascii=False, indent=2)
            first = False
        
        f_out.write("\n]")

if __name__ == "__main__":
    input_file = r"D:\Infosys_SpringBoard\JSON\clean_text.json"
    output_file = r"D:\Infosys_SpringBoard\JSON\tokenized.json"
    tokenize_json(input_file, output_file, batch_size=500)
