"""
dummy mqtt script

datum 18-9-2023

gemaakt door fabian


let op nog auto reconnect nodig als bijvoorbeeld wifi uitvalt nog niet ingebouwd maar dan hebben we alvast wat

ook mqtt ontvangen nog niet ingebouwd komt later

"""





import random
import time

from paho.mqtt import client as mqtt_client


broker = '192.168.1.124'   # broker ip adress 
port = 1883
topic_temperature = "vf/pico_0/temperature"     
topic_humidity = "vf/pico_0/humidity"
topic_air = "vf/pico_0/air"

sleep_interval = 10   # hoeveel keer berichten


client_id = "pico_0"



def get_dummy_temp():
    temp = random.uniform(-10,100)
    return temp

def get_dummy_hum():
    hum = random.uniform(0,100)
    return hum
    
def get_dummy_air():
    air = random.uniform(0,1023)
    return air


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


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
       
        


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()
