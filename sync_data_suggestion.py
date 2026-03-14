import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

# Configuration
DATA_FILE = "marksix_data.js"
URL_SOURCES = [
    "https://www.marksixlotterynumbers.hk/history/",
    "https://www.nfd.com.tw/house/1976-22.htm" # Fallback source
]

def parse_js_data(filepath):
    """Simple parser to extract the HIST_FREQ and existing metadata from js file."""
    if not os.path.exists(filepath):
        return None, None, None, None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract HIST_FREQ
    freq_match = re.search(r'const HIST_FREQ = ({.*?});', content, re.DOTALL)
    if not freq_match:
        return None, None, None, None
    
    # Extract Last Draw Date for comparison
    meta_match = re.search(r'lastDrawDate:\s+"(.*?)"', content)
    last_draw_date = meta_match.group(1) if meta_match else "1970-01-01"

    # Clean up the JS object to valid JSON for parsing
    raw_dict_str = freq_match.group(1)
    clean_dict_str = re.sub(r'(\d+):', r'"\1":', raw_dict_str)
    clean_dict_str = clean_dict_str.replace('};', '}').strip()
    
    try:
        hist_freq = json.loads(clean_dict_str)
    except Exception as e:
        print(f"Error parsing existing JS data: {e}")
        return None, None, None, None

    # Extract HOT and COLD arrays
    hot_match = re.search(r'const HOT_NUMS\s+=\s+(\[.*?\]);', content)
    cold_match = re.search(r'const COLD_NUMS\s+=\s+(\[.*?\]);', content)
    
    hot_nums = json.loads(hot_match.group(1)) if hot_match else []
    cold_nums = json.loads(cold_match.group(1)) if cold_match else []

    return hist_freq, hot_nums, cold_nums, last_draw_date

def get_latest_results(url):
    """Fetches the latest draw results from the web."""
    print(f"Fetching latest results from {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_draws = []
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # Look for date like 2026-03-12
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', row.get_text())
            draw_date = date_match.group(1) if date_match else None

            nums = []
            for cell in cells:
                found = re.findall(r'\b([1-9]|[1-4][0-9])\b', cell.get_text())
                if found:
                    nums.extend([int(n) for n in found])
            
            if len(nums) >= 6 and draw_date:
                all_draws.append({'date': draw_date, 'nums': nums[:7]})

        return all_draws
    except Exception as e:
        print(f"Web scraping error: {e}")
        return []

def update_data():
    hist_freq, hot_nums, cold_nums, last_draw_date = parse_js_data(DATA_FILE)
    if not hist_freq:
        print("Could not load original marksix_data.js. Aborting.")
        return

    new_draws = []
    for url in URL_SOURCES:
        new_draws = get_latest_results(url)
        if new_draws:
            break
        print(f"Retrying with alternative source...")
        
    if not new_draws:
        print("All sources failed to fetch new results.")
        return 'error'

    # Filter for draws newer than our records
    pending_draws = [d for d in new_draws if d['date'] > last_draw_date]
    
    if not pending_draws:
        print(f"Already up to date. (Last draw: {last_draw_date})")
        return 'no_change'

    # Process all new draws found
    print(f"Found {len(pending_draws)} new draws!")
    latest_date = last_draw_date
    for draw in reversed(pending_draws):
        print(f"Adding draw from {draw['date']}: {draw['nums']}")
        for n in draw['nums']:
            num_str = str(n)
            if num_str in hist_freq:
                hist_freq[num_str] += 1
        latest_date = draw['date']

    # Recalculate Hot/Cold (Simple ranking)
    sorted_items = sorted(hist_freq.items(), key=lambda x: x[1], reverse=True)
    new_hot = [int(x[0]) for x in sorted_items[:9]]
    new_cold = [int(x[0]) for x in sorted_items[-12:]]

    # Generate new JS content
    now = datetime.now()
    update_str = now.strftime("%B %Y")
    
    # Format HIST_FREQ nicely
    freq_lines = []
    freq_items = sorted(hist_freq.items(), key=lambda x: int(x[0]))
    for i in range(0, 49, 7):
        chunk = freq_items[i:i+7]
        line = "    " + ", ".join([f"{k:>2}: {v}" for k, v in chunk])
        freq_lines.append(line)
    
    new_js = f"""/**
 * Historical frequency data for HK Mark Six
 * Last Updated: {update_str}
 */
const DATA_META = {{
    lastUpdate: "{update_str}",
    lastDrawDate: "{latest_date}",
    period: "1976 — Present",
    totalDraws: "Calculated with results up to {latest_date}"
}};

const HIST_FREQ = {{
{",\n".join(freq_lines)}
}};

// Recent hot numbers (automatically updated)
const HOT_NUMS  = {json.dumps(new_hot)};
// Cold numbers (automatically updated)
const COLD_NUMS = {json.dumps(new_cold)};
"""
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(new_js)
    
    print(f"Successfully updated to {latest_date}")
    return 'updated'

if __name__ == "__main__":
    result = update_data()
    # Output for PHP to read
    print(f"RESULT:{result}")
