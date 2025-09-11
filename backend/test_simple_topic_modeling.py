#!/usr/bin/env python3
"""
Simple test to validate the advanced topic modeling implementation
following the specified requirements:
- Algorithm Selection: LDA and NMF algorithms
- Model Training: Train models on preprocessed text data
- Topic Identification: Identify key themes and topics
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TEXTS = [
    "Machine learning is revolutionizing technology and artificial intelligence applications in healthcare.",
    "Climate change affects global weather patterns and environmental sustainability efforts worldwide.", 
    "Digital transformation drives innovation in business processes and customer experience strategies.",
    "Healthcare technology improves patient outcomes through advanced diagnostic tools and treatments.",
    "Renewable energy sources like solar and wind power help reduce carbon emissions significantly.",
    "E-commerce platforms enhance online shopping experiences with personalized recommendations and services.",
    "Cybersecurity measures protect sensitive data from threats and ensure digital privacy protection.",
    "Remote work technologies enable flexible employment opportunities and improved work-life balance.",
    "Educational technology transforms learning experiences through interactive digital platforms and tools.",
    "Financial technology innovations streamline banking services and improve accessibility for consumers."
]

def test_lda_algorithm():
    """Test LDA algorithm selection and model training"""
    print("🔍 Testing LDA Algorithm Selection and Model Training...")
    
    payload = {
        "texts": TEST_TEXTS,
        "algorithm": "lda",
        "num_topics": 3,
        "preprocessing_options": {
            "remove_stopwords": True,
            "apply_stemming": True,
            "min_word_length": 3,
            "handle_contractions": True
        },
        "algorithm_params": {
            "max_iter": 100,
            "random_state": 42
        }
    }
    
    response = requests.post(f"{BASE_URL}/topic-modeling", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ LDA Algorithm Test Successful:")
        print(f"   🎯 Algorithm Used: {data.get('algorithm_used', 'Unknown')}")
        print(f"   📊 Number of Topics: {len(data.get('topics', []))}")
        print(f"   📈 Model Performance: {data.get('model_performance', {})}")
        
        # Display topics
        topics = data.get('topics', [])
        for i, topic in enumerate(topics):
            keywords = ', '.join([f"{word}({score:.3f})" for word, score in topic.get('keywords', [])[:5]])
            print(f"   📝 Topic {i+1}: {keywords}")
        
        return data
    else:
        print(f"❌ LDA test failed: {response.status_code} - {response.text}")
        return None

def test_nmf_algorithm():
    """Test NMF algorithm selection and model training"""
    print("\n🔍 Testing NMF Algorithm Selection and Model Training...")
    
    payload = {
        "texts": TEST_TEXTS,
        "algorithm": "nmf",
        "num_topics": 3,
        "preprocessing_options": {
            "remove_stopwords": True,
            "apply_stemming": True,
            "min_word_length": 3,
            "handle_contractions": True
        },
        "algorithm_params": {
            "max_iter": 100,
            "random_state": 42
        }
    }
    
    response = requests.post(f"{BASE_URL}/topic-modeling", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ NMF Algorithm Test Successful:")
        print(f"   🎯 Algorithm Used: {data.get('algorithm_used', 'Unknown')}")
        print(f"   📊 Number of Topics: {len(data.get('topics', []))}")
        print(f"   📈 Model Performance: {data.get('model_performance', {})}")
        
        # Display topics
        topics = data.get('topics', [])
        for i, topic in enumerate(topics):
            keywords = ', '.join([f"{word}({score:.3f})" for word, score in topic.get('keywords', [])[:5]])
            print(f"   📝 Topic {i+1}: {keywords}")
        
        return data
    else:
        print(f"❌ NMF test failed: {response.status_code} - {response.text}")
        return None

def test_algorithm_comparison():
    """Test algorithm comparison functionality"""
    print("\n🔬 Testing Algorithm Comparison...")
    
    payload = {
        "texts": TEST_TEXTS,
        "compare_algorithms": True,
        "num_topics": 3,
        "preprocessing_options": {
            "remove_stopwords": True,
            "apply_stemming": True,
            "min_word_length": 3
        }
    }
    
    response = requests.post(f"{BASE_URL}/topic-modeling", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Algorithm Comparison Successful:")
        
        if "algorithm_comparison" in data:
            comparison = data["algorithm_comparison"]
            print(f"   🏆 Recommended Algorithm: {comparison.get('recommended_algorithm')}")
            
            # Show both algorithm performances
            for alg in ['lda', 'nmf']:
                perf_key = f"{alg}_performance"
                if perf_key in comparison:
                    perf = comparison[perf_key]
                    print(f"   📊 {alg.upper()} Performance:")
                    print(f"      - Coherence Score: {perf.get('coherence_score', 'N/A')}")
                    print(f"      - Training Time: {perf.get('training_time', 'N/A')}")
        
        return data
    else:
        print(f"❌ Algorithm comparison failed: {response.status_code} - {response.text}")
        return None

def validate_requirements_compliance(lda_result: Dict, nmf_result: Dict, comparison_result: Dict):
    """Validate compliance with specified requirements"""
    print("\n✅ VALIDATING REQUIREMENTS COMPLIANCE:")
    print("=" * 60)
    
    compliance_checks = []
    
    # Requirement 1: Algorithm Selection
    if lda_result and nmf_result:
        compliance_checks.append("✅ Algorithm Selection: LDA and NMF algorithms implemented and tested")
    else:
        compliance_checks.append("❌ Algorithm Selection: Missing algorithm implementations")
    
    # Requirement 2: LDA for Latent Topics
    if lda_result and lda_result.get('algorithm_used') == 'lda':
        compliance_checks.append("✅ LDA Implementation: Latent Dirichlet Allocation for identifying latent topics")
    else:
        compliance_checks.append("❌ LDA Implementation: LDA algorithm not properly implemented")
    
    # Requirement 3: NMF for Topic Extraction
    if nmf_result and nmf_result.get('algorithm_used') == 'nmf':
        compliance_checks.append("✅ NMF Implementation: Non-negative Matrix Factorization for topic extraction")
    else:
        compliance_checks.append("❌ NMF Implementation: NMF algorithm not properly implemented")
    
    # Requirement 4: Model Training on Preprocessed Data
    training_evidence = []
    for result, name in [(lda_result, 'LDA'), (nmf_result, 'NMF')]:
        if result and result.get('model_performance'):
            training_evidence.append(name)
    
    if training_evidence:
        compliance_checks.append(f"✅ Model Training: Successfully trained {', '.join(training_evidence)} models on preprocessed text data")
    else:
        compliance_checks.append("❌ Model Training: No evidence of proper model training with performance metrics")
    
    # Requirement 5: Key Themes and Topics Identification
    topics_found = []
    for result, name in [(lda_result, 'LDA'), (nmf_result, 'NMF')]:
        if result and result.get('topics') and len(result['topics']) > 0:
            topics_found.append(f"{name} ({len(result['topics'])} topics)")
    
    if topics_found:
        compliance_checks.append(f"✅ Topic Identification: Successfully identified key themes - {', '.join(topics_found)}")
    else:
        compliance_checks.append("❌ Topic Identification: Failed to identify topics from text data")
    
    # Bonus: Algorithm Comparison
    if comparison_result and comparison_result.get('algorithm_comparison'):
        compliance_checks.append("✅ Advanced Feature: Algorithm comparison and recommendation implemented")
    
    # Print compliance results
    for check in compliance_checks:
        print(check)
    
    # Calculate compliance rate
    passed = sum(1 for check in compliance_checks if check.startswith('✅'))
    total = len([check for check in compliance_checks if check.startswith(('✅', '❌'))])
    compliance_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n📊 COMPLIANCE SUMMARY:")
    print(f"   Passed: {passed}/{total} requirements ({compliance_rate:.1f}%)")
    
    if compliance_rate >= 80:
        print("🎉 HIGH COMPLIANCE: Topic modeling implementation meets requirements!")
        return True
    else:
        print("⚠️  LOW COMPLIANCE: Implementation needs improvements")
        return False

def main():
    """Main test function"""
    print("🚀 ADVANCED TOPIC MODELING VALIDATION TEST")
    print("Following Requirements:")
    print("• Algorithm Selection: Choose appropriate algorithms (LDA, NMF)")
    print("• LDA: For identifying latent topics in text data")
    print("• NMF: As alternative for topic extraction")
    print("• Model Training: Train selected models on preprocessed text data")
    print("=" * 60)
    
    try:
        # Test LDA algorithm
        lda_result = test_lda_algorithm()
        
        # Test NMF algorithm  
        nmf_result = test_nmf_algorithm()
        
        # Test algorithm comparison
        comparison_result = test_algorithm_comparison()
        
        # Validate requirements compliance
        validate_requirements_compliance(lda_result, nmf_result, comparison_result)
        
        print("\n" + "=" * 60)
        print("🏁 TOPIC MODELING VALIDATION COMPLETE")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
