#!/usr/bin/env python3
"""
Test script to validate the advanced topic modeling implementation
following the specified requirements:
- Algorithm Selection: LDA and NMF algorithms
- Model Training: Train models on preprocessed text data
- Topic Identification: Identify key themes and topics
"""

import requests
import json
import time
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

def test_preprocessing_and_storage(texts: list) -> str:
    """Test text preprocessing and storage"""
    print("🔄 Testing text preprocessing and storage...")
    
    # Store texts
    payload = {
        "texts": texts,
        "metadata": {"source": "topic_modeling_test", "type": "sample_data"}
    }
    
    response = requests.post(f"{BASE_URL}/texts/store", json=payload)
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Texts stored successfully with session_id: {session_id}")
        return session_id
    else:
        print(f"❌ Failed to store texts: {response.status_code} - {response.text}")
        return None

def test_algorithm_selection_and_training(session_id: str) -> Dict[str, Any]:
    """Test algorithm selection and model training"""
    print("\n🎯 Testing Algorithm Selection and Model Training...")
    
    # Test with different algorithms
    algorithms_to_test = ["lda", "nmf"]
    results = {}
    
    for algorithm in algorithms_to_test:
        print(f"\n📊 Testing {algorithm.upper()} Algorithm:")
        
        payload = {
            "algorithm": algorithm,
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
        
        response = requests.post(f"{BASE_URL}/analyze/topics/{session_id}", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            results[algorithm] = data
            
            print(f"✅ {algorithm.upper()} Model Training Successful:")
            print(f"   📈 Model Performance: {data.get('model_performance', {})}")
            print(f"   🔍 Number of Topics: {len(data.get('topics', []))}")
            print(f"   ⚙️  Algorithm Used: {data.get('algorithm_used')}")
            
            # Display topics
            topics = data.get('topics', [])
            for i, topic in enumerate(topics[:2]):  # Show first 2 topics
                keywords = ', '.join([f"{word}({score:.3f})" for word, score in topic.get('keywords', [])[:5]])
                print(f"   📝 Topic {i+1}: {keywords}")
        else:
            print(f"❌ {algorithm.upper()} failed: {response.status_code} - {response.text}")
            results[algorithm] = None
    
    return results

def test_model_comparison(session_id: str) -> Dict[str, Any]:
    """Test model comparison and algorithm recommendation"""
    print("\n🔬 Testing Model Comparison and Algorithm Recommendation...")
    
    payload = {
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
        print("✅ Model Comparison Successful:")
        
        if "algorithm_comparison" in data:
            comparison = data["algorithm_comparison"]
            print(f"   🏆 Recommended Algorithm: {comparison.get('recommended_algorithm')}")
            print(f"   📊 LDA Coherence Score: {comparison.get('lda_performance', {}).get('coherence_score', 'N/A')}")
            print(f"   📊 NMF Coherence Score: {comparison.get('nmf_performance', {}).get('coherence_score', 'N/A')}")
        
        if "best_model_results" in data:
            best_results = data["best_model_results"]
            print(f"   🎯 Best Model Algorithm: {best_results.get('algorithm_used')}")
            print(f"   📈 Training Performance: {best_results.get('model_performance', {})}")
        
        return data
    else:
        print(f"❌ Model comparison failed: {response.status_code} - {response.text}")
        return None

def validate_requirements_compliance(results: Dict[str, Any]) -> bool:
    """Validate that implementation follows the specified requirements"""
    print("\n✅ VALIDATING REQUIREMENTS COMPLIANCE:")
    
    compliance_checks = {
        "algorithm_selection": False,
        "lda_implementation": False,
        "nmf_implementation": False,
        "model_training": False,
        "topic_identification": False,
        "preprocessing_integration": False
    }
    
    # Check Algorithm Selection
    if results.get("lda") and results.get("nmf"):
        compliance_checks["algorithm_selection"] = True
        print("✅ Algorithm Selection: LDA and NMF algorithms implemented")
    
    # Check LDA Implementation
    if results.get("lda") and results["lda"].get("algorithm_used") == "lda":
        compliance_checks["lda_implementation"] = True
        print("✅ LDA Implementation: Latent Dirichlet Allocation for identifying latent topics")
    
    # Check NMF Implementation
    if results.get("nmf") and results["nmf"].get("algorithm_used") == "nmf":
        compliance_checks["nmf_implementation"] = True
        print("✅ NMF Implementation: Non-negative Matrix Factorization for topic extraction")
    
    # Check Model Training
    training_evidence = False
    for alg in ["lda", "nmf"]:
        if results.get(alg) and results[alg].get("model_performance"):
            training_evidence = True
            break
    
    if training_evidence:
        compliance_checks["model_training"] = True
        print("✅ Model Training: Models trained on preprocessed text data with performance metrics")
    
    # Check Topic Identification
    topics_found = False
    for alg in ["lda", "nmf"]:
        if results.get(alg) and results[alg].get("topics"):
            topics_found = True
            break
    
    if topics_found:
        compliance_checks["topic_identification"] = True
        print("✅ Topic Identification: Key themes and topics identified successfully")
    
    # Check Preprocessing Integration
    preprocessing_used = False
    for alg in ["lda", "nmf"]:
        if results.get(alg) and results[alg].get("preprocessing_applied"):
            preprocessing_used = True
            break
    
    if preprocessing_used:
        compliance_checks["preprocessing_integration"] = True
        print("✅ Preprocessing Integration: Text preprocessing applied before model training")
    
    # Overall compliance
    total_checks = len(compliance_checks)
    passed_checks = sum(compliance_checks.values())
    compliance_rate = (passed_checks / total_checks) * 100
    
    print(f"\n📊 COMPLIANCE SUMMARY: {passed_checks}/{total_checks} requirements met ({compliance_rate:.1f}%)")
    
    if compliance_rate >= 100:
        print("🎉 FULL COMPLIANCE: All topic modeling requirements successfully implemented!")
        return True
    else:
        print("⚠️  PARTIAL COMPLIANCE: Some requirements need attention")
        return False

def main():
    """Main test function"""
    print("🚀 ADVANCED TOPIC MODELING VALIDATION TEST")
    print("=" * 60)
    
    try:
        # Test preprocessing and storage
        session_id = test_preprocessing_and_storage(TEST_TEXTS)
        if not session_id:
            return
        
        # Wait for processing
        time.sleep(2)
        
        # Test algorithm selection and training
        algorithm_results = test_algorithm_selection_and_training(session_id)
        
        # Test model comparison
        comparison_results = test_model_comparison(session_id)
        
        # Validate requirements compliance
        validate_requirements_compliance(algorithm_results)
        
        print("\n" + "=" * 60)
        print("🏁 TOPIC MODELING VALIDATION COMPLETE")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
