from flask import Flask, request, jsonify
from flasgger import Swagger
import requests
from db_config import db_crud_query, execute_fetch_query

# --- STEP 1: DEFINE THE APP ---
app = Flask(__name__)
swagger = Swagger(app)

# --- STEP 2: YOUR ROUTES ---

@app.route('/')
def home():
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
    responses:
      201:
        description: Live data fetched and saved to PostgreSQL
      404:
        description: City not found
      500:
        description: Server error
    """
    api_key = "cf208e64d5db66f1449c91db8b3de455"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "City not found"}), 404
        
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']

        # Use your db_crud_query function
        insert_query = "INSERT INTO weather_logs (city_name, temp, humidity) VALUES (%s, %s, %s)"
        result = db_crud_query(insert_query, (city, temp, humidity))
        
        if result is True:
            return jsonify({
                "status": "Success", 
                "city": city, 
                "temp": temp,
                "humidity": humidity
            }), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": str(e), "status": "Failed"}), 500

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
    responses:
      200:
        description: Weather history retrieved successfully
    """
    fetch_query = "SELECT city_name, temp, humidity, created_at FROM weather_logs WHERE city_name = %s ORDER BY created_at DESC"
    data = execute_fetch_query(fetch_query, (city,))
    
    if data is None:
        return jsonify({"error": "Database error"}), 500
    
    if not data:
        return jsonify({"message": "No records found", "city": city}), 404
    
    result = []
    for row in data:
        result.append({
            "city": row[0],
            "temp": row[1],
            "humidity": row[2],
            "timestamp": str(row[3])
        })
    
    return jsonify({"city": city, "history": result}), 200

# --- STEP 3: RUN THE APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=False, use_reloader=False)