import json
import os
import re
import spacy
import logging
import nltk
from nltk.corpus import stopwords
from concurrent.futures import ProcessPoolExecutor, as_completed


def process_chunk(lines_chunk):
    """Processes a list of JSON strings: loads, cleans, and lemmatizes each."""
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    stop_words = set(stopwords.words("english"))

    processed_records = []
    for line in lines_chunk:
        record = json.loads(line)

        text = record.get("abstract", "") + " " + record.get("title", "")
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        record["clean_text"] = text

        doc = nlp(text)
        lemmas = [
            token.lemma_.lower() for token in doc
            if token.is_alpha and token.lemma_.lower() not in stop_words
        ]
        record["lemmas"] = lemmas
        processed_records.append(record)

    return processed_records


def process_and_lemmatize_data_parallel(input_path, output_path, chunk_size=1000, workers=None):
    """
    Reads a JSONL file and processes it in parallel using a pool of workers.
    """
    logging.info("Setting up NLP resources...")
    try:
        nltk.data.find('corpora/stopwords')
    except nltk.downloader.DownloadError:
        nltk.download('stopwords', quiet=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logging.info(f"Starting parallel data processing for: {input_path}")
    logging.info(f"Using chunk size: {chunk_size} and workers: {workers or os.cpu_count()}")

    try:
        with open(input_path, "r", encoding="utf-8") as f_in, \
                open(output_path, "w", encoding="utf-8") as f_out, \
                ProcessPoolExecutor(max_workers=workers) as executor:

            lines_buffer = []
            futures = []
            record_count = 0

            for line in f_in:
                lines_buffer.append(line)
                if len(lines_buffer) >= chunk_size:
                    future = executor.submit(process_chunk, lines_buffer)
                    futures.append(future)
                    lines_buffer = []

            if lines_buffer:
                future = executor.submit(process_chunk, lines_buffer)
                futures.append(future)

            logging.info(f"Submitted {len(futures)} chunks to the processing pool. Awaiting results...")
            for future in as_completed(futures):
                try:
                    processed_chunk = future.result()
                    for record in processed_chunk:
                        f_out.write(json.dumps(record) + '\n')
                        record_count += 1

                    print(f"  ... Wrote chunk. Total records processed: {record_count:,} ...", end='\r', flush=True)

                except Exception as e:
                    logging.error(f"A chunk failed to process: {e}")

        print()
        logging.info("=" * 60)
        logging.info("Data processing complete!")
        logging.info(f"   - Total records processed: {record_count:,}")
        logging.info(f"   - Output saved to: {output_path}")
        logging.info("=" * 60)

    except FileNotFoundError:
        logging.error(f"Input file not found at: {input_path}")
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main process: {e}", exc_info=True)


if _name_ == "_main_":
    input_file = r"..\data_set\arxiv-metadata-oai-snapshot.json"
    output_file = r"..\processed_datasets\lemmatized_parallel.jsnol"

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    logging.info("--- Unified Data Preprocessing Script (Parallel Version) ---")
    process_and_lemmatize_data_parallel(input_file, output_file, chunk_size=2000)
    logging.info("Script finished.")
