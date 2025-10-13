#src/cleaners.py
"""
Simple, robust text cleaner for PDFs and CSVs.
No complex heuristics - just remove obvious noise.
"""
import re
import unicodedata
from typing import List, Dict, Optional


def normalize_text(text: str) -> str:
    """Normalize unicode and common PDF artifacts."""
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    
    # Fix ligatures
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = text.replace("\u00A0", " ")  # non-breaking space
    
    # Fix hyphenated line breaks: "prob-\nlem" → "problem"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    
    # Collapse multiple spaces/newlines
    text = re.sub(r"\s*\n+\s*", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    
    return text.strip()


def remove_boilerplate(text: str) -> str:
    """Remove common academic/web boilerplate."""
    
    section_headers = [
        "KEYWORDS?", "INTRODUCTION", "ABSTRACT", "METHODS?", 
        "RESULTS?", "DISCUSSION", "CONCLUSIONS?",
    ]
    
    for header in section_headers:
        text = re.sub(fr"\b({header})(?=[A-Z][a-z])", r"\1 ", text, flags=re.I)
    
    # Remove IJRTI codes (but keep surrounding text)
    text = re.sub(r'\bIJRTI\d{5,}\b', '', text)
    
    # Remove KEYWORDS sections entirely
    text = re.sub(r"(?im)^.*\bKEYWORDS?\b.*$", "", text)
    
    # Remove INTRODUCTION headers (keep the body text after)
    text = re.sub(r"(?i)^\s*INTRODUCTION\s*[:.]?\s*", " ", text, flags=re.M)
    # === END NEW SECTION ===
    
    # Remove copyright, ISSN, DOI
    text = re.sub(r"©\s*\d{4}[^\n.]{0,100}", " ", text, flags=re.I)
    text = re.sub(r"\bISSN[:\s]*\d[\dxX\-]+", " ", text, flags=re.I)
    text = re.sub(r"\bDOI[:\s]*10\.\d{4,9}/\S+", " ", text, flags=re.I)
    
    # Remove copyright, ISSN, DOI
    text = re.sub(r"©\s*\d{4}[^\n.]{0,100}", " ", text, flags=re.I)
    text = re.sub(r"\bISSN[:\s]*\d[\dxX\-]+", " ", text, flags=re.I)
    text = re.sub(r"\bDOI[:\s]*10\.\d{4,9}/\S+", " ", text, flags=re.I)
    
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text, flags=re.I)
    
    # Remove journal headers (common in PDFs)
    text = re.sub(r"(?i)International Journal[^\n]{0,150}", " ", text)
    text = re.sub(r"(?i)Volume\s+\d+[,\s]+Issue\s+\d+", " ", text)
    
    # Remove page numbers
    text = re.sub(r"(?m)^\s*page\s*\d+\s*$", " ", text, flags=re.I)
    text = re.sub(r"(?m)^\s*\d+\s*$", " ", text)
    
    # Remove navigation (common in web scrapes)
    text = re.sub(r"(?i)\b(click here|read more|back to|sign in)\b[^\n]{0,50}", " ", text)
    
    return re.sub(r"\s{2,}", " ", text).strip()


def remove_sections(text: str, remove_after: str = "REFERENCES") -> str:
    """Cut text after a section header (e.g., References, Acknowledgments)."""
    
    # Define multiple cut points (earliest wins)
    cut_patterns = [
        fr"(?i)\b{remove_after}\s*\n",
        fr"(?i)\b{remove_after}\s*$",
        # === ADD THESE SPECIFIC PATTERNS FOR YOUR PDF ===
        r"(?i)\bNetApp and artificial intelligence\b",  # Exact header from your PDF
        r"(?i)\bConclusion\b.*?(?=\bNetApp\b)",         # Cut after Conclusion if NetApp follows
    ]
    
    earliest_pos = len(text)
    
    for pattern in cut_patterns:
        match = re.search(pattern, text)
        if match:
            earliest_pos = min(earliest_pos, match.start())
    
    if earliest_pos < len(text):
        return text[:earliest_pos].strip()
    
    return text


def detect_repeating_headers_footers(pages: List[str], threshold: float = 0.5) -> tuple[set, set]:
    """
    Find lines that repeat across pages (headers/footers).
    Returns: (header_lines, footer_lines)
    """
    if not pages or len(pages) < 2:
        return set(), set()
    
    def normalize_line(line: str) -> str:
        """Normalize for comparison."""
        line = line.lower().strip()
        line = re.sub(r"\d+", "", line)  # remove page numbers
        line = re.sub(r"\s+", " ", line)
        return line
    
    # Count occurrences of first/last lines
    first_lines = {}
    last_lines = {}
    
    for page in pages:
        lines = [l for l in page.split("\n") if l.strip()]
        if not lines:
            continue
        
        # Check first 2 lines
        for line in lines[:2]:
            key = normalize_line(line)
            if key and len(key) > 10:
                first_lines[key] = first_lines.get(key, 0) + 1
        
        # Check last 2 lines
        for line in lines[-2:]:
            key = normalize_line(line)
            if key and len(key) > 10:
                last_lines[key] = last_lines.get(key, 0) + 1
    
    total_pages = len(pages)
    headers = {k for k, v in first_lines.items() if v / total_pages >= threshold}
    footers = {k for k, v in last_lines.items() if v / total_pages >= threshold}
    
    return headers, footers


def clean_text(
    text: str,
    *,
    pages: Optional[List[str]] = None,
    remove_after: str = "REFERENCES",
    aggressive: bool = False
) -> Dict[str, any]:
    """
    Main cleaning function.
    
    Args:
        text: Raw text to clean
        pages: List of per-page text (for header/footer detection)
        remove_after: Section name to cut after (default: REFERENCES)
        aggressive: If True, remove more aggressively (for summarization)
    
    Returns:
        {
            "text": cleaned text,
            "original_length": original char count,
            "cleaned_length": cleaned char count,
            "removed_headers": list of detected headers,
            "removed_footers": list of detected footers,
        }
    """
    original_length = len(text)
    
    # Step 1: Normalize
    text = normalize_text(text)
    
    # Step 2: Remove headers/footers (if pages provided)
    removed_headers, removed_footers = [], []
    if pages and len(pages) >= 2:
        headers, footers = detect_repeating_headers_footers(pages)
        removed_headers = list(headers)
        removed_footers = list(footers)
        
        # Remove them from text
        for pattern in headers | footers:
            text = re.sub(re.escape(pattern), " ", text, flags=re.I)
    
    # Step 3: Remove boilerplate
    text = remove_boilerplate(text)
    
    # Step 4: Cut after references/conclusion
    text = remove_sections(text, remove_after=remove_after)
    
    # Step 4.5: Remove promotional content (always, not just in aggressive mode)
    text_before_promo = text
    text = remove_promotional_content(text)
    
    # === ADD DEBUG ===
    if len(text) < len(text_before_promo) * 0.3:  # If we removed >70% of content
        # Promotional filter was too aggressive, revert
        text = text_before_promo
    # === END DEBUG ===

    
    # Step 5: Aggressive cleaning (for summarization)
    if aggressive:
        # Remove keywords sections
        text = re.sub(r"(?i)\bkeywords?\b[:\-\s][^\n.]{0,200}", " ", text)

        # Remove "in this paper" phrases
        text = re.sub(r"(?i)\bin this paper[^.]{0,100}\.", " ", text)

        # Remove figure/table references
        text = re.sub(r"(?i)\b(figure|fig\.|table)\s*\d+", " ", text)

        

    # Final cleanup
    text = re.sub(r"\s{2,}", " ", text).strip()
    
    return {
        "text": text,
        "original_length": original_length,
        "cleaned_length": len(text),
        "removed_headers": removed_headers,
        "removed_footers": removed_footers,
    }


def split_sentences(text: str) -> List[str]:
    """Simple sentence splitter."""
    if not text:
        return []
    
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Filter short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Remove duplicates (keep order)
    seen = set()
    unique = []
    for s in sentences:
        key = re.sub(r'\W+', '', s.lower())[:100]
        if key not in seen:
            seen.add(key)
            unique.append(s)
    
    return unique


def remove_promotional_content(text: str) -> str:
    """
    Remove promotional/advertisement sections.
    Stricter version that catches vendor-specific content.
    """
    import re
    
    vendor_headers = [
        r"(?i)\bNetApp and artificial intelligence\b",
        r"(?i)\bMicrosoft (Azure|AI)\b.*\b(solutions?|platform)",
        r"(?i)\bAmazon Web Services\b.*\bAI\b",
    ]
    
    for pattern in vendor_headers:
        parts = re.split(pattern, text, maxsplit=1)
        if len(parts) > 1:
            text = parts[0]  # Keep only text before vendor section
    
    # Now split remaining text into blocks
    blocks = re.split(r'\n\s*\n', text)
    
    # Stricter promotional indicators
    promo_keywords = [
        "NetApp", "ONTAP", "AFF", "Cloud Volumes",
        "building blocks", "all-flash", "hybrid cloud",
        "data fabric", "IoT devices", "aggregation points"
    ]
    
    clean_blocks = []
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 20:
            continue
        
        # Count promotional keywords in this block
        promo_count = sum(1 for kw in promo_keywords if kw in block)
        
        # Skip if block has ANY promotional keyword (strict)
        if promo_count > 0:
            continue
        
        # Also skip bullet lists about products/features
        if re.search(r'[•\-]\s+[A-Z].*(?:enables?|accelerate|provide)', block, re.I):
            continue
        
        clean_blocks.append(block)
    
    return '\n\n'.join(clean_blocks)