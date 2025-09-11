#!/usr/bin/env python3
"""
🎭 Advanced Sentiment Analysis Validation Test
Following Specified Requirements:
● Sentiment Detection: Implement sentiment analysis algorithms to assess the emotional tone 
  of the identified topics, categorizing sentiments as positive, negative, or neutral.
● Integration: Combine sentiment analysis results with topic modeling to provide 
  a comprehensive view of the data.
"""

import requests
import json
import time
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"

# Test data with mixed sentiments for comprehensive testing
SENTIMENT_TEST_TEXTS = [
    # Positive sentiment texts
    "This innovative technology is absolutely amazing and revolutionary. It brings excellent solutions and outstanding benefits to users worldwide.",
    "I love how this advanced platform enhances user experience with fantastic features. The implementation is brilliant and truly impressive.",
    "The breakthrough developments in artificial intelligence are wonderful and provide incredible opportunities for growth and success.",
    
    # Negative sentiment texts  
    "This terrible system has awful problems and disappointing performance. The implementation is completely broken and useless for any purpose.",
    "I hate how this outdated platform creates frustrating issues and horrible user experiences. The design is fundamentally flawed and inadequate.",
    "The concerning limitations and troubling barriers in this technology pose serious threats and significant risks to user satisfaction.",
    
    # Neutral sentiment texts
    "This system provides standard functionality with regular features. The platform offers basic capabilities for general use cases.",
    "The technology includes typical components and conventional methods. Users can access standard tools and normal operations.",
    "The implementation follows established patterns and uses common approaches for delivering consistent results."
]

TOPIC_SENTIMENT_TEST_TEXTS = [
    # Technology topics with sentiment
    "Machine learning algorithms are revolutionizing healthcare with amazing diagnostic capabilities and excellent patient outcomes.",
    "Artificial intelligence poses serious concerns and troubling ethical challenges that need immediate attention and careful consideration.",
    "Cloud computing platforms provide standard infrastructure services with typical scalability and regular maintenance requirements.",
    
    # Business topics with sentiment  
    "Digital transformation initiatives are delivering fantastic results and outstanding improvements in operational efficiency across organizations.",
    "Economic uncertainties create significant worries and devastating impacts on business growth and financial stability worldwide.",
    "Market analysis shows conventional trends and normal fluctuations within expected parameters for quarterly performance.",
    
    # Environmental topics with sentiment
    "Renewable energy solutions offer incredible benefits and wonderful opportunities for sustainable development and environmental protection.",
    "Climate change effects cause terrible damage and horrific consequences for ecosystems and communities around the globe.",
    "Environmental monitoring systems collect standard data and provide regular reports on atmospheric conditions and measurements."
]

def test_sentiment_detection_requirement():
    """
    Test Requirement: Sentiment Detection
    ● Implement sentiment analysis algorithms to assess the emotional tone of identified topics, 
      categorizing sentiments as positive, negative, or neutral.
    """
    print("🔍 TESTING SENTIMENT DETECTION REQUIREMENT")
    print("=" * 60)
    
    results = {
        'positive_detection': [],
        'negative_detection': [],
        'neutral_detection': [],
        'categorization_accuracy': 0.0
    }
    
    # Test individual sentiment detection
    expected_sentiments = ['positive'] * 3 + ['negative'] * 3 + ['neutral'] * 3
    detected_sentiments = []
    
    for i, text in enumerate(SENTIMENT_TEST_TEXTS):
        expected = expected_sentiments[i]
        
        payload = {"text": text}
        response = requests.post(f"{BASE_URL}/sentiment-analysis", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            detected = data.get('overall_sentiment', 'unknown')
            detected_sentiments.append(detected)
            
            print(f"📝 Text {i+1} ({expected} expected):")
            print(f"   🎯 Detected: {detected}")
            print(f"   📊 Confidence: {data.get('overall_confidence', 0):.2f}")
            print(f"   ✅ Correct: {'✅' if detected == expected else '❌'}")
            
            # Store results by category
            results[f"{expected}_detection"].append({
                'text_id': i+1,
                'expected': expected,
                'detected': detected,
                'confidence': data.get('overall_confidence', 0),
                'correct': detected == expected
            })
        else:
            print(f"❌ Failed to analyze text {i+1}: {response.status_code}")
            detected_sentiments.append('error')
    
    # Calculate accuracy
    correct_detections = sum(1 for exp, det in zip(expected_sentiments, detected_sentiments) if exp == det)
    accuracy = correct_detections / len(expected_sentiments) * 100
    results['categorization_accuracy'] = accuracy
    
    print(f"\n📊 SENTIMENT DETECTION RESULTS:")
    print(f"   🎯 Overall Accuracy: {accuracy:.1f}% ({correct_detections}/{len(expected_sentiments)})")
    print(f"   ✅ Positive Detection: {len([r for r in results['positive_detection'] if r['correct']])}/3 correct")
    print(f"   ✅ Negative Detection: {len([r for r in results['negative_detection'] if r['correct']])}/3 correct") 
    print(f"   ✅ Neutral Detection: {len([r for r in results['neutral_detection'] if r['correct']])}/3 correct")
    
    return results

def test_integration_requirement():
    """
    Test Requirement: Integration
    ● Combine sentiment analysis results with topic modeling to provide a comprehensive view of the data.
    """
    print("\n🔗 TESTING INTEGRATION REQUIREMENT")
    print("=" * 60)
    
    integration_results = {}
    
    # Test 1: Full Sentiment-Topic Integration
    print("🧠 Test 1: Full Sentiment-Topic Integration")
    payload = {
        "texts": TOPIC_SENTIMENT_TEST_TEXTS,
        "topic_modeling_algorithm": "lda",
        "num_topics": 3,
        "options": {
            "preprocessing_options": {
                "remove_stopwords": True,
                "apply_stemming": True
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/sentiment-topic-integration", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        integration_results['full_integration'] = data
        
        print("✅ Full Integration Successful:")
        print(f"   📊 Topics Analyzed: {len(data.get('topic_sentiment_analysis', []))}")
        print(f"   🎭 Sentiment Categories: {list(data.get('comprehensive_insights', {}).get('overall_sentiment_distribution', {}).keys())}")
        print(f"   📈 Matrix Generated: {'✅' if data.get('sentiment_topic_matrix') else '❌'}")
        print(f"   💡 Recommendations: {len(data.get('recommendations', []))}")
        
        # Show topic-sentiment combinations
        for i, topic_analysis in enumerate(data.get('topic_sentiment_analysis', [])[:2]):
            topic_label = topic_analysis.get('topic_label', f'Topic {i+1}')
            if 'texts_sentiment' in topic_analysis:
                dominant_sentiment = topic_analysis['texts_sentiment']['dominant_sentiment']
                print(f"   🏷️  {topic_label}: {dominant_sentiment} sentiment")
    else:
        print(f"❌ Full integration failed: {response.status_code} - {response.text}")
        integration_results['full_integration'] = None
    
    # Test 2: Comprehensive View Integration
    print("\n📊 Test 2: Comprehensive Data View Integration")
    
    payload = {
        "texts": TOPIC_SENTIMENT_TEST_TEXTS[:6],  # Use subset for faster processing
        "sentiment_options": {
            "detailed_analysis": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/comprehensive-sentiment-topic-view", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        integration_results['comprehensive_view'] = data
        
        print("✅ Comprehensive View Integration Successful:")
        print(f"   📊 Analysis Overview: {data.get('analysis_overview', {})}")
        print(f"   🧠 Topic Results: {'✅' if data.get('topic_modeling_results') else '❌'}")
        print(f"   🎭 Sentiment Results: {'✅' if data.get('individual_sentiment_results') else '❌'}")
        print(f"   🔗 Integrated Analysis: {'✅' if data.get('integrated_analysis') else '❌'}")
        print(f"   💡 Comprehensive Insights: {'✅' if data.get('comprehensive_insights') else '❌'}")
        
        # Show compliance
        compliance = data.get('requirements_compliance', {})
        for requirement, status in compliance.items():
            print(f"   {status} {requirement.replace('_', ' ').title()}")
    else:
        print(f"❌ Comprehensive view integration failed: {response.status_code} - {response.text}")
        integration_results['comprehensive_view'] = None
    
    return integration_results

def validate_requirements_compliance(sentiment_results: Dict, integration_results: Dict):
    """Validate complete compliance with specified requirements"""
    print("\n✅ VALIDATING REQUIREMENTS COMPLIANCE")
    print("=" * 60)
    
    compliance_checks = []
    
    # Requirement 1: Sentiment Detection
    if sentiment_results and sentiment_results['categorization_accuracy'] >= 70:
        compliance_checks.append("✅ Sentiment Detection: Successfully implemented algorithms to assess emotional tone, categorizing as positive, negative, neutral")
        sentiment_detection_passed = True
    else:
        compliance_checks.append("❌ Sentiment Detection: Algorithm implementation needs improvement for emotional tone assessment")
        sentiment_detection_passed = False
    
    # Check specific categorization capabilities
    if sentiment_results:
        pos_correct = len([r for r in sentiment_results['positive_detection'] if r['correct']])
        neg_correct = len([r for r in sentiment_results['negative_detection'] if r['correct']])
        neu_correct = len([r for r in sentiment_results['neutral_detection'] if r['correct']])
        
        if pos_correct >= 2 and neg_correct >= 2 and neu_correct >= 2:
            compliance_checks.append("✅ Categorization Quality: Positive, negative, and neutral sentiment categories properly implemented")
        else:
            compliance_checks.append("❌ Categorization Quality: Some sentiment categories need improvement")
    
    # Requirement 2: Integration  
    integration_passed = False
    if integration_results and integration_results.get('full_integration') and integration_results.get('comprehensive_view'):
        compliance_checks.append("✅ Integration: Successfully combined sentiment analysis results with topic modeling for comprehensive data view")
        integration_passed = True
    else:
        compliance_checks.append("❌ Integration: Sentiment-topic integration implementation incomplete")
    
    # Check integration features
    if integration_results and integration_results.get('full_integration'):
        full_integration = integration_results['full_integration']
        
        features_present = []
        if full_integration.get('topic_sentiment_analysis'):
            features_present.append("topic-sentiment analysis")
        if full_integration.get('comprehensive_insights'):
            features_present.append("comprehensive insights")
        if full_integration.get('sentiment_topic_matrix'):
            features_present.append("sentiment-topic matrix")
        if full_integration.get('recommendations'):
            features_present.append("actionable recommendations")
        
        if len(features_present) >= 3:
            compliance_checks.append(f"✅ Integration Features: {', '.join(features_present)} successfully implemented")
        else:
            compliance_checks.append("❌ Integration Features: Missing key integration components")
    
    # Print all compliance results
    for check in compliance_checks:
        print(check)
    
    # Calculate overall compliance
    passed_checks = sum(1 for check in compliance_checks if check.startswith('✅'))
    total_checks = len(compliance_checks)
    compliance_rate = (passed_checks / total_checks) * 100
    
    print(f"\n📊 OVERALL COMPLIANCE SUMMARY:")
    print(f"   Passed: {passed_checks}/{total_checks} checks ({compliance_rate:.1f}%)")
    
    if compliance_rate >= 80 and sentiment_detection_passed and integration_passed:
        print("🎉 HIGH COMPLIANCE: Sentiment analysis implementation meets specified requirements!")
        return True
    else:
        print("⚠️  COMPLIANCE NEEDS IMPROVEMENT: Some requirements need attention")
        return False

def main():
    """Main validation function"""
    print("🎭 ADVANCED SENTIMENT ANALYSIS VALIDATION")
    print("Following Specified Requirements:")
    print("● Sentiment Detection: Assess emotional tone of topics (positive, negative, neutral)")
    print("● Integration: Combine sentiment analysis with topic modeling for comprehensive view")
    print("=" * 80)
    
    try:
        # Test Sentiment Detection requirement
        sentiment_results = test_sentiment_detection_requirement()
        
        # Test Integration requirement
        integration_results = test_integration_requirement()
        
        # Validate overall compliance
        validate_requirements_compliance(sentiment_results, integration_results)
        
        print("\n" + "=" * 80)
        print("🏁 SENTIMENT ANALYSIS VALIDATION COMPLETE")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
