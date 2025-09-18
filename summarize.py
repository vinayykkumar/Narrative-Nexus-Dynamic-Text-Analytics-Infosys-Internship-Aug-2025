import spacy
import pytextrank

# ==============================================================================
# == TEXT SUMMARIZATION MODULE (using spaCy and pytextrank) ==
# ==============================================================================

# --- 1. SETUP THE SPAcY MODEL WITH PYTEXTRANK ---
try:
    # Load the small English model for spaCy
    nlp = spacy.load('en_core_web_sm')
    # Add the TextRank component to the spaCy pipeline
    nlp.add_pipe("textrank")
    print("✅ spaCy model with pytextrank loaded successfully.")
except OSError:
    print("❌ Error: spaCy English model not found.")
    print("Please run 'python -m spacy download en_core_web_sm' in your terminal.")
    exit()


def summarize_text(original_text, sentence_count=3):
    """
    Generates an extractive summary of the given text using pytextrank.

    Args:
        original_text (str): The long text to be summarized.
        sentence_count (int): The desired number of sentences in the summary.

    Returns:
        str: The generated summary.
    """
    if not isinstance(original_text, str) or len(original_text.strip()) == 0:
        return "The original text is empty or invalid."

    # Process the text through the spaCy pipeline
    doc = nlp(original_text)
    
    # Check if any sentences were found
    if not doc._.textrank.summary:
        return "The original text is too short to generate a meaningful summary."

    # Extract the top-ranked sentences for the summary
    summary_sentences = [
        sentence.text.strip() for sentence in doc._.textrank.summary(limit_phrases=15, limit_sentences=sentence_count)
    ]
    return " ".join(summary_sentences)


# ==============================================================================
# == EXAMPLE USAGE ==
# ==============================================================================

if __name__ == '__main__':
    sample_article_text = """
    Artificial intelligence (AI) is rapidly transforming the technology landscape, with advancements in machine learning
    and deep learning driving innovation across various sectors. Companies are leveraging AI to automate processes, gain
    insights from large datasets, and create more personalized customer experiences. For instance, in the healthcare
    industry, AI algorithms are being used to diagnose diseases with greater accuracy, while in the financial sector,
    they help in fraud detection and algorithmic trading. The development of large language models (LLMs) has further
    accelerated this trend, enabling more natural and sophisticated interactions between humans and computers.
    However, the rapid adoption of AI also raises ethical concerns, including issues of bias in algorithms, job displacement,
    and the need for regulatory oversight. Ensuring that AI is developed and deployed responsibly is a critical challenge
    that researchers, policymakers, and industry leaders are actively working to address. The future of AI will depend on
    balancing its immense potential with a strong commitment to ethical principles and human-centric design.
    """

    print("--- ORIGINAL TEXT ---")
    print(sample_article_text.strip())
    print("\n" + "="*50 + "\n")

    # Generate a summary with a limit of 3 sentences
    generated_summary = summarize_text(sample_article_text, sentence_count=3)

    print(f"--- GENERATED SUMMARY ({3} Sentences) ---")
    print(generated_summary)