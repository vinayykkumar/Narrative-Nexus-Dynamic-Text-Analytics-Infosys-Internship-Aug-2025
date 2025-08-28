/**
 * Data Preprocessing Pipeline for AI Narrative Nexus
 * Handles data loading, cleaning, normalization, and tokenization
 */

import { TextCleaner, CleaningOptions } from './text-cleaner';
import { TextNormalizer, NormalizationOptions } from './normalizer';
import { Tokenizer, TokenizationOptions, TokenMetrics } from './tokenizer';
import * as fs from 'fs';
import * as path from 'path';

export interface DatasetConfig {
  name: string;
  filePath: string;
  format: 'csv' | 'tsv' | 'json';
  textColumn: string;
  labelColumn?: string;
  delimiter?: string;
  hasHeader?: boolean;
  encoding?: string;
}

export interface PreprocessingConfig {
  cleaning?: CleaningOptions;
  normalization?: NormalizationOptions;
  tokenization?: TokenizationOptions;
  outputPath?: string;
  saveIntermediate?: boolean;
  batchSize?: number;
}

export interface ProcessedDataPoint {
  id: string;
  originalText: string;
  cleanedText: string;
  normalizedText: string;
  tokens: string[];
  label?: string;
  metadata?: Record<string, any>;
}

export interface ProcessingStats {
  totalRecords: number;
  processedRecords: number;
  errorRecords: number;
  averageTextLength: number;
  averageTokenCount: number;
  tokenMetrics: TokenMetrics;
  processingTime: number;
  memoryUsage: number;
}

export class DataPreprocessor {
  private cleaner: TextCleaner;
  private normalizer: TextNormalizer;
  private tokenizer: Tokenizer;
  private config: PreprocessingConfig;

  constructor(config: PreprocessingConfig = {}) {
    this.config = {
      batchSize: 1000,
      saveIntermediate: false,
      ...config
    };

    this.cleaner = new TextCleaner(this.config.cleaning);
    this.normalizer = new TextNormalizer(this.config.normalization);
    this.tokenizer = new Tokenizer(this.config.tokenization);
  }

  /**
   * Load dataset from file
   */
  async loadDataset(datasetConfig: DatasetConfig): Promise<any[]> {
    const { filePath, format, delimiter = ',', hasHeader = true, encoding = 'utf-8' } = datasetConfig;
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Dataset file not found: ${filePath}`);
    }

    const content = fs.readFileSync(filePath, { encoding: encoding as BufferEncoding });
    const lines = content.split('\n').filter(line => line.trim().length > 0);
    
    let data: any[] = [];
    let headers: string[] = [];

    if (format === 'csv' || format === 'tsv') {
      const actualDelimiter = format === 'tsv' ? '\t' : delimiter;
      
      if (hasHeader && lines.length > 0) {
        headers = this.parseCsvLine(lines[0], actualDelimiter);
        lines.shift();
      }

      data = lines.map((line, index) => {
        const values = this.parseCsvLine(line, actualDelimiter);
        const record: any = { id: `${datasetConfig.name}_${index}` };
        
        if (headers.length > 0) {
          headers.forEach((header, i) => {
            record[header] = values[i] || '';
          });
        } else {
          values.forEach((value, i) => {
            record[`column_${i}`] = value;
          });
        }
        
        return record;
      });
    } else if (format === 'json') {
      try {
        const jsonData = JSON.parse(content);
        data = Array.isArray(jsonData) ? jsonData : [jsonData];
        data = data.map((item, index) => ({
          id: `${datasetConfig.name}_${index}`,
          ...item
        }));
      } catch (error) {
        throw new Error(`Invalid JSON format in file: ${filePath}`);
      }
    }

    return data;
  }

  /**
   * Process a single dataset
   */
  async processDataset(
    datasetConfig: DatasetConfig,
    progressCallback?: (progress: number, message: string) => void
  ): Promise<{ data: ProcessedDataPoint[], stats: ProcessingStats }> {
    const startTime = Date.now();
    const startMemory = process.memoryUsage().heapUsed;

    progressCallback?.(0, `Loading dataset: ${datasetConfig.name}`);
    
    const rawData = await this.loadDataset(datasetConfig);
    const totalRecords = rawData.length;
    
    progressCallback?.(10, `Loaded ${totalRecords} records`);

    const processedData: ProcessedDataPoint[] = [];
    let errorRecords = 0;
    const batchSize = this.config.batchSize || 1000;

    // Process data in batches
    for (let i = 0; i < rawData.length; i += batchSize) {
      const batch = rawData.slice(i, i + batchSize);
      const batchProgress = ((i + batch.length) / totalRecords) * 80; // 80% for processing
      
      progressCallback?.(10 + batchProgress, `Processing batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(totalRecords / batchSize)}`);

      for (const record of batch) {
        try {
          const processed = this.processRecord(record, datasetConfig);
          if (processed) {
            processedData.push(processed);
          }
        } catch (error) {
          console.error(`Error processing record ${record.id}:`, error);
          errorRecords++;
        }
      }

      // Save intermediate results if requested
      if (this.config.saveIntermediate && this.config.outputPath) {
        const intermediatePath = path.join(
          this.config.outputPath,
          `${datasetConfig.name}_batch_${Math.floor(i / batchSize)}.json`
        );
        fs.writeFileSync(intermediatePath, JSON.stringify(processedData.slice(i, i + batch.length), null, 2));
      }
    }

    progressCallback?.(90, 'Calculating statistics...');

    // Calculate statistics
    const stats = this.calculateStats(processedData, startTime, startMemory);
    stats.totalRecords = totalRecords;
    stats.errorRecords = errorRecords;

    progressCallback?.(100, 'Processing complete');

    return { data: processedData, stats };
  }

  /**
   * Process multiple datasets
   */
  async processMultipleDatasets(
    datasets: DatasetConfig[],
    progressCallback?: (progress: number, message: string) => void
  ): Promise<{ data: ProcessedDataPoint[], stats: ProcessingStats }> {
    const allData: ProcessedDataPoint[] = [];
    let totalStats: ProcessingStats = {
      totalRecords: 0,
      processedRecords: 0,
      errorRecords: 0,
      averageTextLength: 0,
      averageTokenCount: 0,
      tokenMetrics: {
        totalTokens: 0,
        uniqueTokens: 0,
        averageTokenLength: 0,
        tokenLengthDistribution: {},
        longestToken: '',
        shortestToken: '',
        vocabularyDiversity: 0
      },
      processingTime: 0,
      memoryUsage: 0
    };

    for (let i = 0; i < datasets.length; i++) {
      const dataset = datasets[i];
      const datasetProgress = (i / datasets.length) * 100;
      
      progressCallback?.(datasetProgress, `Processing dataset ${i + 1}/${datasets.length}: ${dataset.name}`);
      
      const result = await this.processDataset(dataset, (progress, message) => {
        const overallProgress = datasetProgress + (progress / datasets.length);
        progressCallback?.(overallProgress, `${dataset.name}: ${message}`);
      });

      allData.push(...result.data);
      this.mergeStats(totalStats, result.stats);
    }

    // Recalculate final statistics
    totalStats = this.calculateStats(allData, Date.now() - totalStats.processingTime, totalStats.memoryUsage);

    return { data: allData, stats: totalStats };
  }

  /**
   * Process a single record
   */
  private processRecord(record: any, config: DatasetConfig): ProcessedDataPoint | null {
    const textContent = record[config.textColumn];
    
    if (!textContent || typeof textContent !== 'string' || textContent.trim().length === 0) {
      return null;
    }

    // Step 1: Clean the text
    const cleanedText = this.cleaner.cleanText(textContent);
    
    // Step 2: Normalize the text
    const normalizedText = this.normalizer.normalize(cleanedText);
    
    // Step 3: Tokenize the text
    const tokens = this.tokenizer.tokenize(normalizedText);

    const processedRecord: ProcessedDataPoint = {
      id: record.id,
      originalText: textContent,
      cleanedText,
      normalizedText,
      tokens,
      label: config.labelColumn ? record[config.labelColumn] : undefined,
      metadata: {
        originalLength: textContent.length,
        cleanedLength: cleanedText.length,
        normalizedLength: normalizedText.length,
        tokenCount: tokens.length,
        ...Object.fromEntries(
          Object.entries(record).filter(([key]) => 
            key !== config.textColumn && key !== config.labelColumn && key !== 'id'
          )
        )
      }
    };

    return processedRecord;
  }

  /**
   * Parse CSV line with proper quote handling
   */
  private parseCsvLine(line: string, delimiter: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;
    let i = 0;

    while (i < line.length) {
      const char = line[i];
      const nextChar = line[i + 1];

      if (char === '"' && !inQuotes) {
        inQuotes = true;
      } else if (char === '"' && inQuotes) {
        if (nextChar === '"') {
          current += '"';
          i++; // Skip next quote
        } else {
          inQuotes = false;
        }
      } else if (char === delimiter && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
      i++;
    }

    result.push(current.trim());
    return result;
  }

  /**
   * Calculate processing statistics
   */
  private calculateStats(data: ProcessedDataPoint[], startTime: number, startMemory: number): ProcessingStats {
    const endTime = Date.now();
    const endMemory = process.memoryUsage().heapUsed;

    const totalTextLength = data.reduce((sum, item) => sum + item.originalText.length, 0);
    const totalTokenCount = data.reduce((sum, item) => sum + item.tokens.length, 0);
    
    // Calculate token metrics from all tokens
    const allTokens = data.flatMap(item => item.tokens);
    const tokenMetrics = this.tokenizer.getTokenMetrics(allTokens.join(' '));

    return {
      totalRecords: data.length,
      processedRecords: data.length,
      errorRecords: 0,
      averageTextLength: data.length > 0 ? totalTextLength / data.length : 0,
      averageTokenCount: data.length > 0 ? totalTokenCount / data.length : 0,
      tokenMetrics,
      processingTime: endTime - startTime,
      memoryUsage: endMemory - startMemory
    };
  }

  /**
   * Merge statistics from multiple processing runs
   */
  private mergeStats(totalStats: ProcessingStats, newStats: ProcessingStats): void {
    totalStats.totalRecords += newStats.totalRecords;
    totalStats.processedRecords += newStats.processedRecords;
    totalStats.errorRecords += newStats.errorRecords;
    totalStats.processingTime += newStats.processingTime;
    totalStats.memoryUsage += newStats.memoryUsage;
  }

  /**
   * Save processed data to file
   */
  async saveProcessedData(
    data: ProcessedDataPoint[],
    outputPath: string,
    format: 'json' | 'csv' = 'json'
  ): Promise<void> {
    if (!fs.existsSync(path.dirname(outputPath))) {
      fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    }

    if (format === 'json') {
      fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    } else if (format === 'csv') {
      const headers = ['id', 'originalText', 'cleanedText', 'normalizedText', 'tokens', 'label'];
      const csvLines = [headers.join(',')];
      
      for (const item of data) {
        const row = [
          item.id,
          `"${item.originalText.replace(/"/g, '""')}"`,
          `"${item.cleanedText.replace(/"/g, '""')}"`,
          `"${item.normalizedText.replace(/"/g, '""')}"`,
          `"${item.tokens.join(' ').replace(/"/g, '""')}"`,
          item.label || ''
        ];
        csvLines.push(row.join(','));
      }
      
      fs.writeFileSync(outputPath, csvLines.join('\n'));
    }
  }

  /**
   * Generate preprocessing report
   */
  generateReport(stats: ProcessingStats, outputPath?: string): string {
    const report = `
# Data Preprocessing Report

## Overview
- **Total Records**: ${stats.totalRecords.toLocaleString()}
- **Successfully Processed**: ${stats.processedRecords.toLocaleString()}
- **Errors**: ${stats.errorRecords.toLocaleString()}
- **Success Rate**: ${((stats.processedRecords / stats.totalRecords) * 100).toFixed(2)}%

## Text Analysis
- **Average Text Length**: ${stats.averageTextLength.toFixed(2)} characters
- **Average Token Count**: ${stats.averageTokenCount.toFixed(2)} tokens

## Token Metrics
- **Total Tokens**: ${stats.tokenMetrics.totalTokens.toLocaleString()}
- **Unique Tokens**: ${stats.tokenMetrics.uniqueTokens.toLocaleString()}
- **Vocabulary Diversity**: ${(stats.tokenMetrics.vocabularyDiversity * 100).toFixed(2)}%
- **Average Token Length**: ${stats.tokenMetrics.averageTokenLength.toFixed(2)} characters
- **Longest Token**: "${stats.tokenMetrics.longestToken}"
- **Shortest Token**: "${stats.tokenMetrics.shortestToken}"

## Performance
- **Processing Time**: ${(stats.processingTime / 1000).toFixed(2)} seconds
- **Memory Usage**: ${(stats.memoryUsage / (1024 * 1024)).toFixed(2)} MB
- **Processing Rate**: ${(stats.processedRecords / (stats.processingTime / 1000)).toFixed(2)} records/second

## Token Length Distribution
${Object.entries(stats.tokenMetrics.tokenLengthDistribution)
  .sort(([a], [b]) => parseInt(a) - parseInt(b))
  .map(([length, count]) => `- ${length} characters: ${count.toLocaleString()} tokens`)
  .join('\n')}

---
Generated on: ${new Date().toISOString()}
`;

    if (outputPath) {
      fs.writeFileSync(outputPath, report);
    }

    return report;
  }
}

// Export predefined dataset configurations for the project
export const DATASET_CONFIGS: Record<string, DatasetConfig> = {
  twitterSentiment: {
    name: 'twitter_sentiment',
    filePath: '/home/git/projects/Nexus/dataset/cleaned_tweets.csv',
    format: 'csv',
    textColumn: 'text',
    labelColumn: 'sentiment',
    hasHeader: true
  },
  
  amazonAlexa: {
    name: 'amazon_alexa',
    filePath: '/home/git/projects/Nexus/dataset/amazon_alexa.tsv',
    format: 'tsv',
    textColumn: 'verified_reviews',
    labelColumn: 'feedback',
    hasHeader: true
  },

  amazonReviews: {
    name: 'amazon_reviews',
    filePath: '/home/git/projects/Nexus/dataset/amazon_review_full_csv/train.csv',
    format: 'csv',
    textColumn: '2', // Third column (0-indexed) contains the review text
    labelColumn: '0', // First column contains the rating
    hasHeader: false,
    delimiter: ','
  }
};

// Export default preprocessor instance
export const defaultPreprocessor = new DataPreprocessor();
