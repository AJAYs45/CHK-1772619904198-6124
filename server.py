from fastapi import FastAPI, Request
from pydantic import BaseModel
import joblib
import numpy as np
import csv
from datetime import datetime
import uvicorn
import os
import json
import socket

app = FastAPI(title="SOC Admin Server")

model = joblib.load('anomaly_model.pkl')

with open('traffic_log.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Time', 'Source_IP', 'User_Name', 'Prediction', 'Status', 'Country', 'Lat', 'Lon'])

if not os.path.exists('blocklist.json'):
    with open('blocklist.json', 'w') as f: json.dump([], f)

class NetworkPacket(BaseModel):
    features: list
    source_ip: str
    country: str
    lat: float
    lon: float

@app.post("/predict")
def predict_traffic(packet: NetworkPacket, request: Request):
    client_ip = packet.source_ip
    
    try:
        user_name = socket.gethostbyaddr(request.client.host)[0]
    except Exception:
        user_name = "Unknown-Device"

    # 🌟 JSON फाईल रिकामी असली तरी एरर न येण्यासाठी नवीन बदल
    try:
        with open('blocklist.json', 'r') as f:
            blocklist = json.load(f)
    except Exception:
        blocklist = []  # जर फाईल रिकामी असेल, तर लिस्ट रिकामी घ्या

    if client_ip in blocklist:
        print(f"🛑 BLOCKED CONNECTION from {packet.country} ({client_ip})")
        return {"status": "❌ CONNECTION REFUSED: Firewall Blocked your IP"}

    data = np.array(packet.features).reshape(1, -1)
    prediction = int(model.predict(data)[0])
    status = "Attack 🚨" if prediction == 1 else "Safe ✅"
    
    with open('traffic_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%H:%M:%S"), client_ip, user_name, prediction, status, packet.country, packet.lat, packet.lon])
        
    return {"status": status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)