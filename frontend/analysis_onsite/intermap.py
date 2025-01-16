from flask import Flask, render_template, request, redirect, url_for
import folium

app = Flask(__name__)

@app.route('/')
def index():
    # Initial map centered at a default location (e.g., San Francisco)
    start_coords = (37.7749, -122.4194)
    folium_map = folium.Map(location=start_coords, zoom_start=4)

    # Add click event to get coordinates
    folium_map.add_child(folium.LatLngPopup())  # Allows user to click and see coordinates

    # Save the map as an HTML file
    folium_map.save('templates/map.html')
    
    return render_template('index.html')

@app.route('/select_location', methods=['POST'])
def select_location():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    
    return render_template('confirm_location.html', lat=lat, lon=lon)

@app.route('/save_location', methods=['POST'])
def save_location():
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    user_id = request.form.get('user_id')  # Replace with actual logic to retrieve user ID

    # Here you would add the code to save lat, lon, and user_id to your database
    # Example SQL: INSERT INTO User_Location (User_ID, Latitude, Longitude) VALUES (user_id, lat, lon)

    return "Location saved successfully!"

if __name__ == '__main__':
    app.run(debug=True)

