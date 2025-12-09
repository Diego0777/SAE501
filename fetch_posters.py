"""
Script pour récupérer les posters de toutes les séries via l'API TVmaze (GRATUITE SANS CLE)
"""
import requests
import time
import sqlite3
from database.db_sqlite import get_connection

# API TVmaze - GRATUITE, SANS CLÉ REQUISE !
TVMAZE_BASE_URL = "https://api.tvmaze.com"

# Mapping des noms de séries (titre dans la base -> titre pour recherche TMDB)
SERIES_MAPPING = {
    '24': '24',
    '90210': '90210',
    'alias': 'Alias',
    'angel': 'Angel',
    'battlestargalactica': 'Battlestar Galactica',
    'betteroffted': 'Better Off Ted',
    'bionicwoman': 'Bionic Woman',
    'blade': 'Blade: The Series',
    'bloodties': 'Blood Ties',
    'bones': 'Bones',
    'breakingbad': 'Breaking Bad',
    'buffy': 'Buffy the Vampire Slayer',
    'burnnotice': 'Burn Notice',
    'californication': 'Californication',
    'caprica': 'Caprica',
    'charmed': 'Charmed',
    'chuck': 'Chuck',
    'coldcase': 'Cold Case',
    'community': 'Community',
    'criminalminds': 'Criminal Minds',
    'cupid': 'Cupid',
    'daybreak': 'Daybreak',
    'demons': 'Demons',
    'desperatehousewives': 'Desperate Housewives',
    'dexter': 'Dexter',
    'dirt': 'Dirt',
    'dirtysexymoney': 'Dirty Sexy Money',
    'doctorwho': 'Doctor Who',
    'dollhouse': 'Dollhouse',
    'eleventhhour': 'Eleventh Hour',
    'entourage': 'Entourage',
    'eureka': 'Eureka',
    'extras': 'Extras',
    'fearitself': 'Fear Itself',
    'flashforward': 'FlashForward',
    'flashpoint': 'Flashpoint',
    'flightoftheconchords': 'Flight of the Conchords',
    'fridaynightlights': 'Friday Night Lights',
    'friends': 'Friends',
    'fringe': 'Fringe',
    'futurama': 'Futurama',
    'garyunmarried': 'Gary Unmarried',
    'ghostwhisperer': 'Ghost Whisperer',
    'gossipgirl': 'Gossip Girl',
    'greek': 'Greek',
    'greysanatomy': "Grey's Anatomy",
    'heroes': 'Heroes',
    'house': 'House',
    'howimetyourmother': 'How I Met Your Mother',
    'intreatment': 'In Treatment',
    'invasion': 'Invasion',
    'jake': 'Jake 2.0',
    'jekyll': 'Jekyll',
    'jericho': 'Jericho',
    'johnfromcincinnati': 'John from Cincinnati',
    'journeyman': 'Journeyman',
    'knightrider': 'Knight Rider',
    'kylexy': 'Kyle XY',
    'legendoftheseeker': 'Legend of the Seeker',
    'leverage': 'Leverage',
    'lietome': 'Lie to Me',
    'life': 'Life',
    'lost': 'Lost',
    'madmen': 'Mad Men',
    'mastersofscifi': 'Masters of Science Fiction',
    'medium': 'Medium',
    'melroseplace': 'Melrose Place',
    'mental': 'Mental',
    'merlin': 'Merlin',
    'moonlight': 'Moonlight',
    'mynameisearl': 'My Name Is Earl',
    'ncis': 'NCIS',
    'ncislosangeles': 'NCIS: Los Angeles',
    'niptuck': 'Nip/Tuck',
    'onetreehill': 'One Tree Hill',
    'oz': 'Oz',
    'painkillerjane': 'Painkiller Jane',
    'primeval': 'Primeval',
    'prisonbreak': 'Prison Break',
    'privatepractice': 'Private Practice',
    'psych': 'Psych',
    'pushingdaisies': 'Pushing Daisies',
    'raines': 'Raines',
    'reaper': 'Reaper',
    'robinhood': 'Robin Hood',
    'rome': 'Rome',
    'samanthawho': 'Samantha Who?',
    'sanctuary': 'Sanctuary',
    'scrubs': 'Scrubs',
    'sexandthecity': 'Sex and the City',
    'sixfeetunder': 'Six Feet Under',
    'skins': 'Skins',
    'smallville': 'Smallville',
    'sonsofanarchy': 'Sons of Anarchy',
    'southpark': 'South Park',
    'spaced': 'Spaced',
    'stargateatlantis': 'Stargate Atlantis',
    'stargatesg1': 'Stargate SG-1',
    'stargateuniverse': 'Stargate Universe',
    'supernatural': 'Supernatural',
    'swingtown': 'Swingtown',
    'the4400': 'The 4400',
    'thebigbangtheory': 'The Big Bang Theory',
    'theblackdonnellys': 'The Black Donnellys',
    'thekillpoint': 'The Kill Point',
    'thelostroom': 'The Lost Room',
    'thementalist': 'The Mentalist',
    'thenine': 'The Nine',
    'theoc': 'The O.C.',
    'thepretender': 'The Pretender',
    'theriches': 'The Riches',
    'thesarahconnorchronicles': 'Terminator: The Sarah Connor Chronicles',
    'theshield': 'The Shield',
    'thesopranos': 'The Sopranos',
    'thetudors': 'The Tudors',
    'thevampirediaries': 'The Vampire Diaries',
    'thewire': 'The Wire',
    'torchwood': 'Torchwood',
    'traveler': 'Traveler',
    'trucalling': 'Tru Calling',
    'trueblood': 'True Blood',
    'uglybetty': 'Ugly Betty',
    'v': 'V',
    'veronicamars': 'Veronica Mars',
    'weeds': 'Weeds',
    'whitechapel': 'Whitechapel',
    'womensmurderclub': "Women's Murder Club",
    'xfiles': 'The X-Files'
}

def search_series_on_tvmaze(series_name):
    """Rechercher une série sur TVmaze (API GRATUITE SANS CLÉ)."""
    url = f"{TVMAZE_BASE_URL}/search/shows"
    params = {'q': series_name}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            # Prendre le premier résultat
            first_result = data[0]
            show = first_result.get('show', {})
            image = show.get('image', {})
            
            # TVmaze fournit 'medium' et 'original', on prend 'original' pour la meilleure qualité
            poster_url = image.get('original') or image.get('medium')
            
            if poster_url:
                return poster_url
        
        return None
    except Exception as e:
        print(f"   ❌ Erreur TVmaze: {e}")
        return None

def extract_series_name(title):
    """Extraire le nom de la série sans le suffixe _vf ou _vo."""
    if title.endswith('_vf') or title.endswith('_vo'):
        return title[:-3]
    return title

def fetch_all_posters():
    """Récupérer les posters pour toutes les séries."""
    print("🎬 Récupération des posters via TVmaze (API GRATUITE)")
    print("=" * 60)
    
    # Ajouter la colonne poster_url si elle n'existe pas
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE series ADD COLUMN poster_url TEXT")
            conn.commit()
            print("✅ Colonne poster_url ajoutée à la table series\n")
        except sqlite3.OperationalError:
            print("ℹ️  Colonne poster_url déjà présente\n")
        
        # Récupérer toutes les séries
        cursor.execute("SELECT id, title FROM series ORDER BY title")
        series_list = cursor.fetchall()
    
    print(f"📊 {len(series_list)} séries à traiter\n")
    
    updated = 0
    not_found = 0
    
    # Cache pour éviter de chercher plusieurs fois la même série
    poster_cache = {}
    
    for serie_id, title in series_list:
        base_name = extract_series_name(title)
        
        # Vérifier si on a déjà le poster en cache
        if base_name in poster_cache:
            poster_url = poster_cache[base_name]
        else:
            # Chercher le nom dans le mapping
            search_name = SERIES_MAPPING.get(base_name, base_name)
            
            print(f"🔍 {title:<35} → {search_name}")
            
            # Rechercher sur TVmaze
            poster_url = search_series_on_tvmaze(search_name)
            
            if poster_url:
                print(f"   ✅ {poster_url[:80]}...")
                poster_cache[base_name] = poster_url
            else:
                print(f"   ⚠️  Poster non trouvé")
                poster_cache[base_name] = None
            
            # Respecter l'API (pas de limite stricte mais soyons courtois)
            time.sleep(0.1)
        
        # Mettre à jour la base de données
        if poster_url:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE series SET poster_url = ? WHERE id = ?",
                    (poster_url, serie_id)
                )
            updated += 1
        else:
            not_found += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Terminé !")
    print(f"   Posters trouvés: {updated}")
    print(f"   Non trouvés: {not_found}")
    print(f"   Total: {len(series_list)}")

if __name__ == '__main__':
    fetch_all_posters()
