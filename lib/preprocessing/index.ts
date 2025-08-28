/**
 * Data Preprocessing Module for AI Narrative Nexus
 * Comprehensive text preprocessing pipeline for text analysis
 */

// Export text cleaning utilities
export {
  TextCleaner,
  defaultTextCleaner,
  strictTextCleaner,
  socialMediaCleaner
} from './text-cleaner';

export type { CleaningOptions } from './text-cleaner';

// Export text normalization utilities
export {
  TextNormalizer,
  defaultNormalizer,
  stemmingNormalizer,
  lemmatizationNormalizer,
  minimalNormalizer
} from './normalizer';

export type { NormalizationOptions } from './normalizer';

// Export tokenization utilities
export {
  Tokenizer,
  defaultTokenizer,
  wordTokenizer,
  sentenceTokenizer,
  strictTokenizer
} from './tokenizer';

export type { TokenizationOptions, TokenMetrics } from './tokenizer';

// Export main preprocessing pipeline
export {
  DataPreprocessor,
  DATASET_CONFIGS,
  defaultPreprocessor
} from './data-preprocessor';

export type {
  DatasetConfig,
  PreprocessingConfig,
  ProcessedDataPoint,
  ProcessingStats
} from './data-preprocessor';

// Import for use in convenience functions
import { defaultTextCleaner } from './text-cleaner';
import { defaultNormalizer } from './normalizer';
import { defaultTokenizer } from './tokenizer';

// Convenience function for quick preprocessing
export async function quickPreprocess(
  text: string,
  options?: {
    clean?: boolean;
    normalize?: boolean;
    tokenize?: boolean;
  }
) {
  const { clean = true, normalize = true, tokenize = true } = options || {};
  
  let result = text;
  
  if (clean) {
    result = defaultTextCleaner.cleanText(result);
  }
  
  if (normalize) {
    result = defaultNormalizer.normalize(result);
  }
  
  const tokens = tokenize ? defaultTokenizer.tokenize(result) : [];
  
  return {
    originalText: text,
    cleanedText: clean ? result : text,
    normalizedText: normalize ? result : (clean ? result : text),
    tokens
  };
}

// Convenience function for batch preprocessing
export async function batchPreprocess(
  texts: string[],
  options?: {
    clean?: boolean;
    normalize?: boolean;
    tokenize?: boolean;
  }
) {
  return Promise.all(texts.map(text => quickPreprocess(text, options)));
}
