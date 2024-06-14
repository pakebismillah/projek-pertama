from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)
data_list = []

# Temporary storage for MQTT messages
temp_data = {}

# MQTT settings (change these variables as needed)
MQTT_BROKER = "3cd7aeb7572745878876414c7ff68cf5.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_GAS = "mq2/gas"
MQTT_USERNAME = "punya_musa"
MQTT_PASSWORD = "Bismillah12 "

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_GAS, qos=1)

def on_message(client, userdata, msg):
    global temp_data, data_list
    payload = msg.payload.decode()
    topic = msg.topic
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received message '{payload}' on topic '{topic}'")
    
    if topic == MQTT_TOPIC_GAS:
        temp_data['gas'] = str(payload)
    
    # Store data if gas reading is available
    if 'gas' in temp_data:
        data = {
            'timestamp': timestamp,
            'gas': temp_data['gas']
        }
        data_list.append(data)
        print(f"Appended data: {data}")
        temp_data = {}  # Clear temp_data after storing

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  
client.tls_insecure_set(True)

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

@app.route('/sensor/data', methods=['POST'])
def add_dummy_data():
    try:
        readings = request.json.get('readings')
        print(f"Received readings: {readings}")

        if not readings:
            return jsonify({"error": "Missing 'readings' in request body"}), 400

        for reading in readings:
            gas = reading.get('gas')
            timestamp = reading.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if gas is None:
                return jsonify({"error": "Missing 'gas' in one of the readings"}), 400

            dummy_data = {
                "gas": gas,
                "timestamp": timestamp
            }
            data_list.append(dummy_data)
            print(f"Appended data: {dummy_data}")

        print(f"Final data list: {data_list}")
        return jsonify({"message": "Data added successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Invalid request format"}), 400

@app.route('/sensor/data', methods=['GET'])
def get_data():
    print(f"Data list on GET request: {data_list}")
    return jsonify(data_list), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
