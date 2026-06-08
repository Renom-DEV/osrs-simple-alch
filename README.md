# OSRS Simple Alch

**Simple OSRS High Alchemy desktop tool** built with Grok.  
Displays live Grand Exchange prices and calculates realistic profit using your custom Nature and Fire rune costs. Features a clean table with **Total Profit** and **Total Investment** based on buy limits, smart auto-refresh, and personal hide/favorites system.

> Info displayer only — no botting or game control.

## Features

### Core Functionality
- Live GE prices from the official RuneScape Wiki prices API
- Accurate profit calculation using your actual Nature and Fire rune costs
- Choose between Low / High / Average GE price for calculations
- Total Profit and Total Investment columns based on GE buy limits
- Smart auto-refresh system (fast sync on startup, then efficient 60s updates)
- Clean, modern dark interface
- Lightweight native Windows desktop app

### Search & Navigation
- Real-time search bar with instant filtering
- Pagination with adjustable items per page (50/100/150)
- Manual page input
- Global column sorting (click any header)

### Personalization
- Favorites system — Right-click any item to mark/unmark as favorite
- Hide items — Right-click to hide items you don’t want to see
- Hide Members toggle — Quickly filter out member-only items
- "Favorites Only" filter
- "Show Hidden" button (permanently unhides items)
- "Clear All Favorites" button

### Smart Features
- Background auto-refresh every 60 seconds
- Smart fast sync on startup — Quickly polls for latest prices (1s intervals up to 60s)
- Loading spinner animation during fast sync
- "Sync failed" message shown after timeout (auto-clears after 3 seconds)
- Persistent storage — Favorites, hidden items, and settings are saved locally in config.json

### Configuration
- Easy-to-use settings window that stays open after saving
- Live table updates when changing settings
- Shows current API prices for Nature and Fire runes
- Per-field save buttons for rune prices

## How It Works

The app fetches data from three official APIs:
- /mapping — Item information (High Alch value, buy limits, etc.)
- /latest — Current GE prices
- /24h — 24-hour trading volume

It then calculates profit in real time using the rune costs and price type you define in the Configuration panel.

## Installation

### Requirements
- Windows 10/11
- Python 3.10 or higher (recommended)

### Setup

1. Clone the repository:
   git clone https://github.com/Renom-DEV/osrs-simple-alch.git
   cd osrs-simple-alch

2. Create a virtual environment:
   python -m venv venv

3. Activate the virtual environment:

   Windows:
   venv\Scripts\activate

   macOS / Linux:
   source venv/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

5. Run the app:
   python main.py

## Usage

1. Launch the app.
2. Open Configuration (⚙ button).
3. Set your Nature Rune and Fire Rune costs (leave empty to use live API prices).
4. Choose your preferred GE Price type (Low / High / Average).
5. The table will automatically update with accurate profit numbers.

You can hide items you don’t like and mark favorites for quick filtering.

## Configuration Explained

### Rune Costs
- Nature Rune Price: Your actual cost per nature rune.
- Fire Rune Method:
  - Use Fire Staff / Tome of Fire → 0 gp cost
  - Pay for Fire Runes → Set your fire rune cost

### Price Settings
- Choose which GE price to use for calculations:
  - Low
  - High
  - Average (recommended)

### Auto-Refresh
- Smart sync mode on startup (polls every second until update is found)
- Then switches to efficient 60-second updates
- Can be completely disabled if desired

## Data Sources

All data comes from the official RuneScape Wiki prices API:
- Mapping: https://prices.runescape.wiki/api/v1/osrs/mapping
- Latest: https://prices.runescape.wiki/api/v1/osrs/latest
- 24h Volume: https://prices.runescape.wiki/api/v1/osrs/24h

## Tech Stack

- Python 3
- customtkinter — Modern dark GUI
- requests — API communication

## Development

This project is being developed iteratively with assistance from Grok.

### Current Status
The project is in active development. Core features are complete and functional.

### Versioning
We use semantic versioning and GitHub Releases. Each stable milestone will have a release with changelogs.

## Contributing

This is an open source project built collaboratively between a human developer and AI (Grok).

Contributions, suggestions, bug reports, and forks are very welcome!

You can:
- Open issues
- Submit pull requests
- Suggest new features
- Improve the code or documentation

Even small improvements are appreciated.

## Credits

- Developed by: Renom-DEV (Jesús Javier)
- Built with assistance from: Grok (xAI)
- Data provided by: RuneScape Wiki Prices API

## License

This project is licensed under the MIT License — see the LICENSE file for details.

This means you are free to:
- Use the project commercially or privately
- Modify it
- Distribute it
- Fork it

As long as you include the original license and copyright notice.

---

*Last updated: June 2026*