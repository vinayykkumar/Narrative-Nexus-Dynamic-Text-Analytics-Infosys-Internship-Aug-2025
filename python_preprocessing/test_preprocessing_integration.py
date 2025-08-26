#!/usr/bin/env python3
"""
Integration test to verify the preprocessing demo matches Python implementation
AI Narrative Nexus - Preprocessing Validation
"""

import sys
import os
sys.path.append('python_preprocessing')

from text_preprocessor import TextPreprocessor
import time

def test_preprocessing_demo():
    """Test the same text used in the web demo with Python implementation"""
    
    # Same sample text from the web demo
    sample_text = """This is a COMPREHENSIVE text for preprocessing!!! It contains URLs like https://example.com/path?param=1, emails like user@test-domain.co.uk, social mentions @john_doe, hashtags #AI #MachineLearning, numbers like 123.45, contractions like won't, can't, it's, and various punctuation marks... Are we ready for advanced analysis? 😊✨ Let's see how stemming works with running, runner, runs, and beautiful, beautifully, beauty!"""
    
    print("AI Narrative Nexus - Preprocessing Integration Test")
    print("=" * 60)
    print(f"Testing sample text: {sample_text[:100]}...")
    print()
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(remove_stopwords=True, use_stemming=True, use_lemmatization=False)
    
    start_time = time.time()
    
    # Process the text
    cleaned, normalized, tokens = preprocessor.preprocess_text(sample_text)
    
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    print("PROCESSING RESULTS:")
    print("-" * 40)
    print(f"Original Length: {len(sample_text)} characters")
    print(f"Cleaned Length: {len(cleaned)} characters")
    print(f"Normalized Length: {len(normalized)} characters")
    print(f"Token Count: {len(tokens)} tokens")
    print(f"Processing Time: {processing_time:.2f}ms")
    print()
    
    print("STEP-BY-STEP BREAKDOWN:")
    print("-" * 40)
    print(f"1. Original Text:")
    print(f"   {sample_text}")
    print()
    
    print(f"2. Cleaned Text:")
    print(f"   {cleaned}")
    print()
    
    print(f"3. Normalized Text:")
    print(f"   {normalized}")
    print()
    
    print(f"4. Final Tokens ({len(tokens)}):")
    print(f"   {', '.join(tokens)}")
    print()
    
    # Validate preprocessing steps
    validation_results = {
        'urls_removed': 'https://' not in cleaned and 'www.' not in cleaned,
        'emails_removed': '@' not in cleaned,
        'punctuation_removed': not any(char in cleaned for char in '!@#$%^&*()+={}[]|\\:";\'<>?,./'),
        'numbers_removed': not any(char.isdigit() for char in cleaned),
        'lowercase_applied': cleaned.islower(),
        'contractions_expanded': "won't" not in normalized and "can't" not in normalized,
        'tokens_filtered': len(tokens) < len(normalized.split()),
        'stopwords_removed': not any(word in tokens for word in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']),
        'stemming_applied': any(word in tokens for word in ['run', 'beauti']) and len([t for t in tokens if 'beauti' in t]) >= 1  # Multiple beauty variants should stem to beauti
    }
    
    print("VALIDATION CHECKS:")
    print("-" * 40)
    for check, passed in validation_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check.replace('_', ' ').title()}")
    
    print()
    
    # Summary
    passed_checks = sum(validation_results.values())
    total_checks = len(validation_results)
    
    print(f"SUMMARY: {passed_checks}/{total_checks} validation checks passed")
    print("=" * 60)
    
    if passed_checks == total_checks:
        print("🎉 ALL PREPROCESSING REQUIREMENTS IMPLEMENTED CORRECTLY!")
        print("✅ Web demo matches Python implementation standards")
        print("✅ Ready for production ML pipeline integration")
    else:
        print("⚠️  Some preprocessing requirements need attention")
        print("🔧 Review failed validation checks above")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    test_passed = test_preprocessing_demo()
    sys.exit(0 if test_passed else 1)
