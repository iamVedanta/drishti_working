from flask import Flask, request, jsonify
from mission import execute_mission

app = Flask(__name__)

@app.route('/start_mission', methods=['POST'])
def start():
    data = request.json
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    print(f"Received coordinates: Latitude = {lat}, Longitude = {lon}")
    return jsonify({"status": "recieved coordinates"}), 200
    try:
        execute_mission(lat, lon)
        return jsonify({"status": "recieved coordinates"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
