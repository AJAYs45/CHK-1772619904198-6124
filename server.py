from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import csv
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="Network Anomaly Detection Server")

# AI मॉडेल लोड करणे
print("Loading AI Model...")
model = joblib.load('anomaly_model.pkl')
print("Model Loaded Successfully!")

# सर्व्हर चालू झाल्यावर एक नवीन कोरी लॉग फाईल बनवणे
with open('traffic_log.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Time', 'Prediction', 'Status'])

# लॅपटॉप १ कडून येणाऱ्या डेटाचे स्वरूप
class NetworkPacket(BaseModel):
    features: list

# डेटा स्वीकारण्यासाठी API
@app.post("/predict")
def predict_traffic(packet: NetworkPacket):
    # आलेला डेटा AI ला देणे
    data = np.array(packet.features).reshape(1, -1)
    prediction = model.predict(data)[0]
    
    status = "Attack 🚨" if prediction == 1 else "Safe ✅"
    
    # आलेला रिझल्ट फाईलमध्ये सेव्ह करणे (जेणेकरून डॅशबोर्डला दिसेल)
    with open('traffic_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%H:%M:%S"), int(prediction), status])
        
    return {"status": status}

if __name__ == "__main__":
    # 0.0.0.0 मुळे नेटवर्कमधला दुसरा लॅपटॉप याला कनेक्ट होऊ शकेल
    uvicorn.run(app, host="0.0.0.0", port=8000)