# OSRS Simple Alch

**Simple OSRS High Alchemy desktop tool** built with Grok.  
Displays live Grand Exchange prices and calculates realistic profit using your custom Nature and Fire rune costs. Features a clean table with **Total Profit** and **Total Investment** based on buy limits, smart auto-refresh, and personal hide/favorites system.

> Info displayer only — no botting or game control.

## Features

- Live GE prices from the official RuneScape Wiki prices API
- Accurate profit calculation using **your actual Nature and Fire rune costs**
- Choose between Low / High / Average GE price for calculations
- **Total Profit** and **Total Investment** columns based on GE buy limits
- Smart auto-refresh system（fast sync on start, then efficient 60s updates）
- Hide items you don’t want to see + persistent Favorites filter
- Clean, modern dark interface
- Lightweight native Windows desktop app

## Screenshots

> *(Screenshots will be added as the app is developed)*

## How It Works

The app fetches data from three official APIs:
- `/mapping` — Item information (High Alch value, buy limits, etc.)
- `/latest` — Current GE prices
- `/24h` — 24-hour trading volume

It then calculates profit in real time using the rune costs and price type you define in the Configuration panel.

## Installation

### Requirements
- Windows 10/11
- Python 3.10 or higher (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Renom-DEV/osrs-simple-alch.git
   cd osrs-simple-alch
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   **Windows:**
   ```powershell
   venv\Scripts\activate
   ```

   **macOS / Linux:**
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the app:
   ```bash
   python main.py
   ```

> A packaged `.exe` version will be available in future releases.

## Usage

1. Launch the app.
2. Open **Configuration** (⚙ button).
3. Set your **Nature Rune** and **Fire Rune** costs (leave empty to use live API prices).
4. Choose your preferred **GE Price type** (Low / High / Average).
5. The table will automatically update with accurate profit numbers.

You can hide items you don’t like and mark favorites for quick filtering.

## Configuration Explained

### Rune Costs
- **Nature Rune Price**: Your actual cost per nature rune.
- **Fire Rune Method**:
  - Use Fire Staff / Tome of Fire → 0 gp cost
  - Pay for Fire Runes → Set your fire rune cost

### Price Settings
- Choose which GE price to use for calculations:
  - **Low**
  - **High**
  - **Average** (recommended)

### Auto-Refresh
- Smart sync mode on startup (polls every second until update is found)
- Then switches to efficient 60-second updates
- Can be completely disabled if desired

## Data Sources

All data comes from the official RuneScape Wiki prices API:
- [Mapping](https://prices.runescape.wiki/api/v1/osrs/mapping)
- [Latest](https://prices.runescape.wiki/api/v1/osrs/latest)
- [24h Volume](https://prices.runescape.wiki/api/v1/osrs/24h)

## Tech Stack

- **Python 3**
- **customtkinter** — Modern dark GUI
- **requests** — API communication
- **threading** — Background price updates
- **PyInstaller** (future) — Single `.exe` packaging

## Development

This project is being developed iteratively with assistance from **Grok**.

### Current Status
The project is in early development. Core features are being built step by step.

### Versioning
We use semantic versioning and GitHub Releases. Each stable milestone will have a release with changelogs.

## Contributing

This is currently a personal project. Suggestions and feedback are welcome through issues.

## Credits

- Built with assistance from **Grok** (xAI)
- Developed by **Renom-DEV** (Jesús Javier)
- Data provided by the [RuneScape Wiki](https://oldschool.runescape.wiki/) prices API

## License

This project is currently unlicensed. All rights reserved.

---

*Last updated: June 2026*

---
