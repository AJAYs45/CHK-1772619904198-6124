from fastapi import FastAPI, Request
from pydantic import BaseModel
import joblib
import numpy as np
import csv
from datetime import datetime
import uvicorn
import os
import json
import socket  # 🌟 ही नवीन लायब्ररी PC चे नाव शोधेल

app = FastAPI(title="SOC Admin Server")

model = joblib.load('anomaly_model.pkl')

# सर्व्हर चालू झाल्यावर नवीन लॉग फाईल बनवणे
with open('traffic_log.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Time', 'Source_IP', 'User_Name', 'Prediction', 'Status'])

if not os.path.exists('blocklist.json'):
    with open('blocklist.json', 'w') as f:
        json.dump([], f)

# 🌟 आता Attacker कडून फक्त 'features' (डेटा) घेतला जाईल, नाव नाही.
class NetworkPacket(BaseModel):
    features: list

@app.post("/predict")
def predict_traffic(packet: NetworkPacket, request: Request):
    # 🌟 १. सर्व्हर स्वतःहून Attacker चा खरा IP शोधेल
    client_ip = request.client.host
    
    # 🌟 २. त्या IP वरून Attacker च्या PC चे खरे नाव शोधेल
    try:
        user_name = socket.gethostbyaddr(client_ip)[0]
    except Exception:
        # जर नाव शोधता आले नाही, तर 'Unknown-Device' नाव देईल
        user_name = "Unknown-Device"

    # ॲडमिनने हा IP ब्लॉक केला आहे का ते तपासणे
    with open('blocklist.json', 'r') as f:
        blocklist = json.load(f)

    if client_ip in blocklist:
        print(f"🛑 BLOCKED CONNECTION: {user_name} ({client_ip}) tried to attack!")
        return {"status": "❌ CONNECTION REFUSED: Firewall Blocked your IP"}

    # जर ब्लॉक नसेल, तर AI ला तपासणीसाठी देणे
    data = np.array(packet.features).reshape(1, -1)
    prediction = int(model.predict(data)[0])
    
    status = "Attack 🚨" if prediction == 1 else "Safe ✅"
    
    # रिझल्ट फाईलमध्ये सेव्ह करणे
    with open('traffic_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%H:%M:%S"), client_ip, user_name, prediction, status])
        
    return {"status": status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)