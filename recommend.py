#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recommend.py
------------
Système de recommandation type Netflix:
 - popularity_based(): Séries les plus populaires (meilleures notes moyennes)
 - user_based_recommend(): Recommandations basées sur les utilisateurs similaires
 - hybrid_recommend(): Combinaison popularité + préférences utilisateur

Fichier de notes: ./data/ratings.json
Format:
{
  "alice": {"lost_vf": 5, "breakingbad_vf": 4},
  "bob": {"lost_vo": 4, "friends_vo": 5}
}
"""
import argparse
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def get_series_stats(ratings_file='./data/ratings.json'):
    """
    Calcule les statistiques pour chaque série.
    Returns: dict {series: {'avg_rating': float, 'num_ratings': int, 'popularity_score': float}}
    """
    if not os.path.exists(ratings_file):
        return {}
    
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings = json.load(f)
    
    # Collecter toutes les notes par série
    series_ratings = {}
    for user, user_ratings in ratings.items():
        for series, rating in user_ratings.items():
            if series not in series_ratings:
                series_ratings[series] = []
            series_ratings[series].append(rating)
    
    # Calculer les statistiques
    stats = {}
    for series, ratings_list in series_ratings.items():
        avg_rating = np.mean(ratings_list)
        num_ratings = len(ratings_list)
        
        # Score de popularité: combine note moyenne et nombre de notes
        # Plus une série a de bonnes notes ET est notée par beaucoup d'utilisateurs, plus elle est populaire
        popularity_score = avg_rating * np.log1p(num_ratings)  # log pour éviter que le nombre domine trop
        
        stats[series] = {
            'avg_rating': float(avg_rating),
            'num_ratings': int(num_ratings),
            'popularity_score': float(popularity_score)
        }
    
    return stats


def popularity_based_recommend(ratings_file='./data/ratings.json', topn=10, min_ratings=1, language=None):
    """
    Recommande les séries les plus populaires (meilleures notes moyennes + nombre de notes).
    
    Args:
        ratings_file: Fichier des notes
        topn: Nombre de recommandations
        min_ratings: Nombre minimum de notes requises
        language: Filtrer par langue ('vf', 'vo', ou None pour toutes)
    
    Returns:
        Liste de tuples (série, score_popularité, note_moyenne, nombre_notes)
    """
    stats = get_series_stats(ratings_file)
    
    if not stats:
        return []
    
    # Filtrer par langue si spécifié
    if language:
        stats = {s: st for s, st in stats.items() if s.lower().endswith(f'_{language.lower()}')}
    
    # Filtrer par nombre minimum de notes
    stats = {s: st for s, st in stats.items() if st['num_ratings'] >= min_ratings}
    
    # Trier par score de popularité
    sorted_series = sorted(stats.items(), key=lambda x: x[1]['popularity_score'], reverse=True)
    
    results = []
    for series, st in sorted_series[:topn]:
        results.append((series, st['popularity_score'], st['avg_rating'], st['num_ratings']))
    
    return results

def user_based_recommend(user_id, ratings_file='./data/ratings.json', topn=10, blend_popularity=True):
    """
    Recommandations basées sur les utilisateurs similaires (filtrage collaboratif user-based).
    Combine avec la popularité des séries pour améliorer les recommandations.
    
    Args:
        user_id: Identifiant de l'utilisateur
        ratings_file: Fichier des notes
        topn: Nombre de recommandations
        blend_popularity: Si True, combine avec le score de popularité
    
    Returns:
        Liste de tuples (série, score_final)
    """
    if not os.path.exists(ratings_file):
        print(f"Fichier de notes non trouvé: {ratings_file}")
        return []
    
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings = json.load(f)
    
    if user_id not in ratings:
        # Si l'utilisateur n'existe pas, retourner les séries populaires
        print(f"Utilisateur '{user_id}' non trouvé, recommandations basées sur la popularité")
        return [(s, score, avg, num) for s, score, avg, num in popularity_based_recommend(ratings_file, topn)]
    
    # Construire la matrice utilisateurs × séries
    users = list(ratings.keys())
    all_series = sorted({series for user in users for series in ratings[user].keys()})
    
    # Matrice de notes (users × series)
    R = np.zeros((len(users), len(all_series)))
    for ui, u in enumerate(users):
        for series, rating in ratings[u].items():
            if series in all_series:
                R[ui, all_series.index(series)] = rating
    
    # Calculer la similarité user-user (cosine similarity)
    user_sim = cosine_similarity(R)
    
    # Index de l'utilisateur cible
    uidx = users.index(user_id)
    
    # Trouver les utilisateurs similaires
    similar_users_scores = user_sim[uidx]
    
    # Prédire les notes pour les séries non notées
    user_ratings = R[uidx]
    rated_series = set(ratings[user_id].keys())
    
    predictions = {}
    for sidx, series in enumerate(all_series):
        if series in rated_series:
            continue
        
        # Calculer la note prédite basée sur les utilisateurs similaires
        numerator = 0
        denominator = 0
        
        for other_uidx, other_user in enumerate(users):
            if other_uidx == uidx:
                continue
            
            other_rating = R[other_uidx, sidx]
            if other_rating > 0:  # L'autre utilisateur a noté cette série
                similarity = similar_users_scores[other_uidx]
                if similarity > 0:
                    numerator += similarity * other_rating
                    denominator += similarity
        
        if denominator > 0:
            predicted_rating = numerator / denominator
            predictions[series] = predicted_rating
    
    # Optionnel: combiner avec la popularité
    if blend_popularity:
        stats = get_series_stats(ratings_file)
        for series in predictions:
            if series in stats:
                # Combiner: 70% prédiction utilisateur + 30% popularité normalisée
                pop_score_normalized = stats[series]['avg_rating'] / 5.0  # Normaliser sur 5
                predictions[series] = predictions[series] * 0.7 + pop_score_normalized * 5 * 0.3
    
    # Trier par score et retourner le top N
    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    return sorted_predictions[:topn]


def hybrid_recommend(user_id, ratings_file='./data/ratings.json', topn=10, 
                     popularity_weight=0.3, user_preference_weight=0.7):
    """
    Recommandations hybrides type Netflix:
    - Combine les préférences utilisateur (filtrage collaboratif)
    - Avec la popularité générale des séries
    
    Args:
        user_id: Identifiant de l'utilisateur
        ratings_file: Fichier des notes
        topn: Nombre de recommandations
        popularity_weight: Poids de la popularité (0-1)
        user_preference_weight: Poids des préférences utilisateur (0-1)
    
    Returns:
        Liste de tuples (série, score_hybride)
    """
    # 1. Recommandations basées sur l'utilisateur
    user_recs = user_based_recommend(user_id, ratings_file, topn=topn*2, blend_popularity=False)
    user_dict = {series: score for series, score in user_recs}
    
    # 2. Séries populaires
    pop_recs = popularity_based_recommend(ratings_file, topn=topn*2)
    
    # Normaliser les scores de popularité
    if pop_recs:
        max_pop = max(score for _, score, _, _ in pop_recs)
        pop_dict = {series: (score / max_pop) * 5 for series, score, _, _ in pop_recs}  # Normaliser sur 5
    else:
        pop_dict = {}
    
    # 3. Combiner les scores
    all_series = set(user_dict.keys()) | set(pop_dict.keys())
    
    # Exclure les séries déjà notées par l'utilisateur
    if os.path.exists(ratings_file):
        with open(ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
        if user_id in ratings:
            rated = set(ratings[user_id].keys())
            all_series = all_series - rated
    
    hybrid_scores = {}
    for series in all_series:
        user_score = user_dict.get(series, 0)
        pop_score = pop_dict.get(series, 0)
        
        # Score hybride pondéré
        hybrid_scores[series] = (user_score * user_preference_weight) + (pop_score * popularity_weight)
    
    # Trier et retourner les meilleures recommandations
    sorted_recs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_recs[:topn]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Système de recommandation de séries TV (type Netflix)')
    parser.add_argument('--user', help='ID utilisateur pour recommandations personnalisées')
    parser.add_argument('--popular', action='store_true', help='Afficher les séries les plus populaires')
    parser.add_argument('--language', choices=['vf', 'vo'], help='Filtrer par langue (vf ou vo)')
    parser.add_argument('--hybrid', action='store_true', help='Utiliser recommandations hybrides (user + popularité)')
    parser.add_argument('--top', type=int, default=10, help='Nombre de recommandations')
    parser.add_argument('--ratings', default='./data/ratings.json', help='Fichier de notes utilisateurs')
    args = parser.parse_args()
    
    if args.popular:
        print(f"\n=== Séries les plus populaires ===")
        if args.language:
            print(f"(Filtre: {args.language.upper()})")
        recs = popularity_based_recommend(args.ratings, topn=args.top, language=args.language)
        if recs:
            print(f"\n{'Rang':<6}{'Série':<30}{'Note moy.':<12}{'Nb notes':<12}{'Score pop.':<12}")
            print("-" * 72)
            for i, (series, pop_score, avg_rating, num_ratings) in enumerate(recs, 1):
                print(f"{i:<6}{series:<30}{avg_rating:<12.2f}{num_ratings:<12}{pop_score:<12.2f}")
        else:
            print("Aucune série trouvée")
    
    elif args.user:
        if args.hybrid:
            print(f"\n=== Recommandations hybrides pour '{args.user}' ===")
            print("(Combine vos préférences + popularité générale)")
            recs = hybrid_recommend(args.user, ratings_file=args.ratings, topn=args.top)
        else:
            print(f"\n=== Recommandations personnalisées pour '{args.user}' ===")
            print("(Basées sur les utilisateurs similaires)")
            recs = user_based_recommend(args.user, ratings_file=args.ratings, topn=args.top)
        
        if recs:
            print(f"\n{'Rang':<6}{'Série':<40}{'Score':<12}")
            print("-" * 58)
            for i, (series, score) in enumerate(recs, 1):
                print(f"{i:<6}{series:<40}{score:<12.2f}")
        else:
            print("Aucune recommandation trouvée")
    
    else:
        print("\nUsage:")
        print("  Séries populaires:              python recommend.py --popular --top 10")
        print("  Séries populaires VF:           python recommend.py --popular --language vf --top 10")
        print("  Recommandations utilisateur:    python recommend.py --user alice --top 10")
        print("  Recommandations hybrides:       python recommend.py --user alice --hybrid --top 10")