#!/usr/bin/env python3
"""
AI Narrative Nexus - Machine Learning Model Training
Train sentiment analysis models using preprocessed data
"""

import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import argparse
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
import joblib
import time

class ModelTrainer:
    """
    Train and evaluate machine learning models for sentiment analysis
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize model trainer
        
        Args:
            data_dir: Directory containing preprocessed data
        """
        self.data_dir = Path(data_dir)
        self.models = {}
        
    def load_dataset(self, dataset_name: str):
        """
        Load preprocessed dataset
        
        Args:
            dataset_name: Name of dataset ('alexa', 'twitter', etc.)
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        print(f"Loading {dataset_name} dataset...")
        
        X_train = np.load(self.data_dir / f"{dataset_name}_X_train.npy")
        X_test = np.load(self.data_dir / f"{dataset_name}_X_test.npy")
        y_train = np.load(self.data_dir / f"{dataset_name}_y_train.npy")
        y_test = np.load(self.data_dir / f"{dataset_name}_y_test.npy")
        
        print(f"Dataset loaded:")
        print(f"  Training samples: {X_train.shape[0]}")
        print(f"  Test samples: {X_test.shape[0]}")
        print(f"  Features: {X_train.shape[1]}")
        print(f"  Label distribution (train): {np.bincount(y_train)}")
        print(f"  Label distribution (test): {np.bincount(y_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def train_models(self, X_train, y_train):
        """
        Train multiple machine learning models
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print("\nTraining machine learning models...")
        
        # Define models to train
        models_to_train = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Naive Bayes': MultinomialNB(),
            'SVM': SVC(kernel='linear', random_state=42, probability=True)
        }
        
        trained_models = {}
        
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...")
            start_time = time.time()
            
            # Train model
            model.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            print(f"  Training time: {training_time:.2f} seconds")
            print(f"  CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            
            trained_models[name] = {
                'model': model,
                'cv_scores': cv_scores,
                'training_time': training_time
            }
        
        self.models = trained_models
        return trained_models
    
    def evaluate_models(self, X_test, y_test):
        """
        Evaluate trained models on test set
        
        Args:
            X_test: Test features
            y_test: Test labels
        """
        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)
        
        results = {}
        
        for name, model_info in self.models.items():
            model = model_info['model']
            
            # Make predictions
            start_time = time.time()
            y_pred = model.predict(X_test)
            prediction_time = time.time() - start_time
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"\n{name}:")
            print(f"  Test Accuracy: {accuracy:.4f}")
            print(f"  Prediction time: {prediction_time:.4f} seconds")
            print(f"  CV Score: {model_info['cv_scores'].mean():.4f} ± {model_info['cv_scores'].std():.4f}")
            
            # Classification report
            print(f"\n  Classification Report:")
            report = classification_report(y_test, y_pred, output_dict=True)
            for label in ['0', '1']:
                if label in report:
                    precision = report[label]['precision']
                    recall = report[label]['recall']
                    f1 = report[label]['f1-score']
                    print(f"    Class {label}: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
            
            # Store results
            results[name] = {
                'accuracy': accuracy,
                'cv_mean': model_info['cv_scores'].mean(),
                'cv_std': model_info['cv_scores'].std(),
                'prediction_time': prediction_time,
                'training_time': model_info['training_time'],
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
        
        return results
    
    def save_best_model(self, results, dataset_name, output_dir):
        """
        Save the best performing model
        
        Args:
            results: Evaluation results
            dataset_name: Name of dataset
            output_dir: Output directory
        """
        # Find best model by accuracy
        best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
        best_model = self.models[best_model_name]['model']
        best_accuracy = results[best_model_name]['accuracy']
        
        print(f"\nBest model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
        
        # Save model
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        model_path = output_path / f"{dataset_name}_best_model.pkl"
        joblib.dump(best_model, model_path)
        
        # Save results summary
        results_path = output_path / f"{dataset_name}_model_results.json"
        import json
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Best model saved to: {model_path}")
        print(f"Results saved to: {results_path}")
        
        return best_model_name, best_model

def train_sentiment_models(dataset_name: str, data_dir: str, output_dir: str):
    """
    Complete training pipeline for a dataset
    
    Args:
        dataset_name: Name of dataset to train on
        data_dir: Directory containing preprocessed data
        output_dir: Directory to save trained models
    """
    print(f"Training sentiment analysis models for {dataset_name.upper()} dataset")
    print("="*60)
    
    # Initialize trainer
    trainer = ModelTrainer(data_dir)
    
    # Load data
    X_train, X_test, y_train, y_test = trainer.load_dataset(dataset_name)
    
    # Train models
    trained_models = trainer.train_models(X_train, y_train)
    
    # Evaluate models
    results = trainer.evaluate_models(X_test, y_test)
    
    # Save best model
    best_name, best_model = trainer.save_best_model(results, dataset_name, output_dir)
    
    print(f"\nTraining complete for {dataset_name} dataset!")
    
    return results, best_model

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train sentiment analysis models")
    parser.add_argument("--dataset", choices=["alexa", "twitter", "amazon_reviews"], 
                       required=True, help="Dataset to train on")
    parser.add_argument("--data-dir", default="./python_preprocessing/processed_data", 
                       help="Directory containing preprocessed data")
    parser.add_argument("--output-dir", default="./python_preprocessing/trained_models",
                       help="Directory to save trained models")
    
    args = parser.parse_args()
    
    print("AI Narrative Nexus - Machine Learning Model Training")
    print("="*60)
    
    # Check if data exists
    data_path = Path(args.data_dir)
    if not data_path.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        print("Please run the preprocessing pipeline first!")
        return
    
    # Train models
    try:
        results, best_model = train_sentiment_models(
            args.dataset, args.data_dir, args.output_dir
        )
        
        # Print summary
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        print(f"Dataset: {args.dataset.upper()}")
        print(f"Models trained: {len(results)}")
        
        # Show model comparison
        print("\nModel Performance Comparison:")
        for model_name, result in results.items():
            print(f"  {model_name:20s}: {result['accuracy']:.4f} accuracy")
        
        best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
        print(f"\nBest Model: {best_model_name}")
        print(f"Best Accuracy: {results[best_model_name]['accuracy']:.4f}")
        
        print(f"\nModels saved to: {args.output_dir}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
