import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
CACHE_DIR = "cache"
CACHE_EXPIRY_HOURS = 6  # Mapping rarely changes, so we can cache longer

os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_path(name: str) -> str:
    return os.path.join(CACHE_DIR, f"{name}.json")


def _is_cache_valid(filepath: str, hours: int = CACHE_EXPIRY_HOURS) -> bool:
    if not os.path.exists(filepath):
        return False
    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    return datetime.now() - file_time < timedelta(hours=hours)


def fetch_mapping() -> Optional[Dict]:
    cache_path = _get_cache_path("mapping")

    # Use cache if valid
    if _is_cache_valid(cache_path, hours=24):  # Mapping can be cached longer
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                mapping = {item["id"]: item for item in data}
                return mapping
        except:
            pass

    # Fetch fresh
    try:
        response = requests.get(f"{BASE_URL}/mapping", timeout=15)
        response.raise_for_status()
        data = response.json()

        # Save to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        mapping = {item["id"]: item for item in data}
        return mapping
    except Exception as e:
        print(f"Error fetching mapping: {e}")
        return None


def fetch_latest() -> Optional[Dict]:
    try:
        response = requests.get(f"{BASE_URL}/latest", timeout=10)
        response.raise_for_status()
        return response.json().get("data", {})
    except Exception as e:
        print(f"Error fetching latest: {e}")
        return None


def fetch_24h_volume() -> Optional[Dict]:
    try:
        response = requests.get(f"{BASE_URL}/24h", timeout=10)
        response.raise_for_status()
        return response.json().get("data", {})
    except Exception as e:
        print(f"Error fetching 24h: {e}")
        return None


def get_item_price(latest_data: Dict, item_id: int, price_type: str = "average") -> Optional[int]:
    if not latest_data or str(item_id) not in latest_data:
        return None
    item = latest_data[str(item_id)]
    high = item.get("high")
    low = item.get("low")

    if price_type == "low":
        return low
    elif price_type == "high":
        return high
    else:
        if high and low:
            return (high + low) // 2
        return high or low
    
def fetch_24h_volume() -> Optional[Dict]:
    """Fetch 24h volume data from RuneScape Wiki API"""
    cache_file = os.path.join(CACHE_DIR, "volume_24h.json")

    # Return cached data if still valid
    if _is_cache_valid(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    try:
        response = requests.get("https://prices.runescape.wiki/api/v1/osrs/24h", timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the result
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        return data
    except Exception as e:
        print(f"Error fetching 24h volume: {e}")
        # Return cached data if available (even if expired)
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
def get_item_volume(volume_data: Dict, item_id: int, volume_type: str = "both") -> int:
    """Get volume for an item based on selected type"""
    if not volume_data or "data" not in volume_data:
        return 0

    item_str = str(item_id)
    if item_str not in volume_data["data"]:
        return 0

    item = volume_data["data"][item_str]

    if volume_type == "low":
        return item.get("lowPriceVolume", 0) or 0
    elif volume_type == "high":
        return item.get("highPriceVolume", 0) or 0
    else:  # both
        low = item.get("lowPriceVolume", 0) or 0
        high = item.get("highPriceVolume", 0) or 0
        return low + high