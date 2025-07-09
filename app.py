from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/prices")
def prices():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd")
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "bitcoin": data.get("bitcoin", {}).get("usd", "Error"),
            "ethereum": data.get("ethereum", {}).get("usd", "Error")
        })
    except Exception as e:
        print("Error fetching prices:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = request.get_json()
        with open("settings.json", "w") as f:
            json.dump(data, f)
        return jsonify({"message": "Settings updated."})
    else:
        if os.path.exists("settings.json"):
            with open("settings.json") as f:
                return jsonify(json.load(f))
        return jsonify({})

if __name__ == "__main__":
    app.run(debug=True)
