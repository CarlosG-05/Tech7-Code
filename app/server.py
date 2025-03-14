import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime
from collections import deque
import numpy as np

# MQTT Broker settings
#BROKER = "broker.hivemq.com"
BROKER = "broker.emqx.io"
#BROKER = "test.mosca.io"
PORT = 1883
#BASE_TOPIC = "carlos/ece140/sensors"
BASE_TOPIC = "allsensors"
TOPIC = BASE_TOPIC + "/#"

"""
if BASE_TOPIC == "carlos/ece140/sensors":
    print("Carlos Server")
    exit()
"""

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Successfully connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to {TOPIC}")
    else:
        print(f"Failed to connect with result code {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received."""
    try:
        # Parse JSON message
        payload = json.loads(msg.payload.decode())
        print(payload)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ensure message is from the expected topic
        #if msg.topic == BASE_TOPIC + "/#":
        ##temp = payload.get("temperature", "N/A")
        ##pressure = payload.get("pressure", "N/A")

        ##print(f"[{current_time}] Received sensor data: Temperature = {temp}, Pressure = {pressure} from {msg.topic}")
        #else:
        #    print(f"Ignoring message from topic: {msg.topic}")
        post(payload)

    except json.JSONDecodeError:
        print(f"\nReceived non-JSON message on {msg.topic}:")
        print(f"Payload: {msg.payload.decode()}")

def main():
    """Main function to set up MQTT client."""
    client = mqtt.Client()

    # Set callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to the MQTT broker
        print("Connecting to MQTT broker...")
        client.connect(BROKER, PORT, 60)

        # Start the MQTT loop to process messages
        print("Starting MQTT loop...")
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nDisconnecting from broker...")
        client.disconnect()
        print("Exited successfully")
    except Exception as e:
        print(f"Error: {e}")

    client.loop();

def post(data: dict):
    try:
        response = requests.post("http://localhost:8000/dashboard/data", json=data)
        response.raise_for_status()
        print(f"Data Sent: {data}")

    except requests.exceptions.RequestException as e:
        print(f"Error Sending Data: {e}")


if __name__ == "__main__":
    main()