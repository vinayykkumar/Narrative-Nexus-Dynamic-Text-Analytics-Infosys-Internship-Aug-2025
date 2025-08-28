/**
 * Text Normalization Utilities for AI Narrative Nexus
 * Implements stemming, lemmatization, and text standardization
 */

export interface NormalizationOptions {
  enableStemming?: boolean;
  enableLemmatization?: boolean;
  normalizeWhitespace?: boolean;
  normalizeCase?: boolean;
  expandContractions?: boolean;
  normalizeNumbers?: boolean;
  removeAccents?: boolean;
}

// Common English contractions mapping
const CONTRACTIONS_MAP: Record<string, string> = {
  "ain't": "am not",
  "aren't": "are not",
  "can't": "cannot",
  "couldn't": "could not",
  "didn't": "did not",
  "doesn't": "does not",
  "don't": "do not",
  "hadn't": "had not",
  "hasn't": "has not",
  "haven't": "have not",
  "he'd": "he would",
  "he'll": "he will",
  "he's": "he is",
  "i'd": "i would",
  "i'll": "i will",
  "i'm": "i am",
  "i've": "i have",
  "isn't": "is not",
  "it'd": "it would",
  "it'll": "it will",
  "it's": "it is",
  "let's": "let us",
  "mightn't": "might not",
  "mustn't": "must not",
  "shan't": "shall not",
  "she'd": "she would",
  "she'll": "she will",
  "she's": "she is",
  "shouldn't": "should not",
  "that's": "that is",
  "there's": "there is",
  "they'd": "they would",
  "they'll": "they will",
  "they're": "they are",
  "they've": "they have",
  "we'd": "we would",
  "we're": "we are",
  "we've": "we have",
  "weren't": "were not",
  "what's": "what is",
  "where's": "where is",
  "who's": "who is",
  "won't": "will not",
  "wouldn't": "would not",
  "you'd": "you would",
  "you'll": "you will",
  "you're": "you are",
  "you've": "you have"
};

// Simple stemming rules (Porter Stemmer simplified)
const STEMMING_RULES = [
  // Step 1a
  { pattern: /sses$/i, replacement: 'ss' },
  { pattern: /ies$/i, replacement: 'i' },
  { pattern: /ss$/i, replacement: 'ss' },
  { pattern: /s$/i, replacement: '' },
  
  // Step 1b
  { pattern: /eed$/i, replacement: 'ee' },
  { pattern: /ing$/i, replacement: '' },
  { pattern: /ed$/i, replacement: '' },
  
  // Step 2
  { pattern: /ational$/i, replacement: 'ate' },
  { pattern: /tional$/i, replacement: 'tion' },
  { pattern: /enci$/i, replacement: 'ence' },
  { pattern: /anci$/i, replacement: 'ance' },
  { pattern: /izer$/i, replacement: 'ize' },
  { pattern: /alli$/i, replacement: 'al' },
  { pattern: /entli$/i, replacement: 'ent' },
  { pattern: /eli$/i, replacement: 'e' },
  { pattern: /ousli$/i, replacement: 'ous' },
  { pattern: /ization$/i, replacement: 'ize' },
  { pattern: /ation$/i, replacement: 'ate' },
  { pattern: /ator$/i, replacement: 'ate' },
  { pattern: /alism$/i, replacement: 'al' },
  { pattern: /iveness$/i, replacement: 'ive' },
  { pattern: /fulness$/i, replacement: 'ful' },
  { pattern: /ousness$/i, replacement: 'ous' },
  { pattern: /aliti$/i, replacement: 'al' },
  { pattern: /iviti$/i, replacement: 'ive' },
  { pattern: /biliti$/i, replacement: 'ble' },
  
  // Step 3
  { pattern: /icate$/i, replacement: 'ic' },
  { pattern: /ative$/i, replacement: '' },
  { pattern: /alize$/i, replacement: 'al' },
  { pattern: /iciti$/i, replacement: 'ic' },
  { pattern: /ical$/i, replacement: 'ic' },
  { pattern: /ful$/i, replacement: '' },
  { pattern: /ness$/i, replacement: '' },
  
  // Step 4
  { pattern: /al$/i, replacement: '' },
  { pattern: /ance$/i, replacement: '' },
  { pattern: /ence$/i, replacement: '' },
  { pattern: /er$/i, replacement: '' },
  { pattern: /ic$/i, replacement: '' },
  { pattern: /able$/i, replacement: '' },
  { pattern: /ible$/i, replacement: '' },
  { pattern: /ant$/i, replacement: '' },
  { pattern: /ement$/i, replacement: '' },
  { pattern: /ment$/i, replacement: '' },
  { pattern: /ent$/i, replacement: '' },
  { pattern: /ion$/i, replacement: '' },
  { pattern: /ou$/i, replacement: '' },
  { pattern: /ism$/i, replacement: '' },
  { pattern: /ate$/i, replacement: '' },
  { pattern: /iti$/i, replacement: '' },
  { pattern: /ous$/i, replacement: '' },
  { pattern: /ive$/i, replacement: '' },
  { pattern: /ize$/i, replacement: '' }
];

// Basic lemmatization dictionary
const LEMMA_DICT: Record<string, string> = {
  'better': 'good',
  'best': 'good',
  'worse': 'bad',
  'worst': 'bad',
  'more': 'much',
  'most': 'much',
  'less': 'little',
  'least': 'little',
  'further': 'far',
  'furthest': 'far',
  'elder': 'old',
  'eldest': 'old',
  'am': 'be',
  'is': 'be',
  'are': 'be',
  'was': 'be',
  'were': 'be',
  'being': 'be',
  'been': 'be',
  'have': 'have',
  'has': 'have',
  'had': 'have',
  'having': 'have',
  'do': 'do',
  'does': 'do',
  'did': 'do',
  'doing': 'do',
  'done': 'do',
  'will': 'will',
  'would': 'will',
  'shall': 'will',
  'should': 'will',
  'may': 'may',
  'might': 'may',
  'can': 'can',
  'could': 'can',
  'must': 'must',
  'ought': 'ought',
  'went': 'go',
  'gone': 'go',
  'going': 'go',
  'goes': 'go',
  'came': 'come',
  'coming': 'come',
  'comes': 'come',
  'saw': 'see',
  'seen': 'see',
  'seeing': 'see',
  'sees': 'see',
  'took': 'take',
  'taken': 'take',
  'taking': 'take',
  'takes': 'take',
  'got': 'get',
  'gotten': 'get',
  'getting': 'get',
  'gets': 'get',
  'made': 'make',
  'making': 'make',
  'makes': 'make',
  'said': 'say',
  'saying': 'say',
  'says': 'say',
  'told': 'tell',
  'telling': 'tell',
  'tells': 'tell',
  'knew': 'know',
  'known': 'know',
  'knowing': 'know',
  'knows': 'know',
  'thought': 'think',
  'thinking': 'think',
  'thinks': 'think',
  'felt': 'feel',
  'feeling': 'feel',
  'feels': 'feel',
  'found': 'find',
  'finding': 'find',
  'finds': 'find',
  'gave': 'give',
  'given': 'give',
  'giving': 'give',
  'gives': 'give',
  'left': 'leave',
  'leaving': 'leave',
  'leaves': 'leave',
  'brought': 'bring',
  'bringing': 'bring',
  'brings': 'bring',
  'children': 'child',
  'feet': 'foot',
  'teeth': 'tooth',
  'geese': 'goose',
  'men': 'man',
  'women': 'woman',
  'mice': 'mouse',
  'oxen': 'ox'
};

export class TextNormalizer {
  private options: Required<NormalizationOptions>;

  constructor(options: NormalizationOptions = {}) {
    this.options = {
      enableStemming: true,
      enableLemmatization: false,
      normalizeWhitespace: true,
      normalizeCase: true,
      expandContractions: true,
      normalizeNumbers: false,
      removeAccents: true,
      ...options
    };
  }

  /**
   * Normalize a single text string
   */
  normalize(text: string): string {
    if (!text || typeof text !== 'string') {
      return '';
    }

    let normalized = text;

    // Normalize case
    if (this.options.normalizeCase) {
      normalized = normalized.toLowerCase();
    }

    // Remove accents
    if (this.options.removeAccents) {
      normalized = this.removeAccents(normalized);
    }

    // Expand contractions
    if (this.options.expandContractions) {
      normalized = this.expandContractions(normalized);
    }

    // Normalize numbers
    if (this.options.normalizeNumbers) {
      normalized = normalized.replace(/\d+/g, '<NUM>');
    }

    // Normalize whitespace
    if (this.options.normalizeWhitespace) {
      normalized = normalized.replace(/\s+/g, ' ').trim();
    }

    // Apply lemmatization
    if (this.options.enableLemmatization) {
      normalized = this.lemmatize(normalized);
    }

    // Apply stemming (if lemmatization is not enabled)
    if (this.options.enableStemming && !this.options.enableLemmatization) {
      normalized = this.stem(normalized);
    }

    return normalized;
  }

  /**
   * Normalize an array of texts
   */
  normalizeTexts(texts: string[]): string[] {
    return texts.map(text => this.normalize(text));
  }

  /**
   * Remove accents from text
   */
  private removeAccents(text: string): string {
    return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  /**
   * Expand contractions in text
   */
  private expandContractions(text: string): string {
    let expanded = text;
    
    // Sort by length (longest first) to avoid partial matches
    const sortedContractions = Object.keys(CONTRACTIONS_MAP)
      .sort((a, b) => b.length - a.length);

    for (const contraction of sortedContractions) {
      const pattern = new RegExp(`\\b${contraction}\\b`, 'gi');
      expanded = expanded.replace(pattern, CONTRACTIONS_MAP[contraction.toLowerCase()]);
    }

    return expanded;
  }

  /**
   * Apply lemmatization to text
   */
  private lemmatize(text: string): string {
    const words = text.split(/\s+/);
    const lemmatized = words.map(word => {
      const cleanWord = word.toLowerCase().replace(/[^\w]/g, '');
      return LEMMA_DICT[cleanWord] || word;
    });
    return lemmatized.join(' ');
  }

  /**
   * Apply stemming to text
   */
  private stem(text: string): string {
    const words = text.split(/\s+/);
    const stemmed = words.map(word => this.stemWord(word));
    return stemmed.join(' ');
  }

  /**
   * Stem a single word
   */
  private stemWord(word: string): string {
    if (word.length <= 2) return word;

    let stemmed = word.toLowerCase();
    
    for (const rule of STEMMING_RULES) {
      if (rule.pattern.test(stemmed)) {
        const newStem = stemmed.replace(rule.pattern, rule.replacement);
        // Only apply if the result is meaningful (not too short)
        if (newStem.length >= 2) {
          stemmed = newStem;
          break; // Apply only the first matching rule
        }
      }
    }

    return stemmed;
  }

  /**
   * Get normalization statistics
   */
  getNormalizationStats(originalText: string, normalizedText: string) {
    const originalWords = originalText.split(/\s+/).filter(w => w.length > 0);
    const normalizedWords = normalizedText.split(/\s+/).filter(w => w.length > 0);
    
    return {
      originalLength: originalText.length,
      normalizedLength: normalizedText.length,
      originalWordCount: originalWords.length,
      normalizedWordCount: normalizedWords.length,
      compressionRatio: normalizedText.length / originalText.length,
      uniqueWordsOriginal: new Set(originalWords).size,
      uniqueWordsNormalized: new Set(normalizedWords).size,
      vocabularyReduction: (new Set(originalWords).size - new Set(normalizedWords).size) / new Set(originalWords).size
    };
  }
}

// Export default instance
export const defaultNormalizer = new TextNormalizer();

// Export specialized normalizers
export const stemmingNormalizer = new TextNormalizer({
  enableStemming: true,
  enableLemmatization: false,
  normalizeWhitespace: true,
  normalizeCase: true,
  expandContractions: true,
  normalizeNumbers: false,
  removeAccents: true
});

export const lemmatizationNormalizer = new TextNormalizer({
  enableStemming: false,
  enableLemmatization: true,
  normalizeWhitespace: true,
  normalizeCase: true,
  expandContractions: true,
  normalizeNumbers: false,
  removeAccents: true
});

export const minimalNormalizer = new TextNormalizer({
  enableStemming: false,
  enableLemmatization: false,
  normalizeWhitespace: true,
  normalizeCase: true,
  expandContractions: false,
  normalizeNumbers: false,
  removeAccents: false
});
