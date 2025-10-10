import os
import pickle
import numpy as np
from gensim.models import LdaModel, CoherenceModel
from gensim import corpora
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

def main():
    # ========== CONFIG ==========
    MODEL_DIR = "models"
    DICT_PATH = os.path.join(MODEL_DIR, "dictionary.dict")
    LDA_PATH = os.path.join(MODEL_DIR, "lda.model")
    CORPUS_PATH = os.path.join(MODEL_DIR, "corpus.mm")
    TEXTS_PATH = os.path.join(MODEL_DIR, "texts.pkl")
    COHERENCE_PATH = os.path.join(MODEL_DIR, "coherence_scores.pkl")
    RESULTS_PATH = os.path.join(MODEL_DIR, "evaluation_results.txt")
    # ============================

    print("📂 Loading model components...")
    
    # ---- Load Dictionary and Model ----
    try:
        dictionary = corpora.Dictionary.load(DICT_PATH)
        lda_model = LdaModel.load(LDA_PATH)
        print(f"✅ Model loaded: {lda_model.num_topics} topics, {len(dictionary)} vocabulary")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # ---- Load Corpus ----
    corpus = None
    if os.path.exists(CORPUS_PATH):
        try:
            corpus = corpora.MmCorpus(CORPUS_PATH)
            print(f"✅ Corpus loaded: {len(corpus):,} documents")
        except Exception as e:
            print(f"⚠️ Error loading corpus: {e}")
    else:
        print("⚠️ corpus.mm not found. Perplexity evaluation will be skipped.")

    # ---- Load Sample Texts ----
    texts = None
    if os.path.exists(TEXTS_PATH):
        try:
            with open(TEXTS_PATH, "rb") as f:
                texts = pickle.load(f)
            print(f"✅ Sample texts loaded: {len(texts):,} documents")
        except Exception as e:
            print(f"⚠️ Error loading texts: {e}")
    else:
        print("⚠️ texts.pkl not found. Coherence evaluation will be skipped.")

    print("\n" + "="*60)
    print("📊 COMPREHENSIVE LDA MODEL EVALUATION")
    print("="*60)

    results = []
    results.append(f"Model: {lda_model.num_topics} topics, {len(dictionary)} vocabulary")
    results.append(f"Corpus: {len(corpus) if corpus else 'N/A'} documents")
    results.append("-" * 50)

    # ---- Evaluate Perplexity ----
    if corpus:
        try:
            print("📉 Calculating perplexity...")
            perplexity = lda_model.log_perplexity(corpus)
            print(f"📉 Model Perplexity: {perplexity:.4f}")
            results.append(f"Perplexity: {perplexity:.4f}")
            
            # Perplexity quality assessment
            if perplexity > -7:
                quality = "Excellent"
            elif perplexity > -8:
                quality = "Good"
            elif perplexity > -9:
                quality = "Fair"
            else:
                quality = "Poor"
            
            print(f"  └─ Quality: {quality}")
            results.append(f"Perplexity Quality: {quality}")
            
        except Exception as e:
            print(f"❌ Error calculating perplexity: {e}")

    # ---- Evaluate Coherence ----
    if texts:
        print("\n🔍 Calculating coherence scores...")
        
        try:
            # C_V coherence (most reliable)
            coherence_cv = CoherenceModel(
                model=lda_model, 
                texts=texts[:5000],  # Use subset for faster computation
                dictionary=dictionary, 
                coherence="c_v"
            )
            cv_score = coherence_cv.get_coherence()
            print(f"🔍 Coherence (c_v): {cv_score:.4f}")
            results.append(f"Coherence (c_v): {cv_score:.4f}")
            
            # C_V quality assessment
            if cv_score > 0.6:
                cv_quality = "Excellent"
            elif cv_score > 0.5:
                cv_quality = "Very Good"
            elif cv_score > 0.4:
                cv_quality = "Good"
            elif cv_score > 0.3:
                cv_quality = "Fair"
            else:
                cv_quality = "Poor"
                
            print(f"  └─ C_V Quality: {cv_quality}")
            results.append(f"C_V Quality: {cv_quality}")
            
        except Exception as e:
            print(f"❌ Error calculating c_v coherence: {e}")
            cv_score = None

        try:
            # U_Mass coherence
            if corpus:
                coherence_umass = CoherenceModel(
                    model=lda_model, 
                    corpus=corpus, 
                    dictionary=dictionary, 
                    coherence="u_mass"
                )
                umass_score = coherence_umass.get_coherence()
                print(f"📊 Coherence (u_mass): {umass_score:.4f}")
                results.append(f"Coherence (u_mass): {umass_score:.4f}")
                
                # U_Mass quality (higher is better, but typically negative)
                if umass_score > -1:
                    umass_quality = "Excellent"
                elif umass_score > -2:
                    umass_quality = "Good"
                elif umass_score > -3:
                    umass_quality = "Fair"
                else:
                    umass_quality = "Poor"
                    
                print(f"  └─ U_Mass Quality: {umass_quality}")
                results.append(f"U_Mass Quality: {umass_quality}")
                
        except Exception as e:
            print(f"❌ Error calculating u_mass coherence: {e}")

        try:
            # NPMI coherence
            coherence_npmi = CoherenceModel(
                model=lda_model, 
                texts=texts[:3000], 
                dictionary=dictionary, 
                coherence="c_npmi"
            )
            npmi_score = coherence_npmi.get_coherence()
            print(f"🎯 Coherence (c_npmi): {npmi_score:.4f}")
            results.append(f"Coherence (c_npmi): {npmi_score:.4f}")
            
        except Exception as e:
            print(f"❌ Error calculating npmi coherence: {e}")

    # ---- Topic Analysis ----
    print(f"\n🏷️ TOPIC ANALYSIS ({lda_model.num_topics} topics)")
    print("-" * 40)
    results.append("\nTOPIC ANALYSIS:")
    
    topic_qualities = []
    all_topic_words = []
    
    for idx in range(lda_model.num_topics):
        topic_words = lda_model.show_topic(idx, topn=10, formatted=False)
        words = [w for w, _ in topic_words]
        probs = [p for _, p in topic_words]
        
        print(f"\n🏷️ Topic {idx}:")
        print(f"   Words: {', '.join(words[:5])}")
        print(f"   Top prob: {probs[0]:.3f}")
        
        results.append(f"Topic {idx}: {', '.join(words[:5])}")
        
        # Assess topic quality
        prob_std = np.std(probs)
        if prob_std > 0.01 and probs[0] > 0.05:
            quality = "Good"
        elif prob_std > 0.005 and probs[0] > 0.03:
            quality = "Fair"
        else:
            quality = "Poor"
            
        topic_qualities.append(quality)
        all_topic_words.extend(words)
        print(f"   Quality: {quality}")

    # ---- Topic Diversity Analysis ----
    print(f"\n🎲 TOPIC DIVERSITY ANALYSIS")
    print("-" * 30)
    
    # Calculate topic word overlap
    topic_word_sets = []
    for idx in range(lda_model.num_topics):
        topic_words = [w for w, _ in lda_model.show_topic(idx, topn=10)]
        topic_word_sets.append(set(topic_words))
    
    # Calculate pairwise Jaccard distances
    jaccard_distances = []
    for i in range(len(topic_word_sets)):
        for j in range(i+1, len(topic_word_sets)):
            intersection = len(topic_word_sets[i] & topic_word_sets[j])
            union = len(topic_word_sets[i] | topic_word_sets[j])
            jaccard_sim = intersection / union if union > 0 else 0
            jaccard_dist = 1 - jaccard_sim
            jaccard_distances.append(jaccard_dist)
    
    avg_diversity = np.mean(jaccard_distances) if jaccard_distances else 0
    print(f"🎲 Average topic diversity: {avg_diversity:.4f}")
    results.append(f"Topic Diversity: {avg_diversity:.4f}")
    
    if avg_diversity > 0.8:
        diversity_quality = "Excellent"
    elif avg_diversity > 0.6:
        diversity_quality = "Good"
    elif avg_diversity > 0.4:
        diversity_quality = "Fair"
    else:
        diversity_quality = "Poor"
    
    print(f"   Quality: {diversity_quality}")
    results.append(f"Diversity Quality: {diversity_quality}")

    # ---- Word Frequency Analysis ----
    print(f"\n📈 VOCABULARY ANALYSIS")
    print("-" * 25)
    
    word_counter = Counter(all_topic_words)
    most_common = word_counter.most_common(10)
    
    print("🔤 Most frequent topic words:")
    for word, count in most_common:
        print(f"   {word}: {count} topics")
    
    results.append("\nMost frequent topic words:")
    for word, count in most_common[:5]:
        results.append(f"  {word}: {count} topics")

    # ---- Overall Quality Assessment ----
    print(f"\n🏆 OVERALL QUALITY ASSESSMENT")
    print("=" * 35)
    
    quality_scores = []
    
    # Collect quality indicators
    good_topics = topic_qualities.count("Good")
    fair_topics = topic_qualities.count("Fair")
    poor_topics = topic_qualities.count("Poor")
    
    print(f"📊 Topic Quality Distribution:")
    print(f"   Good topics: {good_topics}")
    print(f"   Fair topics: {fair_topics}")
    print(f"   Poor topics: {poor_topics}")
    
    results.append(f"\nTopic Quality: {good_topics} good, {fair_topics} fair, {poor_topics} poor")
    
    # Overall recommendation
    if good_topics >= lda_model.num_topics * 0.7:
        overall_quality = "Excellent"
        recommendation = "✅ Model is ready for production use!"
    elif good_topics >= lda_model.num_topics * 0.5:
        overall_quality = "Good"
        recommendation = "✅ Model is suitable for most applications"
    elif good_topics >= lda_model.num_topics * 0.3:
        overall_quality = "Fair"
        recommendation = "⚠️ Consider retraining with different parameters"
    else:
        overall_quality = "Poor"
        recommendation = "❌ Recommend retraining with better preprocessing"
    
    print(f"\n🎯 Overall Quality: {overall_quality}")
    print(f"💡 Recommendation: {recommendation}")
    
    results.append(f"Overall Quality: {overall_quality}")
    results.append(f"Recommendation: {recommendation}")

    # ---- Save Results ----
    print(f"\n💾 Saving evaluation results to {RESULTS_PATH}")
    
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        f.write("LDA MODEL EVALUATION RESULTS\n")
        f.write("=" * 40 + "\n\n")
        for result in results:
            f.write(result + "\n")
    
    print("✅ Evaluation completed!")

    # ---- Load and display coherence optimization history ----
    if os.path.exists(COHERENCE_PATH):
        try:
            print(f"\n📈 COHERENCE OPTIMIZATION HISTORY")
            print("-" * 35)
            
            with open(COHERENCE_PATH, 'rb') as f:
                coherence_data = pickle.load(f)
            
            topic_nums = coherence_data['topic_nums']
            coherence_scores = coherence_data['coherence_scores']
            best_topics = coherence_data['best_topics']
            
            print("Topic count -> Coherence score:")
            for topics, score in zip(topic_nums, coherence_scores):
                marker = " ⭐" if topics == best_topics else ""
                print(f"  {topics:2d} topics: {score:.4f}{marker}")
            
            print(f"\n🎯 Optimal configuration: {best_topics} topics")
            
        except Exception as e:
            print(f"⚠️ Could not load coherence history: {e}")

    print("\n" + "="*60)
    print("🎉 EVALUATION COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()