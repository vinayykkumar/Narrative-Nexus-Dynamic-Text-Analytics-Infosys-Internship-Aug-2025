/**
 * Backend API Client for AI Narrative Nexus
 * Handles communication with the Python FastAPI backend
 */

interface PreprocessingOptions {
  remove_stopwords?: boolean;
  use_stemming?: boolean;
  use_lemmatization?: boolean;
  min_token_length?: number;
  max_token_length?: number;
}

interface PreprocessingStats {
  original_length: number;
  cleaned_length: number;
  normalized_length: number;
  token_count: number;
  vocabulary_size: number;
  avg_token_length: number;
  compression_ratio: number;
  processing_time: number;
  removed_urls?: number;
  removed_emails?: number;
  removed_mentions?: number;
  removed_hashtags?: number;
  removed_numbers?: number;
  removed_stopwords?: number;
}

interface PreprocessingResult {
  original_text: string;
  cleaned_text: string;
  normalized_text: string;
  tokens: string[];
  processed_text: string;
  stats: PreprocessingStats;
  processing_time: number;
}

interface BatchPreprocessingResult {
  results: PreprocessingResult[];
  summary: {
    batch_info?: {
      total_texts: number;
      total_processing_time: number;
      avg_processing_time_per_text: number;
      batch_size_used: number;
    };
    text_statistics?: {
      total_tokens: number;
      unique_tokens: number;
      vocabulary_diversity: number;
      avg_tokens_per_text: number;
      avg_token_length: number;
    };
    compression_statistics?: {
      overall_compression_ratio: number;
      cleaning_compression_ratio: number;
      normalization_compression_ratio: number;
    };
    removal_statistics?: {
      urls_removed: number;
      emails_removed: number;
      mentions_removed: number;
      hashtags_removed: number;
      numbers_removed: number;
      stopwords_removed: number;
    };
    top_tokens?: {
      most_common_10: [string, number][];
      most_common_50: [string, number][];
    };
  };
  total_processing_time: number;
}

interface BackendJob {
  job_id: string;
  status: 'started' | 'processing' | 'completed' | 'failed';
  progress: number;
  total: number;
  start_time: number;
  end_time?: number;
  total_time?: number;
  results_count?: number;
  error?: string;
}

class BackendAPIClient {
  private baseURL: string;
  private defaultOptions: PreprocessingOptions;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.defaultOptions = {
      remove_stopwords: true,
      use_stemming: true,
      use_lemmatization: false,
      min_token_length: 2,
      max_token_length: 50
    };
  }

  /**
   * Check if the backend is healthy and accessible
   */
  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Backend health check failed:', error);
      throw new Error('Backend is not accessible');
    }
  }

  /**
   * Preprocess a single text using the backend
   */
  async preprocessText(
    text: string, 
    options?: PreprocessingOptions
  ): Promise<PreprocessingResult> {
    try {
      const response = await fetch(`${this.baseURL}/preprocess/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          options: { ...this.defaultOptions, ...options }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Text preprocessing failed:', error);
      throw error;
    }
  }

  /**
   * Preprocess multiple texts in batch
   */
  async preprocessBatch(
    texts: string[], 
    options?: PreprocessingOptions
  ): Promise<BatchPreprocessingResult> {
    try {
      const response = await fetch(`${this.baseURL}/preprocess/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texts,
          options: { ...this.defaultOptions, ...options }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Batch preprocessing failed:', error);
      throw error;
    }
  }

  /**
   * Upload and preprocess a file
   */
  async preprocessFile(file: File): Promise<PreprocessingResult | BatchPreprocessingResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseURL}/preprocess/file`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `File upload failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('File preprocessing failed:', error);
      throw error;
    }
  }

  /**
   * Start a background processing job for large datasets
   */
  async startBackgroundJob(
    jobId: string, 
    texts: string[], 
    options?: PreprocessingOptions
  ): Promise<{ message: string; job_id: string }> {
    try {
      const response = await fetch(`${this.baseURL}/preprocess/job/${jobId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texts,
          options: { ...this.defaultOptions, ...options }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Job start failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Background job start failed:', error);
      throw error;
    }
  }

  /**
   * Get the status of a background job
   */
  async getJobStatus(jobId: string): Promise<BackendJob> {
    try {
      const response = await fetch(`${this.baseURL}/preprocess/job/${jobId}/status`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Job status check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Job status check failed:', error);
      throw error;
    }
  }

  /**
   * Get the results of a completed background job
   */
  async getJobResults(jobId: string): Promise<{ job_id: string; results: any[]; total_processing_time: number }> {
    try {
      const response = await fetch(`${this.baseURL}/preprocess/job/${jobId}/results`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Job results fetch failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Job results fetch failed:', error);
      throw error;
    }
  }

  /**
   * Poll a background job until completion
   */
  async pollJob(
    jobId: string, 
    onProgress?: (status: BackendJob) => void,
    pollInterval: number = 1000
  ): Promise<BackendJob> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getJobStatus(jobId);
          
          if (onProgress) {
            onProgress(status);
          }

          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.error || 'Job failed'));
          } else {
            setTimeout(poll, pollInterval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }

  /**
   * Update default preprocessing options
   */
  setDefaultOptions(options: PreprocessingOptions): void {
    this.defaultOptions = { ...this.defaultOptions, ...options };
  }

  /**
   * Get current default options
   */
  getDefaultOptions(): PreprocessingOptions {
    return { ...this.defaultOptions };
  }

  /**
   * Get backend information
   */
  async getBackendInfo(): Promise<any> {
    try {
      const response = await fetch(`${this.baseURL}/`);
      if (!response.ok) {
        throw new Error(`Backend info failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Backend info fetch failed:', error);
      throw error;
    }
  }
}

// Create and export a default instance
export const backendAPI = new BackendAPIClient();

// Export types and class for custom instances
export type {
  PreprocessingOptions,
  PreprocessingStats,
  PreprocessingResult,
  BatchPreprocessingResult,
  BackendJob
};

export { BackendAPIClient };
