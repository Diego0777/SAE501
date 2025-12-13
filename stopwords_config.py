#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration centralisée des stopwords utilisés dans preprocessing et indexing.
Permet de maintenir une liste unique de stopwords pour éviter les duos et incohérences.
"""

def get_stopwords():
    """
    Retourne un ensemble complet de stopwords français et anglais.
    Utiliser cette fonction dans preprocess.py ET indexer.py pour cohérence.
    """
    french_stop = {
        # Articles et prépositions
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'car',
        'ni', 'ne', 'pas', 'plus', 'moins', 'tres', 'trop', 'bien', 'mal', 'tout', 'tous', 'toute', 'toutes',
        
        # Pronoms
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'mon', 'ton', 'son',
        'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'ce', 'cet', 'cette', 'ces',
        'qui', 'que', 'quoi', 'dont', 'quand', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles',
        
        # Verbes être/avoir (tous les temps/modes)
        'suis', 'es', 'est', 'sommes', 'etes', 'sont', 'serai', 'seras', 'sera', 'serons', 'serez',
        'etais', 'etait', 'etions', 'etiez', 'etaient', 'etant', 'ete', 'etee', 'etees',
        'ai', 'as', 'avons', 'avez', 'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez',
        'avais', 'avait', 'avions', 'aviez', 'avaient', 'ayant', 'eu', 'eue', 'eues',
        'etre', 'avoir', 'sois', 'soit', 'soyons', 'soyez',
        
        # Verbes courants (infinitif)
        'aller', 'faire', 'dire', 'venir', 'pouvoir', 'vouloir', 'devoir', 'savoir', 'voir', 'donner',
        'mettre', 'prendre', 'vendre', 'partir', 'arriver', 'rester', 'tenir', 'entrer', 'sortir',
        'laisser', 'trouver', 'appeler', 'oublier', 'penser', 'croire', 'suivre', 'attendre', 'perdre',
        'passer', 'commencer', 'finir', 'changer', 'tourner', 'monter', 'descendre', 'mourir', 'naître',
        'vivre', 'marcher', 'courir', 'danser', 'chanter', 'parler', 'écouter', 'regarder', 'entendre',
        'manger', 'boire', 'dormir', 'travailler', 'jouer', 'rire', 'pleurer', 'crier', 'demander',
        
        # Verbes conjugués (3e personne singulier présent)
        'va', 'vais', 'vas', 'vont', 'allons', 'allez', 'fais', 'fait', 'faisons', 'faites', 'font',
        'dis', 'dit', 'disons', 'dites', 'disent', 'viens', 'vient', 'venons', 'venez', 'viennent',
        'peux', 'peut', 'pouvons', 'pouvez', 'peuvent', 'veux', 'veut', 'voulons', 'voulez', 'veulent',
        'dois', 'doit', 'devons', 'devez', 'doivent', 'sais', 'sait', 'savons', 'savez', 'savent',
        'vois', 'voit', 'voyons', 'voyez', 'voient', 'donne', 'donnes', 'donnons', 'donnez', 'donnent',
        'mets', 'met', 'mettons', 'mettez', 'mettent', 'prends', 'prend', 'prenons', 'prenez', 'prennent',
        'vends', 'vend', 'vendons', 'vendez', 'vendent', 'pars', 'part', 'partons', 'partez', 'partent',
        'arrive', 'arrives', 'arrivons', 'arrivez', 'arrivent', 'reste', 'restes', 'restons', 'restez',
        'tiens', 'tient', 'tenons', 'tenez', 'tiennent', 'entre', 'entres', 'entrons', 'entrez', 'entrent',
        'sort', 'sortons', 'sortez', 'sortent', 'laisse', 'laisses', 'laissons', 'laissez', 'laissent',
        'trouve', 'trouves', 'trouvons', 'trouvez', 'trouvent', 'appelle', 'appelles', 'appelons',
        'oublie', 'oublies', 'oublions', 'oubliez', 'oublient', 'pense', 'penses', 'pensons', 'pensez',
        'crois', 'croit', 'croyons', 'croyez', 'croient', 'suis', 'suit', 'suivons', 'suivez', 'suivent',
        'attends', 'attend', 'attendons', 'attendez', 'attendent', 'perds', 'perd', 'perdons', 'perdez',
        'passe', 'passes', 'passons', 'passez', 'passent', 'commence', 'commences', 'commencez',
        'finit', 'finissons', 'finissez', 'finissent', 'change', 'changes', 'changeons', 'changez',
        'tourne', 'tournes', 'tournons', 'tournez', 'tournent', 'monte', 'montes', 'montons', 'montez',
        'descend', 'descends', 'descendons', 'descendez', 'descendent', 'meurt', 'meurent', 'mourons',
        'nait', 'naissent', 'naissons', 'vivent', 'vivons', 'vivez', 'marche', 'marches', 'marchons',
        'court', 'courons', 'courez', 'courent', 'danse', 'danses', 'dansons', 'dansez', 'dansent',
        'chante', 'chantes', 'chantons', 'chantez', 'chantent', 'parle', 'parles', 'parlons', 'parlez',
        'ecoute', 'ecoutes', 'ecoutent', 'regarde', 'regardes', 'regardons', 'regardez', 'regardent',
        'entend', 'entends', 'entendons', 'entendez', 'entendent', 'mange', 'manges', 'mangeons',
        'boit', 'buvons', 'buvez', 'boivent', 'dort', 'dormons', 'dormez', 'dorment', 'travaille',
        'travailles', 'travaillons', 'travaillez', 'travaillent', 'joue', 'joues', 'jouons', 'jouez',
        'rit', 'rions', 'riez', 'rient', 'pleure', 'pleures', 'pleurons', 'pleurez', 'pleurent',
        'crie', 'cries', 'crions', 'criez', 'crient', 'demande', 'demandes', 'demandons', 'demandez',
        
        # Prépositions courantes manquantes
        'sur', 'dans', 'par', 'avec', 'sans', 'sous', 'entre', 'vers', 'chez', 'contre', 'depuis',
        'durant', 'hors', 'sauf', 'malgre', 'selon', 'concernant', 'grace', 'afin',
        
        # Adverbes et autres mots vides
        'si', 'comme', 'aussi', 'alors', 'encore', 'deja', 'toujours', 'jamais', 'ici', 'voici', 'voila',
        'oui', 'non', 'rien', 'quelque', 'quelques', 'chaque', 'autre', 'autres', 'meme', 'memes',
        'tait', 'tre', 'chose', 'choses', 'ah', 'oh', 'euh', 'hum', 'hein', 'ben', 'ok', 'okay',
        'ouais', 'nan', 'peu', 'beaucoup', 'assez', 'plutot', 'environ', 'surtout', 'notamment',
        'ensuite', 'puis', 'apres', 'avant', 'pendant', 'durant', 'maintenant', 'aujourd', 'hier', 'demain',
        'tard', 'tot', 'desormais', 'dorénavant', 'bientot', 'aussitot', 'soudain',
        'lentement', 'vite', 'rapidement', 'doucement', 'fortement', 'faiblement', 'pres', 'loin',
        'souvent', 'parfois', 'quelquefois', 'rarement', 'generalement', 'probablement', 'peut-être',
        'certainement', 'definitivement', 'absolument', 'franchement', 'honnetement', 'sincerement',
        'vraiment', 'faussement', 'clairement', 'gravement', 'legecement', 'facilement', 'difficilement',
        'precisement', 'exactement', 'simplement', 'seulement', 'juste', 'au',
        
        # Pronoms emphatiques/toniques manquants
        'toi', 'moi', 'lui', 'elle', 'nous', 'vous', 'eux', 'elles',
        'y', 'en', 'ca', 'cela', 'celui', 'celle', 'ceux', 'celles',
        
        # Mots tronqués (après suppression des accents)
        'parce', 'quelqu', 'aujourd', 'peut', 'c', 'd', 'l', 's', 't', 'n', 'j', 'qu',
        'lorsqu', 'puisqu', 'jusqu', 'tant', 'sait', 'faut', 'etait', 'quoi',
        
        # Interjections et exclamations
        'pardon', 'merci', 'excuse', 'sorry', 'damn', 'god', 'huh', 'gotta',
        
        # Adjectifs génériques courants
        'bon', 'bonne', 'bonnes', 'bons', 'mauvais', 'mauvaise', 'mauvaises', 'meilleur',
        'grand', 'petite', 'petit', 'nouvelle', 'nouveau', 'ancien', 'derniere', 'dernier',
        'premier', 'premiere', 'seul', 'seule', 'possible', 'impossible', 'vrai', 'faux',
        
        # Mots très génériques supplémentaires
        'machin', 'truc', 'bidule', 'chose', 'quoi', 'pourquoi'
    }
    
    english_stop = {
        # Articles et prépositions
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'as', 'than', 'so', 'such', 'is', 'are', 'was', 'were', 'been',
        
        # Verbes être/avoir
        'be', 'being', 'am', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        
        # Verbes courants
        'go', 'going', 'goes', 'went', 'gone', 'come', 'coming', 'comes', 'came',
        'get', 'getting', 'gets', 'got', 'gotten', 'make', 'making', 'makes', 'made',
        'take', 'taking', 'takes', 'took', 'taken', 'see', 'seeing', 'sees', 'saw', 'seen',
        'say', 'saying', 'says', 'said', 'know', 'knowing', 'knows', 'knew', 'known',
        'think', 'thinking', 'thinks', 'thought', 'want', 'wanting', 'wants', 'wanted',
        'need', 'needing', 'needs', 'needed', 'look', 'looking', 'looks', 'looked',
        'tell', 'telling', 'tells', 'told', 'ask', 'asking', 'asks', 'asked',
        'let', 'letting', 'lets', 'give', 'giving', 'gives', 'gave', 'given',
        'find', 'finding', 'finds', 'found', 'use', 'using', 'uses', 'used',
        'work', 'working', 'works', 'worked', 'call', 'calling', 'calls', 'called',
        'try', 'trying', 'tries', 'tried', 'feel', 'feeling', 'feels', 'felt',
        'become', 'becoming', 'becomes', 'became', 'leave', 'leaving', 'leaves', 'left',
        'put', 'putting', 'puts', 'mean', 'meaning', 'means', 'meant', 'keep', 'keeping', 'keeps', 'kept',
        'would', 'should', 'could', 'might', 'must', 'can', 'will', 'shall', 'may',
        'turn', 'turning', 'turns', 'turned', 'start', 'starting', 'starts', 'started',
        'show', 'showing', 'shows', 'showed', 'hear', 'hearing', 'hears', 'heard',
        'meet', 'meeting', 'meets', 'met', 'include', 'including', 'includes', 'included',
        'continue', 'continuing', 'continues', 'continued', 'set', 'setting', 'sets',
        'learn', 'learning', 'learns', 'learned', 'taught', 'change', 'changing', 'changes', 'changed',
        'lead', 'leading', 'leads', 'led', 'understand', 'understanding', 'understands', 'understood',
        'watch', 'watching', 'watches', 'watched', 'follow', 'following', 'follows', 'followed',
        'stop', 'stopping', 'stops', 'stopped', 'create', 'creating', 'creates', 'created',
        'speak', 'speaking', 'speaks', 'spoke', 'spoken', 'read', 'reading', 'reads',
        'allow', 'allowing', 'allows', 'allowed', 'add', 'adding', 'adds', 'added',
        'spend', 'spending', 'spends', 'spent', 'grow', 'growing', 'grows', 'grew', 'grown',
        'open', 'opening', 'opens', 'opened', 'walk', 'walking', 'walks', 'walked',
        'win', 'winning', 'wins', 'won', 'offer', 'offering', 'offers', 'offered',
        'remember', 'remembering', 'remembers', 'remembered', 'love', 'loving', 'loves', 'loved',
        'consider', 'considering', 'considers', 'considered', 'appear', 'appearing', 'appears', 'appeared',
        'buy', 'buying', 'buys', 'bought', 'wait', 'waiting', 'waits', 'waited',
        'serve', 'serving', 'serves', 'served', 'die', 'dying', 'dies', 'died',
        'send', 'sending', 'sends', 'sent', 'expect', 'expecting', 'expects', 'expected',
        'build', 'building', 'builds', 'built', 'stay', 'staying', 'stays', 'stayed',
        'fall', 'falling', 'falls', 'fell', 'fallen', 'cut', 'cutting', 'cuts',
        'reach', 'reaching', 'reaches', 'reached', 'kill', 'killing', 'kills', 'killed',
        'remain', 'remaining', 'remains', 'remained', 'suggest', 'suggesting', 'suggests', 'suggested',
        'raise', 'raising', 'raises', 'raised', 'pass', 'passing', 'passes', 'passed',
        'sell', 'selling', 'sells', 'sold', 'require', 'requiring', 'requires', 'required',
        'report', 'reporting', 'reports', 'reported', 'decide', 'deciding', 'decides', 'decided',
        'describe', 'describing', 'describes', 'described',
        
        # Pronoms
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
        'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
        
        # Quantificateurs
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'any',
        'many', 'much', 'no', 'none', 'nothing', 'anybody', 'everybody', 'nobody', 'somebody',
        'anyone', 'someone', 'everyone', 'something', 'anything', 'everything',
        
        # Adverbes et autres mots vides
        'very', 'just', 'now', 'only', 'own', 'same', 'also', 'too', 'not', 'no', 'nor',
        'well', 'really', 'even', 'rather', 'quite', 'almost', 'ever', 'never', 'always',
        'sometimes', 'often', 'usually', 'probably', 'certainly', 'definitely', 'maybe', 'perhaps',
        'seriously', 'actually', 'basically', 'literally', 'simply', 'then', 'here', 'there',
        'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whose', 'whom',
        'yeah', 'hey', 'yes', 'okay', 'ok', 'right', 'sure', 'sorry', 'thank', 'thanks',
        'please', 'hello', 'hi', 'bye', 'goodbye', 'good', 'great', 'wow', 'oh', 'ah',
        'uh', 'er', 'um', 'mm', 'hmm', 'honestly', 'frankly', 'basically', 'essentially',
        'roughly', 'still', 'yet', 'already', 'soon', 'later', 'early', 'late',
        'fast', 'slow', 'away', 'back', 'down', 'out', 'in', 'around', 'along',
        'across', 'over', 'under', 'near', 'far', 'close', 'open', 'wide', 'deep',
        'high', 'low', 'short', 'long', 'big', 'small', 'great', 'little',
        
        # Mots tronqués / contractés
        'dont', 'cant', 'wont', 'doesnt', 'isnt', 'arent', 'wasnt', 'werent', 'havent',
        'hasnt', 'hadnt', 'didnt', 'shouldnt', 'wouldnt', 'couldnt', 'mustnt',
        's', 'd', 't', 're', 've', 'll', 'm', 'n', 'nt',
        
        # Formes tronquées après suppression des apostrophes (ex: "didn't" → "didn" + "t")
        'didn', 'doesn', 'isn', 'aren', 'wasn', 'weren', 'haven', 'hasn', 'hadn',
        'shouldn', 'wouldn', 'couldn', 'mustn', 'don', 'won', 'can',
        
        # Mots courants trop génériques
        'time', 'times', 'way', 'thing', 'things', 'place', 'day', 'night', 'morning',
        'evening', 'moment', 'second', 'minute', 'hour', 'week', 'year', 'month',
        'guy', 'guys', 'man', 'men', 'woman', 'women', 'person', 'people', 'persons',
        'friend', 'friends', 'family', 'life', 'world', 'hand', 'eye', 'face', 'head',
        'body', 'part', 'piece', 'bit', 'lot', 'bunch', 'set', 'group', 'number',
        'kind', 'sort', 'type', 'form', 'matter', 'reason', 'cause', 'effect', 'result',
        'point', 'purpose', 'idea', 'thought', 'feeling', 'sense', 'sound', 'name',
        'word', 'line', 'money', 'cost', 'price', 'value', 'size', 'level', 'right',
        'left', 'side', 'middle', 'center', 'top', 'bottom', 'end', 'beginning', 'start',
        
        # Mots supplémentaires courants
        'like', 'talk', 'gonna', 'gotta', 'wanna', 'clock', 'o', 'because', 'till', 'til'
    }
    
    return french_stop | english_stop


def get_french_stopwords():
    """Retourne seulement les stopwords français (pour preprocess.py VF)."""
    french_stop = {
        # Articles et prépositions
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'car',
        'ni', 'ne', 'pas', 'plus', 'moins', 'tres', 'trop', 'bien', 'mal', 'tout', 'tous', 'toute', 'toutes',
        
        # Pronoms
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'mon', 'ton', 'son',
        'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre', 'leur', 'ce', 'cet', 'cette', 'ces',
        'qui', 'que', 'quoi', 'dont', 'quand', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles',
        
        # Verbes être/avoir (tous les temps/modes)
        'suis', 'es', 'est', 'sommes', 'etes', 'sont', 'serai', 'seras', 'sera', 'serons', 'serez',
        'etais', 'etait', 'etions', 'etiez', 'etaient', 'etant', 'ete', 'etee', 'etees',
        'ai', 'as', 'avons', 'avez', 'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez',
        'avais', 'avait', 'avions', 'aviez', 'avaient', 'ayant', 'eu', 'eue', 'eues',
        'etre', 'avoir', 'sois', 'soit', 'soyons', 'soyez',
        
        # Verbes courants (infinitif)
        'aller', 'faire', 'dire', 'venir', 'pouvoir', 'vouloir', 'devoir', 'savoir', 'voir', 'donner',
        'mettre', 'prendre', 'vendre', 'partir', 'arriver', 'rester', 'tenir', 'entrer', 'sortir',
        'laisser', 'trouver', 'appeler', 'oublier', 'penser', 'croire', 'suivre', 'attendre', 'perdre',
        'passer', 'commencer', 'finir', 'changer', 'tourner', 'monter', 'descendre', 'mourir', 'naître',
        'vivre', 'marcher', 'courir', 'danser', 'chanter', 'parler', 'écouter', 'regarder', 'entendre',
        'manger', 'boire', 'dormir', 'travailler', 'jouer', 'rire', 'pleurer', 'crier', 'demander',
        
        # Verbes conjugués (3e personne singulier présent)
        'va', 'vais', 'vas', 'vont', 'allons', 'allez', 'fais', 'fait', 'faisons', 'faites', 'font',
        'dis', 'dit', 'disons', 'dites', 'disent', 'viens', 'vient', 'venons', 'venez', 'viennent',
        'peux', 'peut', 'pouvons', 'pouvez', 'peuvent', 'veux', 'veut', 'voulons', 'voulez', 'veulent',
        'dois', 'doit', 'devons', 'devez', 'doivent', 'sais', 'sait', 'savons', 'savez', 'savent',
        'vois', 'voit', 'voyons', 'voyez', 'voient', 'donne', 'donnes', 'donnons', 'donnez', 'donnent',
        'mets', 'met', 'mettons', 'mettez', 'mettent', 'prends', 'prend', 'prenons', 'prenez', 'prennent',
        'vends', 'vend', 'vendons', 'vendez', 'vendent', 'pars', 'part', 'partons', 'partez', 'partent',
        'arrive', 'arrives', 'arrivons', 'arrivez', 'arrivent', 'reste', 'restes', 'restons', 'restez',
        'tiens', 'tient', 'tenons', 'tenez', 'tiennent', 'entre', 'entres', 'entrons', 'entrez', 'entrent',
        'sort', 'sortons', 'sortez', 'sortent', 'laisse', 'laisses', 'laissons', 'laissez', 'laissent',
        'trouve', 'trouves', 'trouvons', 'trouvez', 'trouvent', 'appelle', 'appelles', 'appelons',
        'oublie', 'oublies', 'oublions', 'oubliez', 'oublient', 'pense', 'penses', 'pensons', 'pensez',
        'crois', 'croit', 'croyons', 'croyez', 'croient', 'suis', 'suit', 'suivons', 'suivez', 'suivent',
        'attends', 'attend', 'attendons', 'attendez', 'attendent', 'perds', 'perd', 'perdons', 'perdez',
        'passe', 'passes', 'passons', 'passez', 'passent', 'commence', 'commences', 'commencez',
        'finit', 'finissons', 'finissez', 'finissent', 'change', 'changes', 'changeons', 'changez',
        'tourne', 'tournes', 'tournons', 'tournez', 'tournent', 'monte', 'montes', 'montons', 'montez',
        'descend', 'descends', 'descendons', 'descendez', 'descendent', 'meurt', 'meurent', 'mourons',
        'nait', 'naissent', 'naissons', 'vivent', 'vivons', 'vivez', 'marche', 'marches', 'marchons',
        'court', 'courons', 'courez', 'courent', 'danse', 'danses', 'dansons', 'dansez', 'dansent',
        'chante', 'chantes', 'chantons', 'chantez', 'chantent', 'parle', 'parles', 'parlons', 'parlez',
        'ecoute', 'ecoutes', 'ecoutent', 'regarde', 'regardes', 'regardons', 'regardez', 'regardent',
        'entend', 'entends', 'entendons', 'entendez', 'entendent', 'mange', 'manges', 'mangeons',
        'boit', 'buvons', 'buvez', 'boivent', 'dort', 'dormons', 'dormez', 'dorment', 'travaille',
        'travailles', 'travaillons', 'travaillez', 'travaillent', 'joue', 'joues', 'jouons', 'jouez',
        'rit', 'rions', 'riez', 'rient', 'pleure', 'pleures', 'pleurons', 'pleurez', 'pleurent',
        'crie', 'cries', 'crions', 'criez', 'crient', 'demande', 'demandes', 'demandons', 'demandez',
        
        # Prépositions courantes manquantes
        'sur', 'dans', 'par', 'avec', 'sans', 'sous', 'entre', 'vers', 'chez', 'contre', 'depuis',
        'durant', 'hors', 'sauf', 'malgre', 'selon', 'concernant', 'grace', 'afin',
        
        # Adverbes et autres mots vides
        'si', 'pour', 'comme', 'aussi', 'alors', 'encore', 'deja', 'toujours', 'jamais', 'ici', 'voici', 'voila',
        'oui', 'non', 'rien', 'quelque', 'quelques', 'chaque', 'autre', 'autres', 'meme', 'memes',
        'tait', 'tre', 'chose', 'choses', 'ah', 'oh', 'euh', 'hum', 'hein', 'ben', 'ok', 'okay',
        'ouais', 'nan', 'peu', 'beaucoup', 'assez', 'plutot', 'environ', 'surtout', 'notamment',
        'ensuite', 'puis', 'apres', 'avant', 'pendant', 'durant', 'maintenant', 'aujourd', 'hier', 'demain',
        'tard', 'tot', 'desormais', 'dorénavant', 'bientot', 'aussitot', 'soudain',
        'lentement', 'vite', 'rapidement', 'doucement', 'fortement', 'faiblement', 'pres', 'loin',
        'souvent', 'parfois', 'quelquefois', 'rarement', 'generalement', 'probablement', 'peut-être',
        'certainement', 'definitivement', 'absolument', 'franchement', 'honnetement', 'sincerement',
        'vraiment', 'faussement', 'clairement', 'gravement', 'legecement', 'facilement', 'difficilement',
        'precisement', 'exactement', 'simplement', 'seulement', 'juste', 'au',
        
        # Pronoms emphatiques/toniques manquants
        'toi', 'moi', 'lui', 'elle', 'nous', 'vous', 'eux', 'elles', 'ils',
        'y', 'en', 'ca', 'cela', 'celui', 'celle', 'ceux', 'celles',
        
        # Mots tronqués (après suppression des accents)
        'parce', 'quelqu', 'aujourd', 'peut', 'c', 'd', 'l', 's', 't', 'n', 'j', 'qu',
        'lorsqu', 'puisqu', 'jusqu', 'tant', 'sait', 'faut', 'etait', 'quoi',
        
        # Interjections et exclamations
        'pardon', 'merci', 'excuse', 'sorry', 'damn', 'god', 'huh', 'gotta',
        
        # Mots très génériques supplémentaires
        'machin', 'truc', 'bidule', 'chose', 'quoi', 'pourquoi'
    }
    
    return french_stop


def get_english_stopwords():
    """Retourne seulement les stopwords anglais (pour preprocess.py VO)."""
    english_stop = {
        # Articles et prépositions
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'as', 'than', 'so', 'such', 'is', 'are', 'was', 'were', 'been',
        
        # Verbes être/avoir
        'be', 'being', 'am', 'is', 'are', 'was', 'were', 'been',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        
        # Verbes courants
        'go', 'going', 'goes', 'went', 'gone', 'come', 'coming', 'comes', 'came',
        'get', 'getting', 'gets', 'got', 'gotten', 'make', 'making', 'makes', 'made',
        'take', 'taking', 'takes', 'took', 'taken', 'see', 'seeing', 'sees', 'saw', 'seen',
        'say', 'saying', 'says', 'said', 'know', 'knowing', 'knows', 'knew', 'known',
        'think', 'thinking', 'thinks', 'thought', 'want', 'wanting', 'wants', 'wanted',
        'need', 'needing', 'needs', 'needed', 'look', 'looking', 'looks', 'looked',
        'tell', 'telling', 'tells', 'told', 'ask', 'asking', 'asks', 'asked',
        'let', 'letting', 'lets', 'give', 'giving', 'gives', 'gave', 'given',
        'find', 'finding', 'finds', 'found', 'use', 'using', 'uses', 'used',
        'work', 'working', 'works', 'worked', 'call', 'calling', 'calls', 'called',
        'try', 'trying', 'tries', 'tried', 'feel', 'feeling', 'feels', 'felt',
        'become', 'becoming', 'becomes', 'became', 'leave', 'leaving', 'leaves', 'left',
        'put', 'putting', 'puts', 'mean', 'meaning', 'means', 'meant', 'keep', 'keeping', 'keeps', 'kept',
        'would', 'should', 'could', 'might', 'must', 'can', 'will', 'shall', 'may',
        'turn', 'turning', 'turns', 'turned', 'start', 'starting', 'starts', 'started',
        'show', 'showing', 'shows', 'showed', 'hear', 'hearing', 'hears', 'heard',
        'let', 'letting', 'lets', 'let', 'meet', 'meeting', 'meets', 'met',
        'include', 'including', 'includes', 'included', 'continue', 'continuing', 'continues', 'continued',
        'set', 'setting', 'sets', 'learn', 'learning', 'learns', 'learned', 'taught',
        'change', 'changing', 'changes', 'changed', 'lead', 'leading', 'leads', 'led',
        'understand', 'understanding', 'understands', 'understood', 'watch', 'watching', 'watches', 'watched',
        'follow', 'following', 'follows', 'followed', 'stop', 'stopping', 'stops', 'stopped',
        'create', 'creating', 'creates', 'created', 'speak', 'speaking', 'speaks', 'spoke', 'spoken',
        'read', 'reading', 'reads', 'read', 'allow', 'allowing', 'allows', 'allowed',
        'add', 'adding', 'adds', 'added', 'spend', 'spending', 'spends', 'spent',
        'grow', 'growing', 'grows', 'grew', 'grown', 'open', 'opening', 'opens', 'opened',
        'walk', 'walking', 'walks', 'walked', 'win', 'winning', 'wins', 'won',
        'offer', 'offering', 'offers', 'offered', 'remember', 'remembering', 'remembers', 'remembered',
        'love', 'loving', 'loves', 'loved', 'consider', 'considering', 'considers', 'considered',
        'appear', 'appearing', 'appears', 'appeared', 'buy', 'buying', 'buys', 'bought',
        'wait', 'waiting', 'waits', 'waited', 'serve', 'serving', 'serves', 'served',
        'die', 'dying', 'dies', 'died', 'send', 'sending', 'sends', 'sent',
        'expect', 'expecting', 'expects', 'expected', 'build', 'building', 'builds', 'built',
        'stay', 'staying', 'stays', 'stayed', 'fall', 'falling', 'falls', 'fell', 'fallen',
        'cut', 'cutting', 'cuts', 'reach', 'reaching', 'reaches', 'reached',
        'kill', 'killing', 'kills', 'killed', 'remain', 'remaining', 'remains', 'remained',
        'suggest', 'suggesting', 'suggests', 'suggested', 'raise', 'raising', 'raises', 'raised',
        'pass', 'passing', 'passes', 'passed', 'sell', 'selling', 'sells', 'sold',
        'require', 'requiring', 'requires', 'required', 'report', 'reporting', 'reports', 'reported',
        'decide', 'deciding', 'decides', 'decided', 'describe', 'describing', 'describes', 'described',
        
        # Pronoms
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
        'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose', 'which', 'what',
        
        # Quantificateurs
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'any',
        'many', 'much', 'no', 'none', 'nothing', 'anybody', 'everybody', 'nobody', 'somebody',
        'anyone', 'someone', 'everyone', 'something', 'anything', 'everything',
        
        # Verbes très courants manquants
        'like', 'talk', 'listen', 'watch', 'think', 'believe', 'seem', 'appear', 'sound',
        'look', 'taste', 'smell', 'feel', 'touch', 'grab', 'hold', 'carry', 'move',
        'run', 'walk', 'jump', 'sit', 'stand', 'lie', 'live', 'stay', 'wait',
        'talk', 'speak', 'say', 'tell', 'ask', 'answer', 'reply', 'respond',
        
        # Adverbes très courants manquants
        'gonna', 'gotta', 'wanna', 'dunno', 'kinda', 'sorta', 'pretty', 'kind',
        'totally', 'absolutely', 'really', 'very', 'so', 'such', 'too', 'also',
        
        # Prépositions manquantes
        'into', 'onto', 'off', 'out', 'up', 'down', 'through', 'across', 'along',
        'past', 'without', 'within', 'during', 'throughout', 'despite', 'plus',
        
        # Adverbes et autres mots vides
        'very', 'just', 'now', 'only', 'own', 'same', 'also', 'too', 'not', 'no', 'nor',
        'well', 'really', 'even', 'rather', 'quite', 'almost', 'ever', 'never', 'always',
        'sometimes', 'often', 'usually', 'probably', 'certainly', 'definitely', 'maybe', 'perhaps',
        'seriously', 'actually', 'basically', 'literally', 'simply', 'then', 'here', 'there',
        'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whose', 'whom',
        'yeah', 'hey', 'yes', 'okay', 'ok', 'right', 'sure', 'sorry', 'thank', 'thanks',
        'please', 'hello', 'hi', 'bye', 'goodbye', 'good', 'great', 'wow', 'oh', 'ah',
        'uh', 'er', 'um', 'mm', 'hmm', 'honestly', 'frankly', 'basically', 'essentially',
        'roughly', 'quite', 'rather', 'still', 'yet', 'already', 'soon', 'later', 'early',
        'late', 'fast', 'slow', 'away', 'back', 'down', 'out', 'in', 'around', 'along',
        'across', 'over', 'under', 'near', 'far', 'close', 'open', 'wide', 'deep',
        'high', 'low', 'short', 'long', 'big', 'small', 'great', 'little',
        
        # Mots tronqués / contractés
        'dont', 'cant', 'wont', 'doesnt', 'isnt', 'arent', 'wasnt', 'werent', 'havent',
        'hasnt', 'hadnt', 'didnt', 'shouldnt', 'wouldnt', 'couldnt', 'mustnt',
        's', 'd', 't', 're', 've', 'll', 'm', 'n', 'nt',
        
        # Formes tronquées après suppression des apostrophes
        'didn', 'doesn', 'isn', 'aren', 'wasn', 'weren', 'haven', 'hasn', 'hadn',
        'shouldn', 'wouldn', 'couldn', 'mustn', 'don', 'won', 'can',
        
        # Formes tronquées supplémentaires
        'gonna', 'gotta', 'wanna', 'dunno', 'kinda', 'sorta', 'ain', 'ain\'t', 'y\'all',
        'ing', 'ed', 'er', 'est', 'ly',
        
        # Mots courants trop génériques
        'time', 'times', 'way', 'thing', 'things', 'place', 'day', 'night', 'morning',
        'evening', 'moment', 'second', 'minute', 'hour', 'week', 'year', 'month',
        'guy', 'guys', 'man', 'men', 'woman', 'women', 'person', 'people', 'persons',
        'friend', 'friends', 'family', 'life', 'world', 'hand', 'eye', 'face', 'head',
        'body', 'part', 'piece', 'bit', 'lot', 'bunch', 'set', 'group', 'number',
        'kind', 'sort', 'type', 'form', 'matter', 'reason', 'cause', 'effect', 'result',
        'point', 'purpose', 'idea', 'thought', 'feeling', 'sense', 'sound', 'name',
        'word', 'line', 'money', 'cost', 'price', 'value', 'size', 'level', 'right',
        'left', 'side', 'middle', 'center', 'top', 'bottom', 'end', 'beginning', 'start',
        'stuff', 'thing', 'things', 'hell', 'way', 'ways', 'means', 'means', 'ways', 
        'stuff', 'things'
    }
    
    return english_stop
