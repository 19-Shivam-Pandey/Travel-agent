import json
import math
import requests
from typing import List, Dict, Any
from langchain.tools import tool
from ddgs import DDGS

HEADERS = {
    "User-Agent": "travel-agent/1.0"
}

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for travel information like attractions, transport ideas,
    neighborhood suggestions, or local food recommendations.
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title"),
                "href": r.get("href"),
                "body": r.get("body"),
            })
    return json.dumps(results, ensure_ascii=False, indent=2)


@tool
def geocode_city(city: str) -> str:
    """
    Convert a city name into latitude and longitude using Open-Meteo geocoding.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("results"):
        return json.dumps({"error": f"No coordinates found for {city}"})

    place = data["results"][0]
    return json.dumps({
        "name": place.get("name"),
        "country": place.get("country"),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "timezone": place.get("timezone")
    }, ensure_ascii=False, indent=2)


@tool
def get_weather(city: str) -> str:
    """
    Get current + forecast weather for a city using Open-Meteo.
    First geocodes the city, then fetches forecast.
    """
    geo = json.loads(geocode_city.invoke({"city": city}))
    if "error" in geo:
        return json.dumps(geo)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "forecast_days": 5,
        "timezone": "auto"
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    return json.dumps({
        "location": geo,
        "current": data.get("current", {}),
        "daily": data.get("daily", {})
    }, ensure_ascii=False, indent=2)


@tool
def estimate_budget(days: int, daily_hotel: float, daily_food: float, daily_transport: float, activities_total: float = 0.0) -> str:
    """
    Estimate trip budget from simple numeric assumptions.
    """
    total = (days * daily_hotel) + (days * daily_food) + (days * daily_transport) + activities_total
    breakdown = {
        "hotel_total": round(days * daily_hotel, 2),
        "food_total": round(days * daily_food, 2),
        "transport_total": round(days * daily_transport, 2),
        "activities_total": round(activities_total, 2),
        "grand_total": round(total, 2)
    }
    return json.dumps(breakdown, ensure_ascii=False, indent=2)