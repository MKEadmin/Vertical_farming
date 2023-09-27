import dht
from machine import Pin, ADC
import time
import ubinascii
from umqtt.simple import MQTTClient
import boot 


do_connect('ssid','passwd')

connected = False


MQTT_BROKER = "192.168.1.10"
MQTT_TOPIC_TEMP_HUMIDITY = "vf/pico_0/sensor/dht22"
MQTT_TOPIC_GAS = "vf/pico_0/sensor/mq135"
MQTT_TOPIC_RELAY_PREFIX = "vf/pico_0/relay/"

sleep_interval = 2 

# DHT22-aansluiting (GPIO-pin 2)
dht_sensor = dht.DHT11(Pin(2))

# MQ135-aansluiting (analoge pin 26)
mq135_sensor = ADC(Pin(26))

# Relais-aansluitingen
relay_pins = [Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT), Pin(6, Pin.OUT)]

# MQTT-clientconfiguratie
mqtt_client = MQTTClient("pico_client", MQTT_BROKER, keepalive=60)
def connect_mqtt():
    
    mqtt_client.connect()
    mqtt_client.set_callback(on_message)
    mqtt_client.subscribe(MQTT_TOPIC_RELAY_PREFIX + "#")
    time.sleep(1)
    print("connected")

def read_dht22():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

def read_gas_sensor():
    return mq135_sensor.read_u16()

def toggle_relay(relay_number, status):
    relay_pins[relay_number].value(status)

def on_message(topic, msg):
    print("Ontvangen bericht - Topic: ", topic, ", Bericht: ", msg)
    try:
        if topic.startswith(MQTT_TOPIC_RELAY_PREFIX):
            relay_number = topic.decode()
            relay_number = relay_number.split("/")[-2]
            print(relay_number)
            relay_status = int(msg.decode())
            print(relay_status)
            
            toggle_relay(int(relay_number), relay_status)
            print("toggeled : ", relay_number, " ", relay_status)
    except Exception as e:
        print("error ", e)

            
    



while True:
    try:
        if connected == False :
            connect_mqtt()
            connected = True

        # Lees de DHT22-sensorgegevens
        temperature, humidity = read_dht22()
        print("temperature : ", temperature , " humidity : ", humidity)

        # Publiceer DHT22-gegevens naar MQTT
        mqtt_client.publish(MQTT_TOPIC_TEMP_HUMIDITY, '{"temperature":' + str(temperature) + ', "humidity":' + str(humidity) + '}')

        # Lees de MQ135-gassensorgegevens
        gas_value = read_gas_sensor()
        print("gas : ", gas_value)

        # Publiceer MQ135-gegevens naar MQTT
        mqtt_client.publish(MQTT_TOPIC_GAS, str(gas_value))

        mqtt_client.check_msg()
        time.sleep(sleep_interval)
    except:
        
        print("reconnecting")
        do_connect('Geendraad','NEUSh00rn!')
        connected = False
        
    
    
