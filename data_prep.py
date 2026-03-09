import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# 1. Column names and Data Loading (Your old code)
columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
           'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
           'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count',
           'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
           'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
           'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
           'dst_host_srv_rerror_rate', 'attack_type', 'difficulty_level']

print("Loading data...")
train_data = pd.read_csv("KDDTrain+.txt", names=columns)

# 2. Preprocessing (Your old code)
categorical_columns = ['protocol_type', 'service', 'flag']
le = LabelEncoder()
for col in categorical_columns:
    train_data[col] = le.fit_transform(train_data[col])

train_data['label'] = train_data['attack_type'].apply(lambda x: 0 if x == 'normal' else 1)
train_data = train_data.drop(['attack_type', 'difficulty_level'], axis=1)

# ---------------- New AI Training Code ---------------- #

print("AI Model training has started... (This might take a few seconds)")

# 3. Separating X (Features) and Y (Target)
X = train_data.drop('label', axis=1) # AI will learn from this
y = train_data['label']              # AI needs to predict this (0 = Safe, 1 = Threat/Attack)

# 4. Splitting Data: 80% for Training and 20% for Testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Creating and Training the Random Forest Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Testing the Model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"✅ Model training complete! Accuracy: {accuracy * 100:.2f}%")

# 7. Saving the trained model for the Dashboard
joblib.dump(model, 'anomaly_model.pkl')
print("📁 Model saved as 'anomaly_model.pkl'!")

# ---------------- Checking how the model works (Testing) ---------------- #

print("\n--- 🔍 Let's see how the model actually works ---")

# Let's take the first 5 network packets from X_test (Testing Data)
test_packets = X_test.head(5)
actual_labels = y_test.head(5).values

# Let's ask the model if these 5 packets are Safe or Threats
real_predictions = model.predict(test_packets)

for i in range(5):
    # 0 means Normal, 1 means Attack
    actual = "Threat (Attack) 🚨" if actual_labels[i] == 1 else "Safe (Normal) ✅"
    predicted = "Threat (Attack) 🚨" if real_predictions[i] == 1 else "Safe (Normal) ✅"
    
    print(f"\n📦 Network Packet {i+1}:")
    print(f"  > Actual Type      : {actual}")
    print(f"  > AI Prediction    : {predicted}")
    
    if actual == predicted:
        print("  🟢 Conclusion: AI predicted perfectly!")
    else:
        print("  🔴 Conclusion: AI made a mistake.")
print("-" * 50)