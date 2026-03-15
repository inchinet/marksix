# Mark Six (HK) 香港六合彩 - AI Forecast

A premium web application for generating Hong Kong Mark Six lottery numbers with an integrated AI forecast engine.

![marksix](https://github.com/inchinet/marksix/blob/main/marksix.jpg)

## Features

- **Random Generator**: Generate random numbers based on a custom count (6-49).
- **AI Forecast**: Provides two distinct forecasts:
  - 🔥 **Hot Trend**: Biased towards numbers with higher historical frequency.
  - ⚖️ **Balanced**: A mix of hot trends and overdue "cold" numbers.
- **Dynamic Liquid Glass UI**: A modern, high-end design with glassmorphism effects and smooth animations.
- **Historical Data**: Uses a comprehensive dataset of results continuously updated for AI analysis.
- **Custom Ball Coloring**: Implements precise HK Mark Six color mapping (Red, Blue, Green).
- **One-Click Update**: Integrated background engine with primary source (marksixlotterynumbers.hk) and robust fallback (nfd.com.tw).

## How to Update Data

The application now updates **automatically**.
- Every time you open `marksix.html`, it silently checks for new draws in the background.
- **Scraping Logic**: 
  1. Primary: [marksixlotterynumbers.hk](https://www.marksixlotterynumbers.hk/history/) (Modern results post-1993).
  2. Fallback: [nfd.com.tw](https://www.nfd.com.tw/house/year/2026.htm) (Yearly tables in case of failure).
  3. Base: [nfd.com.tw/house/1976-22.htm](https://www.nfd.com.tw/house/1976-22.htm) (Historical summary initialization).
- If new results are found, the page refreshes once with the latest data.

## File Structure

- `marksix.html`: The main application file with integrated AI engine.
- `marksix_data.js`: External data file containing historical frequencies (auto-managed).
- `sync_data_suggestion.py`: Python scraper for fetching latest results from the web.
- `sync.php`: PHP bridge to trigger the Python sync from the web UI.
- `marksix.jpg`: Background asset.
- `readme.md`: Documentation for the project.
- `.gitignore`: Git configuration for excluding unnecessary files.

## Technical Details

Data is sourced from historical archives including:
- [nfd.com.tw](https://www.nfd.com.tw/house/1976-22.htm)
- [marksixlotterynumbers.hk](https://www.marksixlotterynumbers.hk/history/)

## Recent Changes

| File | Change Description |
| :--- | :--- |
| `marksix.html` | Implemented silent background sync and dynamic ball coloring from data file. |
| `sync.php` | Created PHP bridge to allow browser-to-server command execution. |
| `sync_data_suggestion.py` | Multi-source Scraper (Primary/Fallback) with specialized HK color mapping. |
| `marksix_data.js` | Now includes `BALL_COLORS` config and enhanced frequency metadata. |

## Server Setup & Requirements

### 1. Python Dependencies
The sync script requires `BeautifulSoup4` and `requests`. Check them using:
```bash
python3 -c "import bs4, requests; print('Dependencies OK')"
```
If missing, install via:
```bash
pip3 install beautifulsoup4 requests
```

### 2. File Permissions
For the web-sync to work, the web server needs write access to the data file:
```bash
chmod 666 marksix_data.js
```

## Author

Developed for [github.com/inchinet](https://github.com/inchinet).
