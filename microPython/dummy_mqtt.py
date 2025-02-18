"""
dummy mqtt script

datum 19-02-2025

gemaakt door fabian
Update Senna

let op nog auto reconnect nodig als bijvoorbeeld wifi uitvalt nog niet ingebouwd maar dan hebben we alvast wat

ook mqtt ontvangen nog niet ingebouwd komt later

"""

import random
import time

import paho.mqtt.client as mqtt


broker = '192.168.1.201'   # broker ip adress 
port = 1883
topic_temperature = "vf/pico_0/sensor/dht22/temp"     
topic_humidity = "vf/pico_0/sensor/dht22/humidity"
topic_air = "vf/pico_0/sensor/mq135"

sleep_interval = 10   # hoeveel keer berichten


CLIENT_ID = "pico_0"



def get_dummy_temp():
    temp = random.randint(0,40)
    return temp

def get_dummy_hum():
    hum = random.randint(0,40)
    return hum
    
def get_dummy_air():
    air = random.randint(0,40)
    return air

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def publish(client):
    while True:
        time.sleep(sleep_interval)
        temperature = get_dummy_temp()
        humidity = get_dummy_hum()
        air = get_dummy_air()
        client.publish(topic_temperature, temperature)
        print("published temp : ", temperature)
        client.publish(topic_humidity, humidity)
        print("published humidity : ", humidity)
        client.publish(topic_air, air)
        print("published air : ", air)
       
        

mqttc = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

mqttc.on_connect = on_connect
mqttc.on_message = on_message
def run():
    mqttc.connect(broker, port, 60)
    while True:
        publish(mqttc)
    mqttc.loop_stop()

if __name__ == '__main__':
    run()





# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# mqttc.loop_forever()


