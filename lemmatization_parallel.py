import json
import multiprocessing as mp
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def lemmatize_tokens(tokens):
    return [lemmatizer.lemmatize(tok) for tok in tokens]

def process_json_parallel(input_file, output_file, workers=4, chunk_size=1000):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract tokens from all items
    all_tokens = [item.get("tokens", []) for item in data]
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("[\n")
        first = True
        
        with mp.Pool(processes=workers) as pool:
            # Process tokens in chunks
            for i in range(0, len(all_tokens), chunk_size):
                chunk = all_tokens[i:i + chunk_size]
                results = pool.map(lemmatize_tokens, chunk)
                
                for j, result in enumerate(results):
                    item_index = i + j
                    if item_index < len(data):
                        item = data[item_index].copy()
                        item["lemmas"] = result
                        
                        if not first:
                            out.write(",\n")
                        json.dump(item, out, ensure_ascii=False, indent=2)
                        first = False
        
        out.write("\n]")

if __name__ == "__main__":
    input_file = r"D:\Infosys_SpringBoard\JSON\tokenized.json"
    output_file = r"D:\Infosys_SpringBoard\JSON\lemmatized.json"
    process_json_parallel(input_file, output_file, workers=4, chunk_size=1000)
