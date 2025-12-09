#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preprocess.py
----------------
Lire les fichiers de sous-titres sous la forme:
    ./subtitles/<SeriesName>/*.srt
et produire deux fichiers nettoyés par série:
    ./data/cleaned/<SeriesName>_vf.txt (français)
    ./data/cleaned/<SeriesName>_vo.txt (version originale)

Nettoyage fait:
 - suppression des timestamps (00:00:00,000 --> ...)
 - suppression des balises HTML
 - normalisation des accents (é -> e, ê -> e, à -> a, ç -> c, etc.)
 - suppression des caractères non-lettres
 - mise en minuscules
 - suppression des stopwords (français pour VF, anglais pour VO)
 - suppression des tokens courts (<=2)
"""
import argparse
import os
import re
import glob
import unicodedata
from tqdm import tqdm
import nltk
from langdetect import detect, LangDetectException

# S'assurer d'avoir les stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

# Normaliser les stopwords (enlever les accents)
def normalize_stopwords(stopwords_set):
    """Enlève les accents des stopwords."""
    normalized = set()
    for word in stopwords_set:
        nfd = unicodedata.normalize('NFD', word)
        normalized.add(''.join(c for c in nfd if unicodedata.category(c) != 'Mn'))
    return normalized

STOPWORDS_FR = normalize_stopwords(set(stopwords.words('french')))
STOPWORDS_EN = normalize_stopwords(set(stopwords.words('english')))

TIMESTAMP_RE = re.compile(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}')
TAG_RE = re.compile(r'<[^>]+>')


def remove_accents(text):
    """
    Convertit les caractères accentués en caractères non accentués.
    Exemple: é -> e, ê -> e, à -> a, ç -> c, etc.
    """
    # Normalise en NFD (décompose les caractères en base + diacritiques)
    nfd_form = unicodedata.normalize('NFD', text)
    # Supprime tous les caractères diacritiques (accents)
    return ''.join(char for char in nfd_form if unicodedata.category(char) != 'Mn')


def detect_language(text):
    """Détecte la langue du texte (fr ou en)."""
    try:
        # Prend un échantillon du texte pour la détection
        sample = ' '.join(text.split()[:500])  # Premiers 500 mots
        if len(sample) < 50:  # Si trop court, prendre tout
            sample = text
        lang = detect(sample)
        return lang
    except LangDetectException:
        return 'unknown'


def clean_text(text, language='fr'):
    """Nettoie le texte des sous-titres selon la langue."""
    # Supprimer timestamps et balises HTML
    text = TIMESTAMP_RE.sub(' ', text)
    text = TAG_RE.sub(' ', text)
    
    # Mise en minuscules AVANT tout
    text = text.lower()
    
    # SUPPRIMER TOUS LES ACCENTS EN PREMIER : é,è,ê,ë->e, à,â->a, ù,û->u, ô->o, ç->c, etc.
    text = remove_accents(text)
    
    # TRANSFORMER LES TIRETS EN ESPACES (peut-etre -> peut etre) APRÈS avoir enlevé les accents
    text = re.sub(r'-', ' ', text)
    
    # Supprimer les chiffres et numéros
    text = re.sub(r'\d+', ' ', text)
    
    # Supprimer TOUTE la ponctuation et caractères spéciaux
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Choisir les stopwords selon la langue
    stopwords_set = STOPWORDS_FR if language == 'fr' else STOPWORDS_EN
    
    # Filtrer les tokens (longueur > 2 et pas dans stopwords)
    tokens = [t for t in text.split() if len(t) > 2 and t not in stopwords_set]
    
    return ' '.join(tokens)


def extract_series_text_by_language(series_dir):
    """
    Extrait et sépare le texte par langue (VF et VO).
    Retourne deux chaînes: (texte_vf, texte_vo)
    """
    vf_parts = []
    vo_parts = []
    
    for ext in ('*.srt', '*.txt'):
        for path in glob.glob(os.path.join(series_dir, ext)):
            try:
                # Essayer différents encodages
                content = None
                for encoding in ['latin-1', 'utf-8', 'cp1252']:
                    try:
                        with open(path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                
                if content is None:
                    # Dernier recours : ignorer les erreurs
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                # Détecter la langue du fichier
                lang = detect_language(content)
                
                if lang == 'fr':
                    vf_parts.append(content)
                else:  # en ou autre -> considéré comme VO
                    vo_parts.append(content)
                    
            except Exception as e:
                print(f"Erreur lors de la lecture de {path}: {e}")
    
    return '\n'.join(vf_parts), '\n'.join(vo_parts)

def safe_filename(name):
    """Remplace les caractères interdits dans les noms de fichiers."""
    return re.sub(r'[\\/":*?<>|]+', '_', name)


def main(args):
    """Traite tous les sous-titres et génère les fichiers nettoyés séparés par langue."""
    subtitles_dir = args.subtitles
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    
    series_dirs = [
        d for d in os.listdir(subtitles_dir) 
        if os.path.isdir(os.path.join(subtitles_dir, d))
    ]
    
    # Si --series spécifié, traiter uniquement cette série
    if hasattr(args, 'series') and args.series:
        series_dirs = [s for s in series_dirs if s.lower() == args.series.lower()]
        if not series_dirs:
            print(f"Série '{args.series}' non trouvée!")
            return
    
    for series_name in tqdm(sorted(series_dirs), desc='Traitement des séries'):
        full_path = os.path.join(subtitles_dir, series_name)
        
        # Extraire le texte séparé par langue
        raw_vf, raw_vo = extract_series_text_by_language(full_path)
        
        safe_name = safe_filename(series_name)
        
        # Traiter et sauvegarder VF (français)
        if raw_vf.strip():
            cleaned_vf = clean_text(raw_vf, language='fr')
            vf_path = os.path.join(out_dir, f'{safe_name}_vf.txt')
            with open(vf_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_vf)
        
        # Traiter et sauvegarder VO (anglais)
        if raw_vo.strip():
            cleaned_vo = clean_text(raw_vo, language='en')
            vo_path = os.path.join(out_dir, f'{safe_name}_vo.txt')
            with open(vo_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_vo)
    
    print(f'Prétraitement terminé. Fichiers nettoyés dans {out_dir}')
    print(f'Format: <série>_vf.txt (français) et <série>_vo.txt (version originale)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prétraite les fichiers de sous-titres en fichiers texte nettoyés par série.'
    )
    parser.add_argument(
        '--subtitles', 
        required=True, 
        help='Répertoire contenant les sous-dossiers de séries'
    )
    parser.add_argument(
        '--out', 
        default='./data/cleaned', 
        help='Répertoire de sortie pour les fichiers nettoyés'
    )
    parser.add_argument(
        '--series',
        help='Nom de la série à traiter (ex: lost). Si omis, toutes les séries sont traitées.'
    )
    args = parser.parse_args()
    main(args)