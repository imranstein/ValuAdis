from bs4 import BeautifulSoup
import json
import os

def analyze_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # common classes
            classes = set()
            for tag in soup.find_all(True):
                for cls in tag.get('class', []):
                    classes.add(cls)
                    
            print(f"--- {filepath} ---")
            possible_wrappers = [c for c in classes if any(sub in c.lower() for sub in ['item', 'card', 'prop', 'list', 'advert'])]
            print("Possible wrappers:", sorted(possible_wrappers)[:20])
            
            # Find links
            links = soup.find_all('a', href=True)
            prop_links = [l['href'] for l in links if any(sub in l['href'].lower() for sub in ['/property/', '/real-estate/', '/rent/', '/sale/'])]
            if prop_links:
                print("Property link examples:", prop_links[:5])
            else:
                # print first few links just in case
                print("First few links:", [l['href'] for l in links][:5])
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

for f in ['tmp_ethiopiapropertycentre.html', 'tmp_jiji.html', 'tmp_zegebeya.html', 'tmp_ethiopianproperties.html', 'tmp_livingethio_props.html']:
    analyze_file(f)
