'use client'

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, FileText, Sparkles, TrendingUp, Clock } from 'lucide-react';

interface SummarizationResult {
  original_text: string;
  summary: string;
  key_sentences: string[];
  sentence_scores: { [key: string]: number };
  method_used: string;
  compression_ratio: number;
  word_count_original: number;
  word_count_summary: number;
}

export default function TextSummaryResults() {
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState<SummarizationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [method, setMethod] = useState<'abstractive' | 'tfidf' | 'frequency'>('abstractive');
  const [maxSentences, setMaxSentences] = useState(3);
  const [error, setError] = useState<string | null>(null);
  // Removed per-topic summaries; we show only overall dataset summary

  const datasetSummary = (() => {
    if (typeof window === 'undefined') return null as null | { summary: string; method_used?: string; key_sentences?: string[] };
    try {
      const raw = localStorage.getItem('analysisResults');
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed?.dataset_summary ?? null;
    } catch {
      return null;
    }
  })();

  const handleSummarize = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to summarize');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/text-summarization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          method: method,
          max_sentences: maxSentences
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to analyze text. Please make sure the backend server is running on http://localhost:8000');
    } finally {
      setIsLoading(false);
    }
  };

  const getSentenceImportance = (sentence: string, scores: { [key: string]: number }) => {
    const score = scores[sentence] || 0;
    const maxScore = Math.max(...Object.values(scores));
    return Math.round((score / maxScore) * 100);
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 80) return 'bg-red-500';
    if (importance >= 60) return 'bg-orange-500';
    if (importance >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-6">
      {/* Overall Dataset Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Overall Dataset Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {datasetSummary ? (
            <div className="p-4 rounded-lg border bg-blue-50">
              <div className="flex items-center justify-between mb-2">
                <div className="font-medium">Summary</div>
                {datasetSummary.method_used && (
                  <Badge variant="outline" className="text-xs">{datasetSummary.method_used}</Badge>
                )}
              </div>
              <p className="text-gray-800 leading-relaxed">{datasetSummary.summary}</p>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">Run an analysis to see the overall dataset summary.</div>
          )}
        </CardContent>
      </Card>

      {/* Input Section (optional custom text summarization) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Text Summarization
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Enter text to summarize</label>
            <Textarea
              placeholder="Enter your text here for summarization..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="min-h-[120px] resize-none"
            />
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium">Summarization Method</label>
        <Select value={method} onValueChange={(value: 'abstractive' | 'tfidf' | 'frequency') => setMethod(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
          <SelectItem value="abstractive">Abstractive (BART)</SelectItem>
                  <SelectItem value="frequency">Frequency-based</SelectItem>
                  <SelectItem value="tfidf">TF-IDF</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium">Max Sentences</label>
              <Select value={maxSentences.toString()} onValueChange={(value) => setMaxSentences(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 sentence</SelectItem>
                  <SelectItem value="2">2 sentences</SelectItem>
                  <SelectItem value="3">3 sentences</SelectItem>
                  <SelectItem value="4">4 sentences</SelectItem>
                  <SelectItem value="5">5 sentences</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button 
            onClick={handleSummarize} 
            disabled={isLoading || !inputText.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Clock className="w-4 h-4 mr-2 animate-spin" />
                Summarizing...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Summary
              </>
            )}
          </Button>

          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </CardContent>
  </Card>

      {/* Results Section */}
  {results && (
        <div className="space-y-6">
          {/* Summary Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Summary Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{results.word_count_original}</div>
                  <div className="text-sm text-gray-600">Original Words</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{results.word_count_summary}</div>
                  <div className="text-sm text-gray-600">Summary Words</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.round((1 - results.compression_ratio) * 100)}%
                  </div>
                  <div className="text-sm text-gray-600">Compression</div>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.key_sentences.length}
                  </div>
                  <div className="text-sm text-gray-600">Key Sentences</div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Compression Ratio</span>
                  <span>{Math.round(results.compression_ratio * 100)}%</span>
                </div>
                <Progress value={results.compression_ratio * 100} className="h-2" />
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="outline" className="capitalize">
                  {results.method_used}
                </Badge>
                <Badge variant="secondary">
                  {results.key_sentences.length} sentences selected
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Generated Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Generated Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                <p className="text-gray-800 leading-relaxed">{results.summary}</p>
              </div>
            </CardContent>
          </Card>

          {/* Key Sentences */}
          <Card>
            <CardHeader>
              <CardTitle>Key Sentences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {results.key_sentences.map((sentence, index) => {
                const importance = getSentenceImportance(sentence, results.sentence_scores);
                return (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <span className="text-sm font-medium text-blue-600">
                        Sentence {index + 1}
                      </span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {importance}% importance
                        </Badge>
                        <div className={`w-3 h-3 rounded-full ${getImportanceColor(importance)}`} />
                      </div>
                    </div>
                    <p className="text-gray-800">{sentence}</p>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* All Sentence Scores */}
          <Card>
            <CardHeader>
              <CardTitle>All Sentence Scores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(results.sentence_scores)
                .sort(([, a], [, b]) => b - a)
                .map(([sentenceText, score], index) => {
                  const importance = Math.round((score / Math.max(...Object.values(results.sentence_scores))) * 100);
                  const isKeySentence = results.key_sentences.includes(sentenceText);
                  return (
                    <div 
                      key={index} 
                      className={`p-3 rounded-lg border ${isKeySentence ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            Score: {score.toFixed(3)}
                          </span>
                          {isKeySentence && (
                            <Badge className="text-xs">Selected</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={importance} className="w-16 h-2" />
                          <span className="text-xs text-gray-500">{importance}%</span>
                        </div>
                      </div>
                      <p className={`text-sm ${isKeySentence ? 'text-blue-800' : 'text-gray-700'}`}>
                        {sentenceText}
                      </p>
                    </div>
                  );
                })}
            </CardContent>
          </Card>
        </div>
  )}
    </div>
  );
}
