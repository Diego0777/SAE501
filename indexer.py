#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexer.py
---------
Construire un TF-IDF à partir des fichiers nettoyés:
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
import time
from sklearn.feature_extraction.text import TfidfVectorizer


def main(args):
    t_global_start = time.time()
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
    
    
    # TIMING: Vectorisation
    t_start_vect = time.time()
    logging.info('Building TF-IDF vectorizer (stopwords déjà appliqués au preprocessing)...')
    # NOTE: Les stopwords ne sont PAS appliqués ici car ils ont déjà été filtrés
    # lors du preprocessing. Cela rend l'indexation BEAUCOUP plus rapide.
    vect = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=20000,
        stop_words=None,  # PAS de stopwords ici : déjà filtrés en preprocessing
        min_df=2,  # Augmenter min_df pour réduire la dimensionalité
        max_df=0.95,  # Exclure les mots trop courants
        lowercase=True,
        token_pattern=r'(?u)\b\w{3,}\b'  # Tokens de 3+ caractères seulement
    )
    X = vect.fit_transform(docs)
    t_vect = time.time() - t_start_vect
    print(f"⏱️  Vectorisation TF-IDF: {t_vect:.2f}s")
    
    os.makedirs(args.out, exist_ok=True)
    joblib.dump({'vectorizer': vect, 'titles': titles}, os.path.join(args.out, 'meta.joblib'))
    joblib.dump(X, os.path.join(args.out, 'tfidf_matrix.joblib'))
    logging.info('Saved TF-IDF matrix and meta into %s', args.out)

    # Optionnel: extraire mots-clés par série à partir de la matrice TF-IDF
    if args.extract_keywords:
        t_start_kw = time.time()
        kw_out = args.keywords_out or os.path.join(os.path.dirname(args.out), 'keywords')
        os.makedirs(kw_out, exist_ok=True)
        logging.info('Extracting top %d keywords per series into %s', args.n_keywords, kw_out)
        feature_names = vect.get_feature_names_out()
        idf_values = vect.idf_
        all_keywords = {}
        
        # Convertir en array dense pour accès plus rapide
        X_array = X.toarray()
        
        total_series = len(titles)
        
        t_prep = time.time() - t_start_kw
        print(f"⏱️  Préparation keywords: {t_prep:.2f}s")
        
        t_start_loop = time.time()
        
        # Boucle simple séquentielle avec scoring complet
        for i, title in enumerate(titles):
            vec_row = X_array[i]
            raw_lower = docs[i].lower()
            
            cand = []
            
            # Traiter les features avec TF-IDF > 0
            non_zero_indices = np.nonzero(vec_row)[0]
            
            for fid in non_zero_indices:
                tfidf_score = vec_row[fid]
                if tfidf_score <= 0:
                    continue
                
                term = feature_names[fid]
                
                # Filtrage : longueur minimum et pas de chiffres
                if len(term) < 3 or re.search(r"\d", term):
                    continue
                
                # Comptage
                term_lower = term.lower()
                occ = raw_lower.count(term_lower)
                
                if occ < 2:
                    continue
                
                # Scoring
                idf = idf_values[fid]
                frequency_score = float(occ ** 0.8)
                specificity_score = idf ** 2.5
                final_score = specificity_score * frequency_score * tfidf_score
                cand.append((term, final_score))
            
            # Trier et garder top N
            cand_sorted = sorted(cand, key=lambda x: x[1], reverse=True)
            topn = cand_sorted[:args.n_keywords]
            
            all_keywords[title] = topn
            
            # Afficher la progression tous les 10 éléments
            if (i + 1) % 10 == 0:
                logging.info(f'[{i+1}/{total_series}] Keywords extracted for: {title}')
            
            # Sauvegarder les fichiers de keywords
            if len(topn) > 0:
                safe_title = re.sub(r'[\\/:"*?<>|]+', '_', title)
                per_txt = os.path.join(kw_out, f"{safe_title}_keywords.txt")
                per_json = os.path.join(kw_out, f"{safe_title}_keywords.json")
                
                with open(per_txt, 'w', encoding='utf-8') as ftxt:
                    for term, sc in topn:
                        ftxt.write(f"{term}\t{sc:.6f}\n")
                
                with open(per_json, 'w', encoding='utf-8') as fj:
                    json.dump([{"keyword": t, "score": s} for t, s in topn], fj, ensure_ascii=False, indent=2)

        t_loop = time.time() - t_start_loop
        print(f"⏱️  Boucle extraction keywords: {t_loop:.2f}s")

        # save combined keywords.json and joblib metadata
        combined_json = os.path.join(kw_out, 'keywords.json')
        with open(combined_json, 'w', encoding='utf-8') as cj:
            json.dump({t: [{"keyword": k, "score": s} for k, s in ks] for t, ks in all_keywords.items()}, cj, ensure_ascii=False, indent=2)
        joblib.dump({'titles': titles, 'keywords': all_keywords}, os.path.join(kw_out, 'keywords_meta.joblib'))
        logging.info('Saved keywords outputs to %s', kw_out)
    
    t_global = time.time() - t_global_start
    print(f"\n{'='*60}")
    print(f"⏱️  TEMPS TOTAL: {t_global:.2f}s ({t_global/60:.1f} minutes)")
    print(f"{'='*60}")

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
