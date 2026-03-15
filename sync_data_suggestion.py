import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime

# Configuration
DATA_FILE = "marksix_data.js"
PRIMARY_SOURCE = "https://www.marksixlotterynumbers.hk/history/"
NFD_SUMMARY_URL = "https://www.nfd.com.tw/house/1976-22.htm"
NFD_YEAR_BASE = "https://www.nfd.com.tw/house/year/{}.htm"

# Ball Color Mapping
BALL_COLORS = {
    "red": [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46],
    "blue": [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48],
    "green": [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]
}

def parse_js_data(filepath):
    """Parses existing JS data to get current state."""
    if not os.path.exists(filepath):
        return {}, [], [], "1970-01-01"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        freq_match = re.search(r'const HIST_FREQ = ({.*?});', content, re.DOTALL)
        if not freq_match:
            return {}, [], [], "1970-01-01"
        
        meta_match = re.search(r'lastDrawDate:\s+"(.*?)"', content)
        last_draw_date = meta_match.group(1) if meta_match else "1970-01-01"

        raw_dict_str = freq_match.group(1)
        clean_dict_str = re.sub(r'(\d+):', r'"\1":', raw_dict_str)
        clean_dict_str = clean_dict_str.replace('};', '}').strip()
        hist_freq = json.loads(clean_dict_str)

        hot_match = re.search(r'const HOT_NUMS\s+=\s+(\[.*?\]);', content)
        cold_match = re.search(r'const COLD_NUMS\s+=\s+(\[.*?\]);', content)
        hot_nums = json.loads(hot_match.group(1)) if hot_match else []
        cold_nums = json.loads(cold_match.group(1)) if cold_match else []

        return hist_freq, hot_nums, cold_nums, last_draw_date
    except Exception as e:
        print(f"Error parsing existing JS: {e}")
        return {}, [], [], "1970-01-01"

def get_latest_results_primary():
    """Fetches from marksixlotterynumbers.hk (Primary)."""
    print(f"Fetching from primary source: {PRIMARY_SOURCE}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(PRIMARY_SOURCE, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_draws = []
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2: continue
            
            # Date look for "2026年3月12日"
            text = row.get_text()
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
            if date_match:
                y, m, d = date_match.groups()
                draw_date = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                # Fallback to old format just in case
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                draw_date = date_match.group(1) if date_match else None

            if not draw_date: continue

            nums = []
            # Try to find numbers in the title attributes first (more precise)
            ball_divs = row.find_all('div', title=re.compile(r'號碼'))
            for div in ball_divs:
                val_match = re.search(r'(\d+)', div.get_text(strip=True))
                if val_match:
                    nums.append(int(val_match.group(1)))
            
            # If no ball divs found, try general number extraction
            if not nums:
                for cell in cells[2:]: # Usually starts from index 2
                    found = re.findall(r'\b([1-9]|[1-4][0-9])\b', cell.get_text())
                    if found:
                        nums.extend([int(n) for n in found])
            
            if len(nums) >= 6:
                all_draws.append({'date': draw_date, 'nums': nums[:7]})
        
        # De-duplicate by date to prevent double entries if source has duplicates
        unique_draws = {d['date']: d for d in all_draws}
        final_draws = sorted(unique_draws.values(), key=lambda x: x['date'])
        return final_draws
    except Exception as e:
        print(f"Primary source error: {e}")
        return []

def get_historical_summary():
    """Scrapes 1976-22.htm for total counts up to 2025."""
    print(f"Fetching historical summary from {NFD_SUMMARY_URL}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(NFD_SUMMARY_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        table = soup.find('table')
        if not table: return None
            
        summary_freq = {}
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if not tds: continue
            
            ball_text = tds[0].get_text(strip=True)
            if re.match(r'^0?[1-9]$|^[1-4][0-9]$', ball_text):
                ball_num = str(int(ball_text))
                total_text = tds[-1].get_text(strip=True)
                if total_text.isdigit():
                    summary_freq[ball_num] = int(total_text)
        return summary_freq
    except Exception as e:
        print(f"Historical summary error: {e}")
        return None

def get_nfd_year_results(year):
    """Scrapes individual draws for a specific year from nfd.com.tw (Fallback)."""
    url = NFD_YEAR_BASE.format(year)
    print(f"Fetching {year} draws from fallback {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        table = soup.find('table')
        if not table: return []
            
        all_draws = []
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) < 10: continue
            try:
                row_year = tds[0].get_text(strip=True)
                row_date = tds[1].get_text(strip=True)
                if not re.match(r'\d{4}', row_year) or not re.match(r'\d{2}/\d{2}', row_date):
                    continue
                full_date = f"{row_year}-{row_date.replace('/', '-')}"
                nums = []
                for i in range(3, 10):
                    num_text = tds[i].get_text(strip=True)
                    if num_text.isdigit(): nums.append(int(num_text))
                if len(nums) == 7: all_draws.append({'date': full_date, 'nums': nums[:7]})
            except: continue
        # De-duplicate by date
        unique_draws = {d['date']: d for d in all_draws}
        final_draws = sorted(unique_draws.values(), key=lambda x: x['date'])
        return final_draws
    except Exception as e:
        print(f"Yearly draws error ({year}): {e}")
        return []

def update_data():
    current_freq, current_hot, current_cold, last_draw_date = parse_js_data(DATA_FILE)
    
    # 1. Primary Source Catch-up (Modern results)
    new_draws = get_latest_results_primary()
    
    # 2. Fallback to NFD if primary is dry or missing
    if not new_draws:
        print("Primary source dry, checking NFD yearly draws...")
        new_draws = get_nfd_year_results(datetime.now().year)

    # 3. Base Data Check (Initialization/Validation)
    if not current_freq:
        print("No existing data found. Initializing from historical summary...")
        base_freq = get_historical_summary()
        if not base_freq:
            print("Failed to initialize base data.")
            return 'error'
        # Summary is up to end of 2025.
        final_freq = base_freq.copy()
        start_date = "2026-01-01"
    else:
        final_freq = current_freq.copy()
        start_date = last_draw_date

    # 4. Integrate New Results
    pending_draws = [d for d in new_draws if d['date'] > start_date]
    print(f"Found {len(pending_draws)} new draws!")
    latest_date = draw['date'] if pending_draws else start_date
    if not pending_draws:
        # Check if current lastUpdate in file is old format (e.g., "March 2026")
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            if not re.search(r'lastUpdate: "\d{4}-\d{2}-\d{2}"', f.read()):
                print("Updating file to reflect exact date format...")
            else:
                print(f"Already up to date. (Last draw: {start_date})")
                return 'no_change'
    for draw in pending_draws:
        for n in draw['nums']:
            num_str = str(n)
            if num_str in final_freq: final_freq[num_str] += 1
        latest_date = draw['date']

    # Recalculate Hot/Cold
    sorted_items = sorted(final_freq.items(), key=lambda x: x[1], reverse=True)
    new_hot = [int(x[0]) for x in sorted_items[:12]]
    new_cold = [int(x[0]) for x in sorted_items[-15:]]

    # Generate new JS content
    now = datetime.now()
    update_str = now.strftime("%Y-%m-%d")
    freq_lines = []
    freq_items = sorted(final_freq.items(), key=lambda x: int(x[0]))
    for i in range(0, 49, 7):
        chunk = freq_items[i:i+7]
        line = "    " + ", ".join([f"{k:>2}: {v}" for k, v in chunk])
        freq_lines.append(line)
    
    new_js = f"""/**
 * Historical frequency data for HK Mark Six
 * Last Updated: {update_str}
 * Primary Source: marksixlotterynumbers.hk (Post-1993)
 * Fallback/Base: nfd.com.tw (1976-Present)
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

// Ball Color Configuration
const BALL_COLORS = {json.dumps(BALL_COLORS, indent=4)};
"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f: f.write(new_js)
    print(f"Successfully updated to {latest_date}")
    return 'updated'

if __name__ == "__main__":
    result = update_data()
    print(f"RESULT:{result}")
