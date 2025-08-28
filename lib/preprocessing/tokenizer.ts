/**
 * Tokenization Utilities for AI Narrative Nexus
 * Implements various tokenization strategies for text analysis
 */

export interface TokenizationOptions {
  splitOnWhitespace?: boolean;
  splitOnPunctuation?: boolean;
  preservePunctuation?: boolean;
  minTokenLength?: number;
  maxTokenLength?: number;
  removeDuplicates?: boolean;
  preserveCase?: boolean;
  splitOnNumbers?: boolean;
  preserveNumbers?: boolean;
}

export interface TokenMetrics {
  totalTokens: number;
  uniqueTokens: number;
  averageTokenLength: number;
  tokenLengthDistribution: Record<number, number>;
  longestToken: string;
  shortestToken: string;
  vocabularyDiversity: number; // unique tokens / total tokens
}

export class Tokenizer {
  private options: Required<TokenizationOptions>;

  constructor(options: TokenizationOptions = {}) {
    this.options = {
      splitOnWhitespace: true,
      splitOnPunctuation: true,
      preservePunctuation: false,
      minTokenLength: 1,
      maxTokenLength: 50,
      removeDuplicates: false,
      preserveCase: false,
      splitOnNumbers: false,
      preserveNumbers: true,
      ...options
    };
  }

  /**
   * Tokenize text into an array of tokens
   */
  tokenize(text: string): string[] {
    if (!text || typeof text !== 'string') {
      return [];
    }

    let tokens: string[] = [];

    // Start with the basic text
    let processedText = text;

    // Handle case preservation
    if (!this.options.preserveCase) {
      processedText = processedText.toLowerCase();
    }

    // Apply different tokenization strategies
    if (this.options.splitOnWhitespace && this.options.splitOnPunctuation) {
      tokens = this.whitespaceAndPunctuationTokenize(processedText);
    } else if (this.options.splitOnWhitespace) {
      tokens = this.whitespaceTokenize(processedText);
    } else if (this.options.splitOnPunctuation) {
      tokens = this.punctuationTokenize(processedText);
    } else {
      // Simple character split as fallback
      tokens = this.characterTokenize(processedText);
    }

    // Filter tokens based on options
    tokens = this.filterTokens(tokens);

    return tokens;
  }

  /**
   * Tokenize multiple texts
   */
  tokenizeTexts(texts: string[]): string[][] {
    return texts.map(text => this.tokenize(text));
  }

  /**
   * Get all unique tokens from text
   */
  getUniqueTokens(text: string): string[] {
    const tokens = this.tokenize(text);
    return [...new Set(tokens)];
  }

  /**
   * Get token frequency map
   */
  getTokenFrequency(text: string): Record<string, number> {
    const tokens = this.tokenize(text);
    const frequency: Record<string, number> = {};
    
    for (const token of tokens) {
      frequency[token] = (frequency[token] || 0) + 1;
    }
    
    return frequency;
  }

  /**
   * Get token metrics for analysis
   */
  getTokenMetrics(text: string): TokenMetrics {
    const tokens = this.tokenize(text);
    const uniqueTokens = [...new Set(tokens)];
    
    const tokenLengths = tokens.map(token => token.length);
    const averageLength = tokenLengths.reduce((sum, len) => sum + len, 0) / tokens.length;
    
    const lengthDistribution: Record<number, number> = {};
    for (const length of tokenLengths) {
      lengthDistribution[length] = (lengthDistribution[length] || 0) + 1;
    }

    const sortedByLength = tokens.sort((a, b) => a.length - b.length);
    
    return {
      totalTokens: tokens.length,
      uniqueTokens: uniqueTokens.length,
      averageTokenLength: averageLength,
      tokenLengthDistribution: lengthDistribution,
      longestToken: sortedByLength[sortedByLength.length - 1] || '',
      shortestToken: sortedByLength[0] || '',
      vocabularyDiversity: uniqueTokens.length / tokens.length
    };
  }

  /**
   * Whitespace-based tokenization
   */
  private whitespaceTokenize(text: string): string[] {
    return text.split(/\s+/).filter(token => token.length > 0);
  }

  /**
   * Punctuation-based tokenization
   */
  private punctuationTokenize(text: string): string[] {
    let tokens: string[] = [];
    
    if (this.options.preservePunctuation) {
      // Split on punctuation but keep it
      tokens = text.split(/([.,;:!?()[\]{}"'-])/).filter(token => token.length > 0);
    } else {
      // Split on punctuation and remove it
      tokens = text.split(/[.,;:!?()[\]{}"'-]+/).filter(token => token.length > 0);
    }
    
    return tokens;
  }

  /**
   * Combined whitespace and punctuation tokenization
   */
  private whitespaceAndPunctuationTokenize(text: string): string[] {
    let tokens: string[] = [];
    
    if (this.options.preservePunctuation) {
      // Split on whitespace and punctuation, preserving punctuation
      tokens = text.split(/(\s+|[.,;:!?()[\]{}"'-])/).filter(token => 
        token.length > 0 && !/^\s+$/.test(token)
      );
    } else {
      // Split on whitespace and punctuation, removing both
      tokens = text.split(/[\s.,;:!?()[\]{}"'-]+/).filter(token => token.length > 0);
    }
    
    return tokens;
  }

  /**
   * Character-level tokenization
   */
  private characterTokenize(text: string): string[] {
    return text.split('').filter(char => char.trim().length > 0);
  }

  /**
   * Filter tokens based on options
   */
  private filterTokens(tokens: string[]): string[] {
    let filtered = tokens;

    // Filter by length
    filtered = filtered.filter(token => 
      token.length >= this.options.minTokenLength && 
      token.length <= this.options.maxTokenLength
    );

    // Handle numbers
    if (!this.options.preserveNumbers) {
      filtered = filtered.filter(token => !/^\d+$/.test(token));
    }

    // Split on numbers if specified
    if (this.options.splitOnNumbers) {
      const newTokens: string[] = [];
      for (const token of filtered) {
        if (/\d/.test(token)) {
          // Split tokens that contain numbers
          const parts = token.split(/(\d+)/).filter(part => part.length > 0);
          newTokens.push(...parts);
        } else {
          newTokens.push(token);
        }
      }
      filtered = newTokens;
    }

    // Remove duplicates if specified
    if (this.options.removeDuplicates) {
      filtered = [...new Set(filtered)];
    }

    return filtered;
  }

  /**
   * Advanced n-gram tokenization
   */
  generateNGrams(text: string, n: number): string[] {
    const tokens = this.tokenize(text);
    const ngrams: string[] = [];
    
    for (let i = 0; i <= tokens.length - n; i++) {
      const ngram = tokens.slice(i, i + n).join(' ');
      ngrams.push(ngram);
    }
    
    return ngrams;
  }

  /**
   * Generate all n-grams from 1 to maxN
   */
  generateAllNGrams(text: string, maxN: number = 3): Record<number, string[]> {
    const result: Record<number, string[]> = {};
    
    for (let n = 1; n <= maxN; n++) {
      result[n] = this.generateNGrams(text, n);
    }
    
    return result;
  }

  /**
   * Sentence tokenization
   */
  tokenizeSentences(text: string): string[] {
    // Simple sentence tokenization based on sentence-ending punctuation
    const sentences = text
      .split(/[.!?]+/)
      .map(sentence => sentence.trim())
      .filter(sentence => sentence.length > 0);
    
    return sentences;
  }

  /**
   * Paragraph tokenization
   */
  tokenizeParagraphs(text: string): string[] {
    return text
      .split(/\n\s*\n/)
      .map(paragraph => paragraph.trim())
      .filter(paragraph => paragraph.length > 0);
  }

  /**
   * Extract keywords based on frequency and length
   */
  extractKeywords(text: string, minFrequency: number = 2, minLength: number = 3): string[] {
    const frequency = this.getTokenFrequency(text);
    
    return Object.entries(frequency)
      .filter(([token, freq]) => freq >= minFrequency && token.length >= minLength)
      .sort(([, freqA], [, freqB]) => freqB - freqA)
      .map(([token]) => token);
  }

  /**
   * Get contextual tokens (tokens around a target token)
   */
  getContextualTokens(text: string, targetToken: string, windowSize: number = 2): string[][] {
    const tokens = this.tokenize(text);
    const contexts: string[][] = [];
    
    for (let i = 0; i < tokens.length; i++) {
      if (tokens[i] === targetToken) {
        const start = Math.max(0, i - windowSize);
        const end = Math.min(tokens.length, i + windowSize + 1);
        const context = tokens.slice(start, end);
        contexts.push(context);
      }
    }
    
    return contexts;
  }
}

// Export default tokenizer instances
export const defaultTokenizer = new Tokenizer();

export const wordTokenizer = new Tokenizer({
  splitOnWhitespace: true,
  splitOnPunctuation: true,
  preservePunctuation: false,
  minTokenLength: 1,
  maxTokenLength: 50,
  removeDuplicates: false,
  preserveCase: false,
  splitOnNumbers: false,
  preserveNumbers: true
});

export const sentenceTokenizer = new Tokenizer({
  splitOnWhitespace: false,
  splitOnPunctuation: true,
  preservePunctuation: true,
  minTokenLength: 5,
  maxTokenLength: 1000,
  removeDuplicates: false,
  preserveCase: true,
  splitOnNumbers: false,
  preserveNumbers: true
});

export const strictTokenizer = new Tokenizer({
  splitOnWhitespace: true,
  splitOnPunctuation: true,
  preservePunctuation: false,
  minTokenLength: 2,
  maxTokenLength: 30,
  removeDuplicates: true,
  preserveCase: false,
  splitOnNumbers: true,
  preserveNumbers: false
});
