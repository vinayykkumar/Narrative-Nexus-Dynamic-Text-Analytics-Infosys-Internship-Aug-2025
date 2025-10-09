import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, roc_auc_score


def evaluate_model():
    print("--- Starting Model Evaluation ---")

    try:
        print("Loading model, vectorizer, and test data...")
        model = joblib.load('sentiment_model.joblib')
        vectorizer = joblib.load('tfidf_vectorizer.joblib')
        test_df = pd.read_csv('test_data.csv')
        test_df.dropna(subset=['clean_text'], inplace=True)
        print("Assets loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error: A required file was not found: {e.filename}")
        print("Please run the 'train_model.py' script first to generate the necessary files.")
        return

    X_test = test_df['clean_text']
    y_test = test_df['sentiment']

    print("Making predictions on the test set...")
    X_test_tfidf = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_tfidf)
    y_pred_proba = model.predict_proba(X_test_tfidf)[:, 1]
    print("Predictions complete.")

    print("Generating and saving evaluation metrics...")

    report = classification_report(y_test, y_pred, target_names=['Negative', 'Positive'], output_dict=True)
    report['accuracy'] = accuracy_score(y_test, y_pred)

    with open('model_evaluation.json', 'w') as f:
        json.dump(report, f, indent=4)
    print("    - Classification report saved to 'model_evaluation.json'")

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'])
    plt.title('Confusion Matrix', fontsize=16)
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.savefig('confusion_matrix.png')
    plt.close()
    print("    - Confusion matrix plot saved to 'confusion_matrix.png'")

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    auc = roc_auc_score(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=16)
    plt.legend(loc="lower right")
    plt.savefig('roc_curve.png')
    plt.close()
    print("    - ROC curve plot saved to 'roc_curve.png'")

    print("\n--- Evaluation Complete. All reports and plots have been saved. ---")


if __name__ == '__main__':
    evaluate_model()

