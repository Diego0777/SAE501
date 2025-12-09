#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexer.py
---------
Construire un TF-IDF Ã  partir des fichiers nettoyÃ©s:
    ./data/cleaned/<Series>.txt

Sauve:
 - ./data/index/meta.joblib  (vectorizer + titles)
 - ./data/index/tfidf_matrix.joblib
"""
import argparse
import os
import glob
import joblib
import json
import logging
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk

# Télécharger les stopwords si nécessaire
try:
    stop_fr = set(stopwords.words('french'))
    stop_en = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    stop_fr = set(stopwords.words('french'))
    stop_en = set(stopwords.words('english'))

# Stopwords combinés + mots très communs à filtrer
STOPWORDS = stop_fr | stop_en | {'know', 'get', 'got', 'going', 'yeah', 'okay', 'right', 'just', 
                                  'like', 'want', 'think', 'look', 'see', 'come', 'go', 'say',
                                  'tell', 'make', 'take', 'let', 'need', 'thing', 'things',
                                  'est', 'sont', 'être', 'avoir', 'faire', 'dire', 'aller',
                                  'venir', 'voir', 'savoir', 'vouloir', 'pouvoir', 'quoi',
                                  'bien', 'peut', 'peut être', 'dois', 'faut', 'allez', 'vais'}

def main(args):
    # Traitement de TOUTES les séries (VF et VO séparées)
    files = sorted(glob.glob(os.path.join(args.input, '*.txt')))
    if not files:
        raise SystemExit(f"No cleaned files found in {args.input}")
    
    titles = [os.path.splitext(os.path.basename(f))[0] for f in files]
    docs = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            docs.append(fh.read())
    
    print(f"\n=== Traitement de {len(titles)} fichiers (séries VF et VO séparées) ===")
    print(f"Premières séries: {titles[:5]}...")
    print(f"Dernières séries: {titles[-5:]}...")
    print()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Stop words COMPLETS pour bien filtrer les mots génériques
    french_stop = {
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'car',
        'ni', 'ne', 'pas', 'plus', 'moins', 'tres', 'trop', 'bien', 'mal', 'tout', 'tous', 'toute', 'toutes',
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'mon', 'ton', 'son',
        'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'ce', 'cet', 'cette', 'ces',
        'qui', 'que', 'quoi', 'dont', 'ou', 'quand', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles',
        'suis', 'es', 'est', 'sommes', 'etes', 'sont', 'ai', 'as', 'avons', 'avez', 'ont',
        'ete', 'etais', 'etait', 'etions', 'etiez', 'etaient', 'avoir', 'etre', 'fait', 'faire',
        'dit', 'dire', 'va', 'vas', 'vais', 'allons', 'allez', 'vont', 'aller', 'peux', 'peut', 'pouvons',
        'pouvez', 'peuvent', 'pouvoir', 'veux', 'veut', 'voulons', 'voulez', 'veulent', 'vouloir',
        'dois', 'doit', 'devons', 'devez', 'doivent', 'devoir', 'sais', 'sait', 'savons', 'savez', 'savent',
        'pour', 'dans', 'sur', 'avec', 'sans', 'sous', 'par', 'chez', 'vers', 'avant', 'apres',
        'si', 'comme', 'aussi', 'alors', 'encore', 'deja', 'toujours', 'jamais', 'ici', 'la', 'voici', 'voila',
        'oui', 'non', 'peut', 'etre', 'rien', 'quelque', 'quelques', 'chaque', 'autre', 'autres', 'meme', 'memes',
        'tait', 'tre', 'chose', 'choses'
    }
    
    english_stop = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'would', 'should', 'could', 'might', 'must', 'can', 'will', 'shall',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
        'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
        'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
        'get', 'got', 'goes', 'going', 'gonna', 'gotta', 'know', 'like', 'yeah', 'well', 'hey', 'come',
        'want', 'wanna', 'need', 'think', 'okay', 'right', 'good', 'look', 'see', 'tell', 'make', 'take',
        'let', 'one', 'two', 'man', 'men', 'woman', 'women', 'time', 'times', 'sorry', 'help', 'people',
        'thing', 'things', 'guy', 'guys', 'yes', 'maybe', 'here', 'there', 'back', 'out', 'down', 'off'
    }
    
    all_stop_words = french_stop | english_stop
    print(f"Stopwords: {len(all_stop_words)} mots exclus")
    
    logging.info('Building TF-IDF vectorizer...')
    # min_df=1 pour capturer TOUS les mots, même rares (comme "dharma", "hatch", "crash", "avion", "ile")
    # Traiter VF et VO séparément pour avoir des stopwords adaptés
    vect = TfidfVectorizer(ngram_range=(1,2), max_features=50000, stop_words=None, min_df=1)
    X = vect.fit_transform(docs)
    os.makedirs(args.out, exist_ok=True)
    joblib.dump({'vectorizer': vect, 'titles': titles}, os.path.join(args.out, 'meta.joblib'))
    joblib.dump(X, os.path.join(args.out, 'tfidf_matrix.joblib'))
    logging.info('Saved TF-IDF matrix and meta into %s', args.out)

    # Optionnel: extraire mots-clés par série à partir de la matrice TF-IDF
    if args.extract_keywords:
        kw_out = args.keywords_out or os.path.join(os.path.dirname(args.out), 'keywords')
        os.makedirs(kw_out, exist_ok=True)
        logging.info('Extracting top %d keywords per series into %s', args.n_keywords, kw_out)
        feature_names = vect.get_feature_names_out()
        idf_values = vect.idf_
        all_keywords = {}
        
        # Calculer la matrice TF-IDF en numpy pour un accès plus rapide
        X_array = X.toarray()
        
        total_series = len(titles)
        for i, title in enumerate(titles):
            logging.info(f'[{i+1}/{total_series}] Extraction des mots-clés pour: {title}')
            
            # Détecter la langue (VF ou VO) depuis le nom du fichier
            is_vf = title.lower().endswith('_vf')
            is_vo = title.lower().endswith('_vo')
            
            # Choisir les stopwords appropriés
            if is_vf:
                current_stopwords = french_stop
                logging.info(f'  → Mode VF (stopwords français)')
            elif is_vo:
                current_stopwords = english_stop
                logging.info(f'  → Mode VO (stopwords anglais)')
            else:
                current_stopwords = all_stop_words
            
            try:
                vec = X_array[i]
                raw = docs[i]
                cand = []
                
                # Limite le nombre de features à traiter pour accélérer (ne garder que les meilleurs)
                max_features_to_process = 5000  # Réduit pour plus de vitesse
                non_zero_indices = np.nonzero(vec)[0]
                
                if len(non_zero_indices) > max_features_to_process:
                    # Trier par score TF-IDF et garder seulement les meilleurs
                    top_indices = non_zero_indices[np.argsort(vec[non_zero_indices])[-max_features_to_process:]]
                else:
                    top_indices = non_zero_indices
                
                logging.info(f'  → Traitement de {len(top_indices)} features pour "{title}"')
                
                for fid in top_indices:
                    tfidf_score = vec[fid]
                    if tfidf_score <= 0:
                        continue
                    term = feature_names[fid]
                    
                    # Filtrage : longueur minimum et pas de chiffres
                    if len(term) < 3 or re.search(r"\d", term):
                        continue
                    
                    # Ignorer les stopwords selon la langue
                    if term.lower() in current_stopwords:
                        continue
                    
                    # Compter les occurrences dans le texte brut (insensible à la casse)
                    try:
                        occ = len(re.findall(r"\b" + re.escape(term) + r"\b", raw, re.IGNORECASE))
                    except re.error:
                        occ = raw.lower().count(term.lower())
                    
                    # Seuil TRÈS BAS pour capturer même les mots rares mais pertinents (crash, avion, ile, plane, island...)
                    if occ < 2:
                        continue
                    
                    # SCORING OPTIMISÉ pour mots-clés SPÉCIFIQUES
                    idf = idf_values[fid]
                    
                    # Favoriser MASSIVEMENT les mots avec IDF élevé (spécifiques)
                    # IDF élevé = mot rare dans le corpus = spécifique à cette série
                    frequency_score = float(occ ** 0.8)  # Moins de poids sur la fréquence brute
                    specificity_score = idf ** 2.5  # ÉNORME poids sur la spécificité
                    
                    # Score final privilégiant la SPÉCIFICITÉ
                    final_score = specificity_score * frequency_score * tfidf_score
                    cand.append((term, final_score, occ, idf))
                
                # Trier par score final
                cand_sorted = sorted(cand, key=lambda x: x[1], reverse=True)
                topn = [(term, score) for term, score, _, _ in cand_sorted[:args.n_keywords]]
                
                if len(topn) == 0:
                    logging.warning(f'⚠ Aucun mot-clé extrait pour "{title}" - série ignorée')
                    continue
                    
                all_keywords[title] = topn
                # write per-series files
                safe_title = re.sub(r'[\\/:"*?<>|]+', '_', title)
                per_txt = os.path.join(kw_out, f"{safe_title}_keywords.txt")
                per_json = os.path.join(kw_out, f"{safe_title}_keywords.json")
                with open(per_txt, 'w', encoding='utf-8') as ftxt:
                    for term, sc in topn:
                        ftxt.write(f"{term}\t{sc:.6f}\n")
                with open(per_json, 'w', encoding='utf-8') as fj:
                    json.dump([{"keyword": t, "score": s} for t, s in topn], fj, ensure_ascii=False, indent=2)
                
                # Message de confirmation pour cette série
                logging.info(f'✓ Fichiers de mots-clés créés pour "{title}" ({len(topn)} mots-clés)')
            
            except Exception as e:
                logging.error(f'✗ ERREUR lors du traitement de "{title}": {e}')
                logging.info(f'  → Passage à la série suivante...')
                continue

        # save combined keywords.json and joblib metadata
        combined_json = os.path.join(kw_out, 'keywords.json')
        with open(combined_json, 'w', encoding='utf-8') as cj:
            json.dump({t: [{"keyword": k, "score": s} for k, s in ks] for t, ks in all_keywords.items()}, cj, ensure_ascii=False, indent=2)
        joblib.dump({'titles': titles, 'keywords': all_keywords}, os.path.join(kw_out, 'keywords_meta.joblib'))
        logging.info('Saved keywords outputs to %s', kw_out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build TF-IDF index from cleaned series texts.')
    parser.add_argument('--input', default='./data/cleaned', help='Directory with cleaned per-series txt files')
    parser.add_argument('--out', default='./data/index', help='Output directory to save index and models')
    parser.add_argument('--extract_keywords', action='store_true', help='Also extract top keywords per series and save them')
    parser.add_argument('--keywords_out', default=None, help='Directory to save keywords (defaults to ../keywords)')
    parser.add_argument('--n_keywords', type=int, default=200, help='Number of keywords to extract per series')
    args = parser.parse_args()
    
    # Force l'extraction de keywords
    args.extract_keywords = True
    print(f"\n{'='*60}")
    print(f"Extraction de {args.n_keywords} mots-clés par série (VF et VO séparés)")
    print(f"{'='*60}\n")
    
    main(args)