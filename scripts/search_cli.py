#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_cli.py
--------------
Recherche par mots-clÃ©s via TF-IDF + cosine similarity.
Usage:
    python3 search_cli.py "mot1 mot2" --top 10
"""
import sys
import os
import argparse
import joblib
from sklearn.metrics.pairwise import cosine_similarity

def search(query, model_dir='./data/index', topn=10, keyword_boost=True):
    meta = joblib.load(os.path.join(model_dir,'meta.joblib'))
    X = joblib.load(os.path.join(model_dir,'tfidf_matrix.joblib'))
    vect = meta['vectorizer']
    titles = meta['titles']
    
    # Recherche TF-IDF standard
    q_vec = vect.transform([query])
    sims = cosine_similarity(q_vec, X).flatten()
    
    # Si keywords disponibles, appliquer un boost
    if keyword_boost:
        kw_dir = os.path.join(os.path.dirname(model_dir), 'keywords')
        kw_meta_path = os.path.join(kw_dir, 'keywords_meta.joblib')
        
        if os.path.exists(kw_meta_path):
            kw_data = joblib.load(kw_meta_path)
            keywords_dict = kw_data.get('keywords', {})
            
            # Tokeniser la requête
            query_lower = query.lower()
            query_tokens = set(query_lower.split())
            
            # Pour chaque série, calculer un boost basé sur les mots-clés
            for i, title in enumerate(titles):
                if title in keywords_dict:
                    kw_list = keywords_dict[title]
                    boost = 0.0
                    
                    for keyword, kw_score in kw_list:
                        keyword_lower = keyword.lower()
                        # Boost si le mot-clé apparaît dans la requête
                        if keyword_lower in query_lower:
                            boost += kw_score * 0.5  # facteur de boost ajustable
                        # Boost partiel pour les mots individuels
                        for qt in query_tokens:
                            if len(qt) > 2 and qt in keyword_lower:
                                boost += kw_score * 0.2
                    
                    # Appliquer le boost au score de similarité
                    sims[i] = sims[i] + boost
    
    ranked_idx = sims.argsort()[::-1][:topn]
    return [(titles[i], float(sims[i])) for i in ranked_idx if sims[i] > 0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search series by keywords.')
    parser.add_argument('query', nargs='+', help='Search query (one or more keywords)')
    parser.add_argument('--model_dir', default='./data/index', help='Index directory')
    parser.add_argument('--top', type=int, default=10, help='Number of results')
    args = parser.parse_args()
    q = ' '.join(args.query)
    try:
        results = search(q, model_dir=args.model_dir, topn=args.top)
    except Exception as e:
        print('Error:', e)
        sys.exit(1)
    if not results:
        print('No matching series found.')
    else:
        for title,score in results:
            print(f"{title}\t{score:.4f}")