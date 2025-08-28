/**
 * Text Cleaning Utilities for AI Narrative Nexus
 * Implements comprehensive text preprocessing as per project methodology
 */

export interface CleaningOptions {
  removeSpecialChars?: boolean;
  removePunctuation?: boolean;
  removeNumbers?: boolean;
  removeStopWords?: boolean;
  convertToLowercase?: boolean;
  removeExtraWhitespace?: boolean;
  removeUrls?: boolean;
  removeEmails?: boolean;
  removeHtmlTags?: boolean;
  preserveEmoticons?: boolean;
}

// Common English stop words
const STOP_WORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
  'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
  'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
  'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
  'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
  'her', 'would', 'make', 'like', 'into', 'him', 'two', 'more', 'go',
  'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who',
  'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come',
  'made', 'may', 'part'
]);

// Emoticon patterns to preserve
const EMOTICON_PATTERNS = [
  /:\)/g, /:\(/g, /:D/g, /:P/g, /;\)/g, /:\|/g, /:o/g, /:O/g,
  /=\)/g, /=\(/g, /=D/g, /=P/g, /;\(/g, /8\)/g, /8\(/g,
  /<3/g, /<\/3/g, /:'\(/g, /:'\)/g
];

export class TextCleaner {
  private options: Required<CleaningOptions>;

  constructor(options: CleaningOptions = {}) {
    this.options = {
      removeSpecialChars: true,
      removePunctuation: true,
      removeNumbers: false,
      removeStopWords: true,
      convertToLowercase: true,
      removeExtraWhitespace: true,
      removeUrls: true,
      removeEmails: true,
      removeHtmlTags: true,
      preserveEmoticons: true,
      ...options
    };
  }

  /**
   * Clean a single text string
   */
  cleanText(text: string): string {
    if (!text || typeof text !== 'string') {
      return '';
    }

    let cleaned = text;

    // Preserve emoticons if required
    const preservedEmoticons: string[] = [];
    if (this.options.preserveEmoticons) {
      for (let index = 0; index < EMOTICON_PATTERNS.length; index++) {
        const pattern = EMOTICON_PATTERNS[index];
        const matches = cleaned.match(pattern);
        if (matches) {
          matches.forEach((match, matchIndex) => {
            const placeholder = `__EMOTICON_${index}_${matchIndex}__`;
            preservedEmoticons.push(match);
            cleaned = cleaned.replace(match, placeholder);
          });
        }
      }
    }

    // Remove HTML tags
    if (this.options.removeHtmlTags) {
      cleaned = cleaned.replace(/<[^>]*>/g, ' ');
    }

    // Remove URLs
    if (this.options.removeUrls) {
      cleaned = cleaned.replace(/https?:\/\/[^\s]+/g, ' ');
      cleaned = cleaned.replace(/www\.[^\s]+/g, ' ');
    }

    // Remove email addresses
    if (this.options.removeEmails) {
      cleaned = cleaned.replace(/[\w\.-]+@[\w\.-]+\.\w+/g, ' ');
    }

    // Convert to lowercase
    if (this.options.convertToLowercase) {
      cleaned = cleaned.toLowerCase();
    }

    // Remove numbers
    if (this.options.removeNumbers) {
      cleaned = cleaned.replace(/\d+/g, ' ');
    }

    // Remove special characters
    if (this.options.removeSpecialChars) {
      cleaned = cleaned.replace(/[^\w\s]/g, ' ');
    } else if (this.options.removePunctuation) {
      // Remove only punctuation but keep other special chars
      cleaned = cleaned.replace(/[.,;:!?'"()\[\]{}-]/g, ' ');
    }

    // Remove extra whitespace
    if (this.options.removeExtraWhitespace) {
      cleaned = cleaned.replace(/\s+/g, ' ').trim();
    }

    // Remove stop words
    if (this.options.removeStopWords) {
      const words = cleaned.split(' ');
      cleaned = words
        .filter(word => word.length > 0 && !STOP_WORDS.has(word))
        .join(' ');
    }

    // Restore emoticons
    if (this.options.preserveEmoticons && preservedEmoticons.length > 0) {
      let emoticonIndex = 0;
      EMOTICON_PATTERNS.forEach((pattern, patternIndex) => {
        const placeholderPattern = new RegExp(`__EMOTICON_${patternIndex}_\\d+__`, 'g');
        cleaned = cleaned.replace(placeholderPattern, () => {
          return preservedEmoticons[emoticonIndex++] || '';
        });
      });
    }

    return cleaned.trim();
  }

  /**
   * Clean an array of texts
   */
  cleanTexts(texts: string[]): string[] {
    return texts.map(text => this.cleanText(text));
  }

  /**
   * Clean text with custom options for this call only
   */
  cleanTextWithOptions(text: string, options: Partial<CleaningOptions>): string {
    const originalOptions = { ...this.options };
    this.options = { ...this.options, ...options };
    const result = this.cleanText(text);
    this.options = originalOptions;
    return result;
  }

  /**
   * Get statistics about the cleaning process
   */
  getCleaningStats(originalText: string, cleanedText: string) {
    return {
      originalLength: originalText.length,
      cleanedLength: cleanedText.length,
      originalWordCount: originalText.split(/\s+/).length,
      cleanedWordCount: cleanedText.split(/\s+/).filter(w => w.length > 0).length,
      compressionRatio: cleanedText.length / originalText.length,
      wordsRemoved: originalText.split(/\s+/).length - cleanedText.split(/\s+/).filter(w => w.length > 0).length
    };
  }

  /**
   * Validate if text needs cleaning
   */
  needsCleaning(text: string): boolean {
    if (!text) return false;

    const hasUrls = /https?:\/\/[^\s]+/.test(text);
    const hasHtml = /<[^>]*>/.test(text);
    const hasExtraSpaces = /\s{2,}/.test(text);
    const hasSpecialChars = /[^\w\s]/.test(text) && this.options.removeSpecialChars;
    
    return hasUrls || hasHtml || hasExtraSpaces || hasSpecialChars;
  }
}

// Export default instance with standard options
export const defaultTextCleaner = new TextCleaner();

// Export specialized cleaners for different use cases
export const strictTextCleaner = new TextCleaner({
  removeSpecialChars: true,
  removePunctuation: true,
  removeNumbers: true,
  removeStopWords: true,
  convertToLowercase: true,
  removeExtraWhitespace: true,
  removeUrls: true,
  removeEmails: true,
  removeHtmlTags: true,
  preserveEmoticons: false
});

export const socialMediaCleaner = new TextCleaner({
  removeSpecialChars: false,
  removePunctuation: false,
  removeNumbers: false,
  removeStopWords: false,
  convertToLowercase: true,
  removeExtraWhitespace: true,
  removeUrls: true,
  removeEmails: true,
  removeHtmlTags: true,
  preserveEmoticons: true
});
