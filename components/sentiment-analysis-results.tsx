"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, Smile, Frown, Meh } from 'lucide-react'

interface SentimentResult {
  sentence: string;
  sentiment: string;
  confidence: number;
  positive_score: number;
  negative_score: number;
  neutral_score: number;
}

interface SentimentAnalysisResult {
  overall_sentiment: string;
  overall_confidence: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  emotional_indicators: {
    joy: number;
    sadness: number;
    anger: number;
    fear: number;
  };
  results: SentimentResult[];
  summary: {
    total_sentences: number;
    positive_sentences: number;
    negative_sentences: number;
    neutral_sentences: number;
    average_confidence: number;
  };
}

interface SentimentAnalysisResultsProps {
  results?: SentimentAnalysisResult
}

export function SentimentAnalysisResults({ results }: SentimentAnalysisResultsProps) {
  // Debug: Log what data we're receiving
  console.log("🔍 SentimentAnalysisResults received data:", results)
  
  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return <Smile className="h-4 w-4 text-green-500" />
      case 'negative':
        return <Frown className="h-4 w-4 text-red-500" />
      default:
        return <Meh className="h-4 w-4 text-gray-500" />
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'negative':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (!results) {
    return (
      <Card className="border-border">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-secondary" />
            <CardTitle>Sentiment Analysis Results</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Sentiment analysis results will appear here after analysis</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overall Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getSentimentIcon(results.overall_sentiment)}
            Overall Sentiment Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Sentiment:</span>
            <Badge className={getSentimentColor(results.overall_sentiment)}>
              {results.overall_sentiment.toUpperCase()}
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Confidence:</span>
              <span className="font-medium">{(results.overall_confidence * 100).toFixed(1)}%</span>
            </div>
            <Progress value={results.overall_confidence * 100} className="w-full" />
          </div>

          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center p-2 bg-green-50 rounded-lg border">
              <div className="font-medium text-green-700">Positive</div>
              <div className="text-green-600">{(results.sentiment_distribution.positive * 100).toFixed(1)}%</div>
            </div>
            <div className="text-center p-2 bg-red-50 rounded-lg border">
              <div className="font-medium text-red-700">Negative</div>
              <div className="text-red-600">{(results.sentiment_distribution.negative * 100).toFixed(1)}%</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg border">
              <div className="font-medium text-gray-700">Neutral</div>
              <div className="text-gray-600">{(results.sentiment_distribution.neutral * 100).toFixed(1)}%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emotional Indicators */}
      {results.emotional_indicators && (
        <Card>
          <CardHeader>
            <CardTitle>Emotional Indicators</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(results.emotional_indicators).map(([emotion, score]) => (
                <div key={emotion} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">{emotion}:</span>
                    <span className="font-medium">{(score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={score * 100} className="w-full" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Statistics */}
      {results.summary && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Total Sentences</div>
                <div className="text-gray-900 text-lg font-semibold">{results.summary.total_sentences}</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600">Positive</div>
                <div className="text-green-900 text-lg font-semibold">{results.summary.positive_sentences}</div>
              </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <div className="text-sm text-red-600">Negative</div>
              <div className="text-red-900 text-lg font-semibold">{results.summary.negative_sentences}</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Neutral</div>
              <div className="text-gray-900 text-lg font-semibold">{results.summary.neutral_sentences}</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-600">Avg Confidence</div>
              <div className="text-blue-900 text-lg font-semibold">{(results.summary.average_confidence * 100).toFixed(1)}%</div>
            </div>
          </div>
        </CardContent>
      </Card>
      )}

      {/* Detailed Results */}
      {results.results && (
        <Card>
          <CardHeader>
            <CardTitle>Sentence-by-Sentence Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.results.map((result, index) => (
              <div key={index} className="p-3 border rounded-lg">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm">{result.sentence}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getSentimentIcon(result.sentiment)}
                    <Badge variant="outline" className={getSentimentColor(result.sentiment)}>
                      {result.sentiment}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      )}
    </div>
  )
}
