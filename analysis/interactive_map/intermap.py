from flask import Flask, render_template, request, redirect, url_for, jsonify
import folium
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Initial map centered in the US
    start_coords = (37.7749, -122.4194)  # Example: San Francisco, USA
    folium_map = folium.Map(location=start_coords, zoom_start=4)

    # Add a clickable map layer
    folium_map.add_child(folium.LatLngPopup())

    # Save map as an HTML file
    folium_map.save('templates/map.html')
    
    return render_template('index.html')

@app.route('/save_location', methods=['POST'])
def save_location():
    lat = request.json.get('lat')
    lon = request.json.get('lon')
    user_id = request.json.get('user_id')  # Obtain user ID in some way

    # Save location to the database (Example)
    # Here you can add database logic to store the lat, lon for the user
    # Example SQL: INSERT INTO User_Location (User_ID, Latitude, Longitude) VALUES (user_id, lat, lon)

    return jsonify({"status": "Location saved successfully!", "lat": lat, "lon": lon})

if __name__ == '__main__':
    app.run(debug=True)
