import os
import pandas as pd
from pathlib import Path
from datasets import Dataset
import torch
from io import StringIO
from transformers import (
    LEDForConditionalGeneration,
    LEDTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
import random

CONFIG = {
    "PERCENTAGE_TO_USE": 0.2,
    "paths": {
        "arxiv": r"C:\Users\nithi\PycharmProjects\infosys_project_trial_2\data_set\arxiv-metadata-oai-snapshot.json",
        "bbc": r"C:\Users\nithi\Documents\college\sem 5\infosys internship\summarization and insight\1\archive\BBC News Summary",
        "cnn_dailymail": r"C:\Users\nithi\Documents\college\sem 5\infosys internship\summarization and insight\2\archive\cnn_dailymail",
        "samsum": r"C:\Users\nithi\Documents\college\sem 5\infosys internship\summarization and insight\3\archive (1)",
        "pubmed": r"C:\Users\nithi\Documents\college\sem 5\infosys internship\summarization and insight\4\archive"
    },
    "features": {
        "arxiv": {"text": "title", "summary": "abstract"},
        "cnn_dailymail": {"text": "article", "summary": "highlights"},
        "samsum": {"text": "dialogue", "summary": "summary"},
        "pubmed": {"text": "article", "summary": "abstract"}
    }
}


def load_arxiv_data(path, features, percentage):
    """Generator for the arXiv dataset."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for line in f)
        sample_size = int(total_lines * percentage)
        print(f"arXiv total lines: {total_lines}, taking {percentage * 100:.0f}%: {sample_size} samples.")
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= sample_size: break
                record = pd.read_json(StringIO(line), typ='series')
                text, summary = record.get(features["text"], ""), record.get(features["summary"], "")
                if text and summary: yield {"text": text.strip(), "summary": summary.strip()}
    except FileNotFoundError:
        print(f"Warning: arXiv file not found at {path}. Skipping.")


def load_bbc_data(path, percentage):
    """Generator for the BBC News dataset."""
    all_files = []
    try:
        articles_path, summaries_path = Path(path) / "News Articles", Path(path) / "Summaries"
        if not all([articles_path.exists(), summaries_path.exists()]):
            print(f"Warning: BBC folders not found in {path}. Skipping.");
            return
        for category in articles_path.iterdir():
            if category.is_dir():
                article_files = sorted(list((articles_path / category.name).glob("*.txt")))
                summary_files = sorted(list((summaries_path / category.name).glob("*.txt")))
                all_files.extend(zip(article_files, summary_files))
        random.seed(42);
        random.shuffle(all_files)
        sample_size = int(len(all_files) * percentage)
        print(f"BBC total files: {len(all_files)}, taking {percentage * 100:.0f}%: {sample_size} samples.")
        for article_file, summary_file in all_files[:sample_size]:
            try:
                with open(article_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                with open(summary_file, 'r', encoding='utf-8', errors='ignore') as f:
                    summary = f.read()
                if text and summary: yield {"text": text.strip(), "summary": summary.strip()}
            except Exception as e:
                print(f"Skipping a BBC file due to error: {e}")
    except Exception as e:
        print(f"Error loading BBC data: {e}")


def load_csv_data(path, features, dataset_name, percentage):
    """CORRECTED: Generator for CSV-based datasets that ONLY samples from the train split."""
    data_loaded = False
    split_to_load = "train"
    file_path = Path(path) / f"{split_to_load}.csv"
    if not file_path.exists(): file_path = Path(path) / f"samsum-{split_to_load}.csv"
    if file_path.exists():
        data_loaded = True
        df = pd.read_csv(file_path)
        df_sample = df.sample(frac=percentage, random_state=42).copy()
        print(
            f"{dataset_name} ({split_to_load}) total rows: {len(df)}, taking {percentage * 100:.0f}%: {len(df_sample)} samples.")
        df_sample.dropna(subset=[features["text"], features["summary"]], inplace=True)
        for _, row in df_sample.iterrows():
            yield {"text": str(row[features["text"]]).strip(), "summary": str(row[features["summary"]]).strip()}
    if not data_loaded: print(
        f"Warning: No 'train.csv' or 'samsum-train.csv' found for {dataset_name} at {path}. Skipping.")


def stream_all_datasets():
    percentage = CONFIG["PERCENTAGE_TO_USE"]
    print("Streaming arXiv data...");
    yield from load_arxiv_data(CONFIG["paths"]["arxiv"], CONFIG["features"]["arxiv"], percentage)
    print("\nStreaming BBC News data...");
    yield from load_bbc_data(CONFIG["paths"]["bbc"], percentage)
    print("\nStreaming CNN/DailyMail data...");
    yield from load_csv_data(CONFIG["paths"]["cnn_dailymail"], CONFIG["features"]["cnn_dailymail"], "CNN/DailyMail",
                             percentage)
    print("\nStreaming Samsum data...");
    yield from load_csv_data(CONFIG["paths"]["samsum"], CONFIG["features"]["samsum"], "Samsum", percentage)
    print("\nStreaming PubMed data...");
    yield from load_csv_data(CONFIG["paths"]["pubmed"], CONFIG["features"]["pubmed"], "PubMed", percentage)


def main():
    full_dataset = Dataset.from_generator(stream_all_datasets)
    print(f"\nTotal combined samples for this run: {len(full_dataset)}")
    dataset_dict = full_dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset, test_dataset = dataset_dict["train"], dataset_dict["test"]
    print(f"Train samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")

    model_name = "allenai/led-base-16384"

    tokenizer = LEDTokenizer.from_pretrained(model_name)
    model = LEDForConditionalGeneration.from_pretrained(model_name)

    def preprocess_function(examples):
        inputs = examples["text"]

        model_inputs = tokenizer(inputs, max_length=1024, truncation=True)

        labels = tokenizer(text_target=examples["summary"], max_length=512, truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    print("\nTokenizing the combined dataset for LED... This may take some time.")
    tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True,
                                                remove_columns=train_dataset.column_names)
    tokenized_test_dataset = test_dataset.map(preprocess_function, batched=True,
                                              remove_columns=test_dataset.column_names)

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir="./led_base_universal_summarizer_results",
        do_eval=True,
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=16,
        weight_decay=0.01,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=3,
        num_train_epochs=1,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        logging_steps=100,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_test_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    print("\nStarting the fine-tuning process for the LED model...")
    trainer.train(resume_from_checkpoint=True)

    final_model_path = "./led_base_universal_summarizer"
    trainer.save_model(final_model_path)
    print(f"Model fine-tuning complete! Final model saved to {final_model_path}")


if _name_ == "_main_":
    main()
