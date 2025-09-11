"""
Insight Generation and Summarization Module
As specified in the architecture diagram: "Extracted Themes, Key Insights, Recommendations"
"""

from typing import List, Dict, Tuple, Any
from collections import Counter, defaultdict
import re
import math
import json

class InsightGenerator:
    """
    Insight Generation and Summarization component following the architecture
    Processes results from Sentiment Analysis and Topic Modeling to generate insights
    """
    
    def __init__(self):
        self.min_theme_frequency = 2
        self.confidence_threshold = 0.7
        
    def generate_comprehensive_insights(self, 
                                      sentiment_results: Dict, 
                                      topic_results: Dict,
                                      text_data: Dict) -> Dict:
        """
        Main insight generation method combining all analysis results
        Architecture: Sentiment Analysis + Topic Modeling → Insight Generation
        """
        
        # Extract themes from topic modeling
        extracted_themes = self._extract_themes_from_topics(topic_results)
        
        # Generate key insights from sentiment and topics
        key_insights = self._generate_key_insights(sentiment_results, topic_results, text_data)
        
        # Generate actionable recommendations
        recommendations = self._generate_recommendations(sentiment_results, topic_results, extracted_themes)
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(sentiment_results, topic_results)
        
        return {
            "extracted_themes": extracted_themes,
            "key_insights": key_insights,
            "recommendations": recommendations,
            "confidence_score": confidence_score,
            "summary": self._generate_executive_summary(extracted_themes, key_insights, sentiment_results),
            "processing_metadata": {
                "sentiment_confidence": sentiment_results.get('overall_confidence', 0),
                "topic_coherence": topic_results.get('coherence_score', 0),
                "analysis_timestamp": text_data.get('created_at', ''),
                "text_length": len(text_data.get('original_text', ''))
            }
        }
    
    def _extract_themes_from_topics(self, topic_results: Dict) -> List[Dict]:
        """
        Extract meaningful themes from topic modeling results
        """
        themes = []
        
        if 'topics' in topic_results:
            for topic in topic_results['topics']:
                theme = {
                    'theme_id': topic.get('id', 0),
                    'theme_name': self._generate_theme_name(topic),
                    'keywords': topic.get('keywords', []),
                    'top_words': topic.get('top_words', []),
                    'relevance_score': self._calculate_theme_relevance(topic),
                    'description': self._generate_theme_description(topic)
                }
                themes.append(theme)
        
        # Sort themes by relevance
        themes.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return themes
    
    def _generate_theme_name(self, topic: Dict) -> str:
        """
        Generate a descriptive theme name from topic keywords
        """
        keywords = topic.get('keywords', [])
        if not keywords:
            return f"Theme {topic.get('id', 0) + 1}"
        
        # Use top 2-3 most relevant keywords
        top_keywords = keywords[:3] if len(keywords) >= 3 else keywords
        
        # Create theme name
        if len(top_keywords) >= 2:
            return f"{top_keywords[0].title()} & {top_keywords[1].title()}"
        else:
            return f"{top_keywords[0].title()} Focus"
    
    def _generate_theme_description(self, topic: Dict) -> str:
        """
        Generate a description for the theme
        """
        keywords = topic.get('keywords', [])[:5]  # Top 5 keywords
        
        if not keywords:
            return "No clear theme description available"
        
        return f"This theme focuses on {', '.join(keywords[:-1])} and {keywords[-1]}."
    
    def _calculate_theme_relevance(self, topic: Dict) -> float:
        """
        Calculate theme relevance score
        """
        # Base relevance on number of keywords and their weights
        keywords = topic.get('top_words', [])
        if not keywords:
            return 0.5
        
        # Sum of keyword weights
        total_weight = sum(weight for _, weight in keywords) if keywords else 0
        return min(total_weight, 1.0)
    
    def _generate_key_insights(self, sentiment_results: Dict, topic_results: Dict, text_data: Dict) -> List[Dict]:
        """
        Generate key insights from combined analysis results
        """
        insights = []
        
        # Sentiment-based insights
        sentiment_insights = self._extract_sentiment_insights(sentiment_results)
        insights.extend(sentiment_insights)
        
        # Topic-based insights
        topic_insights = self._extract_topic_insights(topic_results)
        insights.extend(topic_insights)
        
        # Cross-analysis insights
        cross_insights = self._generate_cross_analysis_insights(sentiment_results, topic_results)
        insights.extend(cross_insights)
        
        # Text characteristics insights
        text_insights = self._analyze_text_characteristics(text_data)
        insights.extend(text_insights)
        
        return insights
    
    def _extract_sentiment_insights(self, sentiment_results: Dict) -> List[Dict]:
        """
        Extract key insights from sentiment analysis
        """
        insights = []
        
        overall_sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        confidence = sentiment_results.get('overall_confidence', 0)
        distribution = sentiment_results.get('sentiment_distribution', {})
        emotional_indicators = sentiment_results.get('emotional_indicators', {})
        
        # Overall sentiment insight
        insights.append({
            'type': 'sentiment_overview',
            'category': 'Sentiment Analysis',
            'title': f'Overall Sentiment: {overall_sentiment.title()}',
            'description': f'The text shows a {overall_sentiment} sentiment with {confidence:.1%} confidence.',
            'confidence': confidence,
            'impact': 'high' if confidence > 0.8 else 'medium'
        })
        
        # Emotional indicators insight
        if emotional_indicators:
            dominant_emotion = max(emotional_indicators.items(), key=lambda x: x[1])
            insights.append({
                'type': 'emotional_tone',
                'category': 'Emotional Analysis',
                'title': f'Dominant Emotion: {dominant_emotion[0].title()}',
                'description': f'The text primarily expresses {dominant_emotion[0]} ({dominant_emotion[1]:.1%}).',
                'confidence': dominant_emotion[1],
                'impact': 'high' if dominant_emotion[1] > 0.6 else 'medium'
            })
        
        return insights
    
    def _extract_topic_insights(self, topic_results: Dict) -> List[Dict]:
        """
        Extract key insights from topic modeling
        """
        insights = []
        
        topics = topic_results.get('topics', [])
        num_topics = len(topics)
        coherence_score = topic_results.get('coherence_score', 0)
        
        # Topic diversity insight
        insights.append({
            'type': 'topic_diversity',
            'category': 'Content Analysis',
            'title': f'Content Covers {num_topics} Main Topics',
            'description': f'The analysis identified {num_topics} distinct topics with {coherence_score:.1%} coherence.',
            'confidence': coherence_score,
            'impact': 'high' if num_topics >= 3 else 'medium'
        })
        
        # Most prominent topic
        if topics:
            # Find topic with highest document proportion or most keywords
            most_prominent = max(topics, key=lambda t: len(t.get('keywords', [])))
            insights.append({
                'type': 'prominent_topic',
                'category': 'Content Focus',
                'title': f'Primary Focus: {self._generate_theme_name(most_prominent)}',
                'description': f'The main topic revolves around {", ".join(most_prominent.get("keywords", [])[:3])}.',
                'confidence': 0.8,
                'impact': 'high'
            })
        
        return insights
    
    def _generate_cross_analysis_insights(self, sentiment_results: Dict, topic_results: Dict) -> List[Dict]:
        """
        Generate insights from combining sentiment and topic analysis
        """
        insights = []
        
        sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        topics = topic_results.get('topics', [])
        
        # Sentiment-topic correlation
        if topics and sentiment != 'neutral':
            insights.append({
                'type': 'sentiment_topic_correlation',
                'category': 'Cross-Analysis',
                'title': f'{sentiment.title()} Sentiment Across {len(topics)} Topics',
                'description': f'The {sentiment} sentiment is consistent across the identified topics, suggesting unified perspective.',
                'confidence': 0.75,
                'impact': 'medium'
            })
        
        return insights
    
    def _analyze_text_characteristics(self, text_data: Dict) -> List[Dict]:
        """
        Analyze text characteristics for additional insights
        """
        insights = []
        
        original_text = text_data.get('original_text', '')
        tokens = text_data.get('tokens', [])
        
        if original_text and tokens:
            word_count = len(tokens)
            char_count = len(original_text)
            
            # Text length analysis
            if word_count > 500:
                insights.append({
                    'type': 'text_length',
                    'category': 'Text Characteristics',
                    'title': 'Comprehensive Text Analysis',
                    'description': f'Analyzed {word_count} words across {char_count} characters, providing robust insights.',
                    'confidence': 0.9,
                    'impact': 'high'
                })
            elif word_count < 50:
                insights.append({
                    'type': 'text_length',
                    'category': 'Text Characteristics',
                    'title': 'Brief Text Analysis',
                    'description': f'Short text ({word_count} words) may limit insight depth.',
                    'confidence': 0.6,
                    'impact': 'low'
                })
        
        return insights
    
    def _generate_recommendations(self, sentiment_results: Dict, topic_results: Dict, themes: List[Dict]) -> List[Dict]:
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []
        
        sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        confidence = sentiment_results.get('overall_confidence', 0)
        num_topics = len(topic_results.get('topics', []))
        
        # Sentiment-based recommendations
        if sentiment == 'negative' and confidence > 0.7:
            recommendations.append({
                'category': 'Sentiment Improvement',
                'title': 'Address Negative Sentiment',
                'description': 'Consider reviewing and addressing the concerns expressed in the text.',
                'priority': 'high',
                'actionable_steps': [
                    'Identify specific negative sentiment triggers',
                    'Develop response strategies',
                    'Monitor sentiment changes over time'
                ]
            })
        elif sentiment == 'positive' and confidence > 0.8:
            recommendations.append({
                'category': 'Leverage Positive Sentiment',
                'title': 'Capitalize on Positive Response',
                'description': 'The strong positive sentiment indicates opportunity for amplification.',
                'priority': 'medium',
                'actionable_steps': [
                    'Identify what drives positive sentiment',
                    'Replicate successful elements',
                    'Share positive insights with stakeholders'
                ]
            })
        
        # Topic-based recommendations
        if num_topics > 5:
            recommendations.append({
                'category': 'Content Focus',
                'title': 'Streamline Content Focus',
                'description': 'Multiple topics detected - consider focusing on key themes.',
                'priority': 'medium',
                'actionable_steps': [
                    'Prioritize most important topics',
                    'Consolidate related themes',
                    'Create focused content strategy'
                ]
            })
        
        # Theme-based recommendations
        if themes:
            top_theme = themes[0]
            recommendations.append({
                'category': 'Content Strategy',
                'title': f'Leverage {top_theme["theme_name"]} Theme',
                'description': f'Focus on the prominent {top_theme["theme_name"]} theme for maximum impact.',
                'priority': 'high',
                'actionable_steps': [
                    f'Develop content around {top_theme["theme_name"]}',
                    'Monitor theme performance metrics',
                    'Expand on successful theme elements'
                ]
            })
        
        return recommendations
    
    def _calculate_confidence_score(self, sentiment_results: Dict, topic_results: Dict) -> float:
        """
        Calculate overall confidence score for the insights
        """
        sentiment_conf = sentiment_results.get('overall_confidence', 0)
        topic_conf = topic_results.get('coherence_score', 0)
        
        # Weighted average of confidences
        return (sentiment_conf * 0.6 + topic_conf * 0.4)
    
    def _generate_executive_summary(self, themes: List[Dict], insights: List[Dict], sentiment_results: Dict) -> str:
        """
        Generate executive summary of all insights
        """
        sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        num_themes = len(themes)
        high_impact_insights = [i for i in insights if i.get('impact') == 'high']
        
        summary = f"Analysis reveals {sentiment} sentiment across {num_themes} main themes. "
        summary += f"Generated {len(high_impact_insights)} high-impact insights "
        summary += f"with actionable recommendations for content strategy and sentiment optimization."
        
        if themes:
            primary_theme = themes[0]['theme_name']
            summary += f" Primary focus area identified: {primary_theme}."
        
        return summary

# Global insight generator instance
insight_generator = InsightGenerator()
