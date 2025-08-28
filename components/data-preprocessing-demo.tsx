'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, FileText, BarChart3, Clock, Zap } from 'lucide-react';

interface PreprocessingResult {
  originalText: string;
  cleanedText: string;
  normalizedText: string;
  tokens: string[];
  stats: {
    originalLength: number;
    cleanedLength: number;
    normalizedLength: number;
    tokenCount: number;
    processingTime: number;
  };
}

export default function DataPreprocessingDemo() {
  const [inputText, setInputText] = useState(`This is a COMPREHENSIVE text for preprocessing!!! It contains URLs like https://example.com/path?param=1, emails like user@test-domain.co.uk, social mentions @john_doe, hashtags #AI #MachineLearning, numbers like 123.45, contractions like won't, can't, it's, and various punctuation marks... Are we ready for advanced analysis? 😊✨ Let's see how stemming works with running, runner, runs, and beautiful, beautifully, beauty!`);
  const [result, setResult] = useState<PreprocessingResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Comprehensive stop words list (matching Python NLTK stopwords)
  const stopWords = new Set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
    'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
    'now', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn',
    'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'
  ]);

  // Simple stemming function (Porter stemmer-like rules)
  const stem = (word: string): string => {
    // Handle common suffixes
    if (word.endsWith('ing') && word.length > 5) {
      return word.slice(0, -3);
    }
    if (word.endsWith('ed') && word.length > 4) {
      return word.slice(0, -2);
    }
    if (word.endsWith('er') && word.length > 4) {
      return word.slice(0, -2);
    }
    if (word.endsWith('est') && word.length > 5) {
      return word.slice(0, -3);
    }
    if (word.endsWith('ly') && word.length > 4) {
      return word.slice(0, -2);
    }
    if (word.endsWith('tion') && word.length > 6) {
      return word.slice(0, -4) + 'te';
    }
    if (word.endsWith('ness') && word.length > 6) {
      return word.slice(0, -4);
    }
    return word;
  };

  const processText = useCallback(async () => {
    // Handle missing values and ensure data consistency
    if (!inputText || typeof inputText !== 'string' || !inputText.trim()) {
      setResult({
        originalText: inputText || '',
        cleanedText: '',
        normalizedText: '',
        tokens: [],
        stats: {
          originalLength: 0,
          cleanedLength: 0,
          normalizedLength: 0,
          tokenCount: 0,
          processingTime: 0
        }
      });
      return;
    }

    setIsProcessing(true);
    const startTime = Date.now();

    // Simulate preprocessing steps with delays for demonstration
    await new Promise(resolve => setTimeout(resolve, 500));

    try {
      // Step 1: Text Cleaning (comprehensive)
      let cleanedText = inputText
        .toLowerCase() // Convert to lowercase
        .replace(/https?:\/\/[^\s]+/g, '') // Remove URLs
        .replace(/www\.[^\s]+/g, '') // Remove www links
        .replace(/[\w\.-]+@[\w\.-]+\.\w+/g, '') // Remove emails
        .replace(/@\w+/g, '') // Remove mentions (@username)
        .replace(/#\w+/g, '') // Remove hashtags
        .replace(/\d+/g, ' ') // Remove numbers
        .replace(/[^\w\s]/g, ' ') // Remove all punctuation and special characters
        .replace(/\s+/g, ' ') // Normalize multiple whitespaces to single space
        .trim();

      // Step 2: Text Normalization (contraction expansion)
      let normalizedText = cleanedText
        .replace(/won't/g, 'will not')
        .replace(/can't/g, 'cannot')
        .replace(/n't/g, ' not')
        .replace(/'re/g, ' are')
        .replace(/'ve/g, ' have')
        .replace(/'ll/g, ' will')
        .replace(/'d/g, ' would')
        .replace(/'m/g, ' am')
        .replace(/let's/g, 'let us')
        .replace(/that's/g, 'that is')
        .replace(/who's/g, 'who is')
        .replace(/what's/g, 'what is')
        .replace(/where's/g, 'where is')
        .replace(/how's/g, 'how is')
        .replace(/it's/g, 'it is')
        .replace(/he's/g, 'he is')
        .replace(/she's/g, 'she is')
        .replace(/\s+/g, ' ') // Normalize whitespace again
        .trim();

      // Step 3: Tokenization with stop word removal and stemming
      const rawTokens = normalizedText
        .split(/\s+/)
        .filter(token => token.length > 0);

      // Filter tokens: remove stop words, short tokens, and apply stemming
      const tokens = rawTokens
        .filter(token => token.length >= 2) // Remove very short tokens
        .filter(token => token.length <= 50) // Remove very long tokens (likely errors)
        .filter(token => !stopWords.has(token)) // Remove stop words
        .map(token => stem(token)) // Apply stemming
        .filter(token => token.length >= 2); // Remove tokens that became too short after stemming

      const processingTime = Date.now() - startTime;

      // Ensure data consistency - validate processed data
      const validatedResult: PreprocessingResult = {
        originalText: inputText,
        cleanedText: cleanedText || '',
        normalizedText: normalizedText || '',
        tokens: tokens || [],
        stats: {
          originalLength: inputText.length,
          cleanedLength: cleanedText.length,
          normalizedLength: normalizedText.length,
          tokenCount: tokens.length,
          processingTime
        }
      };

      setResult(validatedResult);
    } catch (error) {
      console.error('Processing error:', error);
      // Handle errors gracefully - provide empty but valid result
      setResult({
        originalText: inputText,
        cleanedText: '',
        normalizedText: '',
        tokens: [],
        stats: {
          originalLength: inputText.length,
          cleanedLength: 0,
          normalizedLength: 0,
          tokenCount: 0,
          processingTime: Date.now() - startTime
        }
      });
    } finally {
      setIsProcessing(false);
    }
  }, [inputText]);

  const renderProcessingStep = (title: string, content: string, icon: React.ReactNode) => (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="bg-muted p-3 rounded-lg">
          <code className="text-sm break-words">{content || 'No content to display'}</code>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Data Preprocessing Pipeline</h1>
        <p className="text-muted-foreground">
          AI Narrative Nexus - Text Cleaning, Normalization & Tokenization
        </p>
      </div>

      <div className="w-full">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Input Text</CardTitle>
              <CardDescription>
                Enter text to see the preprocessing pipeline in action
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Enter your text here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <Button 
                onClick={processText} 
                disabled={isProcessing || !inputText.trim()}
                className="w-full"
              >
                {isProcessing ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Process Text
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {result && (
            <div className="space-y-6">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Text processed successfully in {result.stats.processingTime}ms
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{result.stats.originalLength}</div>
                    <p className="text-sm text-muted-foreground">Original Characters</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{result.stats.cleanedLength}</div>
                    <p className="text-sm text-muted-foreground">Cleaned Characters</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{result.stats.normalizedLength}</div>
                    <p className="text-sm text-muted-foreground">Normalized Characters</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{result.stats.tokenCount}</div>
                    <p className="text-sm text-muted-foreground">Final Tokens</p>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                {renderProcessingStep(
                  "Step 1: Original Text",
                  result.originalText,
                  <FileText className="w-4 h-4" />
                )}

                {renderProcessingStep(
                  "Step 2: Text Cleaning (URLs, emails, mentions, hashtags, numbers, punctuation removed)",
                  result.cleanedText,
                  <CheckCircle className="w-4 h-4" />
                )}

                {renderProcessingStep(
                  "Step 3: Text Normalization (contractions expanded, whitespace normalized)",
                  result.normalizedText,
                  <BarChart3 className="w-4 h-4" />
                )}

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Zap className="w-4 h-4" />
                      Step 4: Tokenization + Stop Word Removal + Stemming
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-3">
                      <p className="text-sm text-muted-foreground mb-2">
                        Tokens after removing stop words and applying Porter stemming:
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {result.tokens.map((token, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {token}
                        </Badge>
                      ))}
                      {result.tokens.length === 0 && (
                        <Badge variant="outline">No meaningful tokens found</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
