import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import datetime
import os

# API key and list of cities
API_KEY = "cecf7776233af023cfa30b3d941c4019"
CITY = ["Faridabad", "Jammu and kashmir", "Delhi", "Punjab", "Himachal Pradesh", "Rajasthan", "WRONG"]
JSON_FILE = "Weather File.txt"

# ------------------------
# Function to fetch weather
# ------------------------
def fetch_weather(city):
    """
    Makes a request to OpenWeatherMap API and returns a dictionary:
    - If success: {"error": False, "data": {...}}
    - If error: {"error": True, "status": ..., "message": ...}
    """
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "en"}

    try:
        response = requests.get(weather_url, params=params)
        data = response.json()

        # HTTP error (city not found, wrong API key, etc.)
        if response.status_code >= 400:
            return {"error": True, "status": response.status_code, "message": data.get("message", "unknown error")}

        # Success
        return {"error": False, "data": data}

    except requests.exceptions.RequestException as e:
        # Network errors or connection issues
        return {"error": True, "status": None, "message": str(e)}


# ------------------------
# Main execution with threads
# ------------------------
Results = []
timestamp = datetime.datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_weather, city): city for city in CITY}

    for future in as_completed(futures):
        city = futures[future]
        data = future.result()

        if data["error"]:
            print(f"Error for {city}: {data['message'].capitalize()}")
            Results.append({
                "city": city,
                "temp": "-",
                "humidity": "-",
                "description": "-",
                "country": "-",
                "status": "ERROR",
                "message": f"{city} not found"
            })
        else:
            weather_json = data["data"]
            city_name = weather_json.get("name", "N/A")
            temp = weather_json.get("main", {}).get("temp", "N/A")
            humidity = weather_json.get("main", {}).get("humidity", "N/A")
            description = weather_json.get("weather", [{}])[0].get("description", "N/A")
            country = weather_json.get("sys", {}).get("country", "N/A")

            print(f"{city_name} : {temp}°C, {humidity}%, {description}, {country}")

            Results.append({
                "city": city_name,
                "temp": f"{temp} °C",
                "humidity": f"{humidity} %",
                "description": description,
                "country": country,
                "status": "OK"
            })


# ------------------------
# Print results in a table
# ------------------------
print(f"\nTimestamp: {timestamp}")
print(f"{'CITY':<20} {'Temperature':<12} {'Humidity':<10} {'Description':<20} {'Country':<8} {'Status':<8}")
print("-" * 90)
for result in Results:
    print(
        f"{result['city']:<20} {result['temp']:<12} {result['humidity']:<10} "
        f"{result['description']:<20} {result['country']:<8} {result['status']:<8}"
    )


# ------------------------
# Save results to JSON (append log style)
# ------------------------
log_entry = {
    "timestamp": timestamp,
    "results": Results
}

# If file exists, load old data, else create new list
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            old_data = json.load(f)
        except json.JSONDecodeError:
            old_data = []
else:
    old_data = []

old_data.append(log_entry)

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(old_data, f, ensure_ascii=False, indent=4)

print(f"\nResults saved to {JSON_FILE}")
