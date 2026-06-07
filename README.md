# osrs-simple-alch

**Simple OSRS High Alchemy desktop tool** built with Grok.  
Displays live Grand Exchange prices and calculates realistic profit using your custom Nature and Fire rune costs. Features a clean table with **Total Profit** and **Total Investment** based on buy limits, smart auto-refresh, and personal hide/favorites system.

> Info displayer only — no botting or game control.

---

## Features

- Live GE prices from the official RuneScape Wiki prices API
- Accurate profit calculation using **your actual Nature and Fire rune costs**
- Choose between Low / High / Average GE price for calculations
- **Total Profit** and **Total Investment** columns based on GE buy limits
- Smart auto-refresh system (fast sync on start, then efficient 60s updates)
- Hide items you don’t want to see + persistent Favorites filter
- Clean, modern dark interface
- Lightweight native Windows desktop app

---

## Screenshots

> *(Screenshots will be added as the app is developed)*

---

## How It Works

The app fetches data from three official APIs:
- `/mapping` — Item information (High Alch value, buy limits, etc.)
- `/latest` — Current GE prices
- `/24h` — 24-hour trading volume

It then calculates profit in real time using the rune costs and price type you define in the Configuration panel.

---

## Installation

### Requirements
- Windows 10/11
- Python 3.10 or higher (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Renom-DEV/osrs-simple-alch.git
   cd osrs-simple-alch
