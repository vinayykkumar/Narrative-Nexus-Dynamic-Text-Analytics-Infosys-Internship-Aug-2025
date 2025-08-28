import json
import multiprocessing as mp
from nltk.stem import WordNetLemmatizer
import ijson

lemmatizer = WordNetLemmatizer()

def lemmatize_tokens(tokens):
    return [lemmatizer.lemmatize(tok) for tok in tokens]

def process_json_parallel(input_file, output_file, workers=4, chunk_size=1000):
    with open(input_file, "r", encoding="utf-8") as f:
        parser = ijson.items(f, "item")
        buffer = []
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("[\n")
            first = True
            with mp.Pool(processes=workers) as pool:
                for item in parser:
                    buffer.append(item)
                    if len(buffer) >= chunk_size:
                        results = pool.map(lemmatize_tokens, buffer)
                        for r in results:
                            if not first:
                                out.write(",\n")
                            json.dump(r, out, ensure_ascii=False)
                            first = False
                        buffer = []

                # leftover
                if buffer:
                    results = pool.map(lemmatize_tokens, buffer)
                    for r in results:
                        if not first:
                            out.write(",\n")
                        json.dump(r, out, ensure_ascii=False)
                        first = False

            out.write("\n]")

if __name__ == "__main__":
    input_file = "tokenized.json"
    output_file = "lemmatized.json"
    process_json_parallel(input_file, output_file, workers=4, chunk_size=1000)
