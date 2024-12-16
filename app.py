from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# Global variable to store the latest data
latest_data = {}

# MQTT setup
broker = "test.mosquitto.org"
port = 1883
topic_data = "drone/position"
topic_control = "drone/control"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_data)

def on_message(client, userdata, msg):
    global latest_data
    data = msg.payload.decode()
    # print(f"Received message: {data}")
    latest_data = data

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)

# Start MQTT client in a separate thread
def start_mqtt():
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(latest_data)

@app.route('/control', methods=['POST'])
def control():
    command = request.json.get('command')
    client.publish(topic_control, command)
    print(f"Sent control command: {command}")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)