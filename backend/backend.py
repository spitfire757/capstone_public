from flask import Flask, request, jsonify
from test_transfer import test
import subprocess
from generate_user_maps import create_user_models
from predict_and_plot import predict_and_plot
from surrounding_data import grab_data
# from plot_terrain import plot_terrain

app = Flask(__name__)


@app.route('/forecast', methods=['POST'])
def handle_forecast_request():
    try:
        # try to get json data
        data = request.json
        if not data:
            return jsonify({'status': error, "message": 'No data provided'}), 400
        # If data exists 
        user_id = data.get('user_id')
        lat = data.get('latitude')
        lon = data.get('longitude')
        param = data.get('parameter')
        # Make sure all fields are revieved
        if not all([user_id, lat, lon, param]):
            return jsonify({
                'status' : 'error',
                'message': 'Not all fields recieved',
                }), 400
        # Here is where the shell script and ML algo will go, placeholder for now
        # This will be a test process for the file transfering
        result, path = test(user_id, lat, lon, param)
        # arr, points = create_user_models(user_id, lat, lon, param)
        # path = predict_and_plot(user_ID, filt, arr, points, '/Users/brendankelley/Desktop/All/NEW_FINAL_OFFSITE/school_2024_2025/main/data', lat, lon)
        arr, points = create_user_models(user_id, lat, lon, param)
        path = predict_and_plot(user_id, param, arr, points, '/Users/brendankelley/Desktop/All/NEW_FINAL_OFFSITE/school_2024_2025/main/data', lat, lon)
        # terr = plot_terrain(user_id, points, '/Users/brendankelley/Desktop/All/NEW_FINAL_OFFSITE/school_2024_2025/main/data')


        if result:
            forecast_result = result
            script_path = "/Users/brendankelley/Desktop/All/NEW_FINAL_OFFSITE/school_2024_2025/445Cap/for_server/rpi/transfer_files.sh"
            command = ['sudo', script_path, str(user_id), str(lat), str(lon), str(param)]

            try:
                # Execute the script
                # print(command)
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print("Script output:\n", result.stdout)
            except subprocess.CalledProcessError as e:
                print("FAILED TRANSFER")
                print(e)
                print("Error executing script:\n", e.stderr)
        # forecast_result = f"Forecast for param {param} at {lat}, {lon} for user {user_id}"
        # print(forecast_result)
        return jsonify({
            "status" : "YIPEE",
            "message" : "Data recieved and forecast is being generated",
            "forecast_result" : forecast_result
            }), 200
    except Exception as e:
        return jsonify({
            'status' : 'error',
            'message' : str(e)
            }), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')

