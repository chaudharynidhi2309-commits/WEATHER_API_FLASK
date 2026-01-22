"""
Weather API Service
Fetches live weather data and stores in PostgreSQL
"""
import os
from flask import Flask, jsonify
from flasgger import Swagger
import requests
from dotenv import load_dotenv
from db_config import db_crud_query, execute_fetch_query

# Load environment variables
load_dotenv()

# Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = os.getenv("WEATHER_API_URL")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 8089))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Initialize Flask app
app = Flask(__name__)
swagger = Swagger(app)


@app.route('/')
def home():
    """Health check endpoint"""
    return "<h1>Weather API is Running!</h1><p>Go to <a href='/apidocs/'>/apidocs/</a></p>"


@app.route('/weather/fetch/<city>', methods=['POST'])
def fetch_live_weather(city):
    """
    Fetch Live Weather and Save to DB
    ---
    parameters:
      - name: city
        in: path
        type: string
        required: true
        description: City name
    responses:
      201:
        description: Weather data successfully fetched and stored
      404:
        description: City not found
      500:
        description: Server error
    """
    try:
        # Fetch weather data from API
        response = requests.get(
            WEATHER_API_URL,
            params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"},
            timeout=10
        )
        
        if response.status_code != 200:
            return jsonify({"error": "City not found"}), 404
        
        # Extract weather data
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']

        # Store in database
        query = "INSERT INTO weather_logs (city_name, temp, humidity) VALUES (%s, %s, %s)"
        result = db_crud_query(query, (city, temp, humidity))
        
        if result is True:
            return jsonify({
                "status": "success",
                "city": city,
                "temp": temp,
                "humidity": humidity
            }), 201
        else:
            return jsonify(result), 500
            
    except requests.RequestException as e:
        return jsonify({"error": "Weather API request failed", "details": str(e)}), 500
    except KeyError as e:
        return jsonify({"error": "Invalid API response format", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route('/weather/history/<city>', methods=['GET'])
def get_weather_history(city):
    """
    Get Weather History for a City
    ---
    parameters:
      - name: city
        in: path
        type: string
        required: true
        description: City name
    responses:
      200:
        description: Weather history retrieved successfully
      404:
        description: No records found
      500:
        description: Database error
    """
    query = """
        SELECT city_name, temp, humidity, recorded_at 
        FROM weather_logs 
        WHERE city_name = %s 
        ORDER BY recorded_at DESC
    """
    data = execute_fetch_query(query, (city,))
    
    if data is None:
        return jsonify({"error": "Database error"}), 500
    
    if not data:
        return jsonify({"message": "No records found", "city": city}), 404
    
    # Format response
    history = [
        {
            "city": row[0],
            "temp": float(row[1]) if row[1] is not None else None,
            "humidity": float(row[2]) if row[2] is not None else None,
            "timestamp": row[3].isoformat() if row[3] else None
        }
        for row in data
    ]
    
    return jsonify({"city": city, "count": len(history), "history": history}), 200


if __name__ == '__main__':
    # Validate required environment variables
    if not WEATHER_API_KEY:
        raise ValueError("WEATHER_API_KEY not found in environment variables")
    
    print(f"🚀 Starting Weather API on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, use_reloader=False)