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
import time
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

def create_comprehensive_stopwords():
    """
    Crée un ensemble complet de stopwords français et anglais
    inspiré du vieux système qui fonctionnait très bien.
    """
    french_stop = {
        # Pronoms et articles
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'car',
        'ni', 'ne', 'pas', 'plus', 'moins', 'tres', 'trop', 'bien', 'mal', 'tout', 'tous', 'toute', 'toutes',
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'mon', 'ton', 'son',
        'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'ce', 'cet', 'cette', 'ces',
        'qui', 'que', 'quoi', 'dont', 'quand', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles',
        
        # Verbes courants
        'suis', 'es', 'est', 'sommes', 'etes', 'sont', 'ai', 'as', 'avons', 'avez', 'ont',
        'ete', 'etais', 'etait', 'etions', 'etiez', 'etaient', 'avoir', 'etre', 'fait', 'faire',
        'dit', 'dire', 'va', 'vas', 'vais', 'allons', 'allez', 'vont', 'aller', 'peux', 'peut', 'pouvons',
        'pouvez', 'peuvent', 'pouvoir', 'veux', 'veut', 'voulons', 'voulez', 'veulent', 'vouloir',
        'dois', 'doit', 'devons', 'devez', 'doivent', 'devoir', 'sais', 'sait', 'savons', 'savez', 'savent',
        'pour', 'dans', 'sur', 'avec', 'sans', 'sous', 'par', 'chez', 'vers', 'avant', 'apres',
        
        # Adverbes et conjonctions
        'si', 'comme', 'aussi', 'alors', 'encore', 'deja', 'toujours', 'jamais', 'ici', 'voici', 'voila',
        'oui', 'non', 'rien', 'quelque', 'quelques', 'chaque', 'autre', 'autres', 'meme', 'memes',
        'tait', 'tre', 'chose', 'choses', 'ah', 'oh', 'euh', 'hum', 'hein', 'ben', 'ok', 'okay', 'ouais', 'nan',
        'allez', 'allons', 'attends', 'attendez', 'regarde', 'regardez', 'ecoute', 'ecoutez',
        'tiens', 'tenez', 'viens', 'venez', 'voici', 'peu', 'beaucoup', 'assez',
        
        # MOTS TRONQU\u00c9S (apr\u00e8s suppression des accents et s\u00e9paration)
        'parce', 'quelqu', 'aujourd', 'peut', 'c', 'd', 'l', 's', 't',
        
        # MOTS COMMUNS TR\u00c8S FR\u00c9QUENTS (sans sp\u00e9cificit\u00e9)
        'voir', 'fais', 'passe', 'juste', 'vie', 'merci', 'vraiment', 'fois', 'soir',
        'pense', 'crois', 'semble', 'parait', 'comprends', 'trouve',
        'reste', 'part', 'vient', 'tient', 'sent', 'vois', 'sens',
        'attend', 'appelle', 'ouvre', 'ferme', 'commence', 'finit', 'continue',
        'moment', 'jour', 'nuit', 'matin', 'heure', 'temps', 'ans', 'annees',
        'personne', 'gens', 'monde', 'homme', 'femme', 'enfant', 'fille', 'garcon',
        'bon', 'mauvais', 'grand', 'petit', 'nouveau', 'ancien', 'premier', 'dernier',
        'hier', 'demain', 'tard', 'tot',
        'pourrait', 'faudrait', 'devrait', 'serait', 'irait',
        'vrai', 'faux', 'possible', 'impossible', 'certain',
        'pardon', 'excuse',
        'mieux', 'pire', 'meilleur',
        'seul', 'seule', 'seuls', 'seules', 'ensemble',
        'maintenant', 'ensuite', 'puis', 'pendant',
        'aller', 'venir', 'etre', 'avoir'
    }
    
    english_stop = {
        # Articles et prépositions
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'as', 'than', 'than', 'so', 'such',
        
        # Verbes courants
        'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'would', 'should', 'could', 'might', 'must', 'can', 'will', 'shall',
        'go', 'goes', 'going', 'come', 'comes', 'coming', 'get', 'gets', 'getting', 'make', 'makes', 'making',
        'take', 'takes', 'taking', 'see', 'sees', 'seeing', 'say', 'says', 'said', 'know', 'knows', 'knowing',
        'think', 'thinks', 'thinking', 'want', 'wants', 'wanting', 'need', 'needs', 'needing',
        'look', 'looks', 'looking', 'tell', 'tells', 'telling', 'ask', 'asks', 'asking',
        'let', 'lets', 'letting', 'give', 'gives', 'giving', 'find', 'finds', 'finding',
        'use', 'uses', 'using', 'work', 'works', 'working', 'call', 'calls', 'calling',
        'try', 'tries', 'trying', 'feel', 'feels', 'feeling', 'become', 'becomes', 'becoming',
        'leave', 'leaves', 'leaving', 'put', 'puts', 'putting', 'mean', 'means', 'meaning',
        
        # Pronoms
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours',
        'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
        
        # Questions et démonstratifs
        'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whose', 'whom',
        
        # Quantificateurs
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'any',
        'many', 'much', 'no', 'none', 'nothing', 'anybody', 'anybody', 'everybody',
        'nobody', 'somebody', 'anyone', 'someone', 'everyone', 'something', 'anything',
        'everything',
        
        # Adverbes courants
        'very', 'just', 'now', 'only', 'own', 'same', 'also', 'too', 'not', 'no', 'nor',
        'well', 'really', 'even', 'rather', 'quite', 'almost', 'ever', 'never', 'always',
        'sometimes', 'often', 'usually', 'probably', 'certainly', 'definitely', 'maybe', 'perhaps',
        'certainly', 'seriously', 'actually', 'basically', 'literally', 'simply', 'just',
        
        # Interjections et expressions courantes
        'yeah', 'hey', 'yes', 'okay', 'ok', 'right', 'sure', 'sorry', 'thank', 'thanks',
        'please', 'hello', 'hi', 'bye', 'goodbye', 'good', 'great', 'wow', 'oh', 'ah',
        'uh', 'er', 'um', 'mm', 'hmm', 'really', 'seriously', 'honestly', 'actually',
        
        # Mots tronqués / contractés
        'dont', 'cant', 'wont', 'doesnt', 'isnt', 'arent', 'wasnt', 'werent', 'havent',
        'hasnt', 'hadnt', 'didnt', 'shouldnt', 'wouldnt', 'couldnt', 'mustnt',
        's', 'd', 't', 're', 've', 'll', 'm',
        
        # Mots courants trop génériques
        'time', 'times', 'way', 'thing', 'things', 'place', 'day', 'night', 'morning',
        'evening', 'moment', 'second', 'minute', 'hour', 'week', 'year', 'month',
        'guy', 'guys', 'man', 'men', 'woman', 'women', 'person', 'people',
        'person', 'friend', 'friends', 'family', 'life', 'world', 'life', 'world',
        'right', 'left', 'good', 'bad', 'big', 'small', 'new', 'old', 'first', 'last',
        'next', 'last', 'same', 'different', 'same', 'different', 'like', 'unlike',
        'help', 'hand', 'idea', 'matter', 'reason', 'fact', 'kind', 'sort', 'type',
        'sense', 'point', 'part', 'piece', 'bit', 'lot', 'bunch', 'set', 'group',
        'look', 'sound', 'feel', 'seem', 'appear', 'show', 'turn', 'move', 'come',
        'back', 'down', 'up', 'out', 'in', 'here', 'there', 'around', 'along',
        'away', 'over', 'under', 'near', 'far', 'close', 'close', 'open', 'close'
    }
    
    return french_stop | english_stop

# Stopwords combinés et complets
STOPWORDS = create_comprehensive_stopwords()


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
    
    print(f"Stopwords: {len(STOPWORDS)} mots exclus")
    
    # TIMING: Vectorisation
    t_start_vect = time.time()
    logging.info('Building TF-IDF vectorizer with comprehensive stopwords...')
    # IMPORTANT: Appliquer les stopwords directement à la vectorisation
    # min_df=1 pour capturer TOUS les mots rares pertinents
    # Les stopwords sont maintenant appliqués à la vectorisation, pas seulement au preprocessing
    vect = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=20000,
        stop_words=list(STOPWORDS),  # Appliquer les stopwords complets
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
                
                # Stopwords check
                if term.lower() in STOPWORDS:
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