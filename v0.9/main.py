import dht
from machine import Pin, ADC
import time
import ubinascii
from umqtt.simple import MQTTClient
import boot 

wifi_started = False
reset_pin = 7
checked_reset = 0
reset = Pin(reset_pin, Pin.IN,Pin.PULL_DOWN)

MQTT_BROKER = "192.168.1.10"
MQTT_TOPIC_TEMP_HUMIDITY = "vf/pico_0/sensor/dht22"
MQTT_TOPIC_GAS = "vf/pico_0/sensor/mq135"
MQTT_TOPIC_RELAY_PREFIX = "vf/pico_0/relay/"
mqtt_client = MQTTClient("pico_client", MQTT_BROKER, keepalive=60)

sleep_interval_mqtt = 1 # sleep intervall for mqtt if set to high the relay state takes longer to update

sleep_interval_sensor_readings = 20  # sleep interval for sensor reading and how long it takes to publish to mqtt each time

max_ticks = sleep_interval_sensor_readings / sleep_interval_mqtt # calculate ticks

current_amount_tick = 0

dht_sensor = dht.DHT11(Pin(2)) # DHT22-aansluiting (GPIO-pin 2)

# MQ135-aansluiting (analoge pin 26)
mq135_sensor = ADC(Pin(26))

# Relais-aansluitingen
relay_pins = [Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT), Pin(6, Pin.OUT)]


wifi_pin = 9
ap_pin = 10
wifi_led = Pin(wifi_pin, Pin.OUT)
ap_led = Pin(ap_pin, Pin.OUT)
wifi_led.value(0)
ap_led.value(0)


if reset.value() == 1:
    print("ap activated")
    write_config("ap", "", "")
    ap_led.value(1)
    checked_reset = 1
elif reset.value() == 0:
    checked_reset = 1
    print("bla")

wifi_mode, ssid, passwd = select_mode()
if wifi_mode == "wlan":
    do_connect(ssid,passwd)
    wifi_started = True

connected = False

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
    
def toggle_relay_full(relay_state):
    relay_pins[0].value(relay_state)
    relay_pins[1].value(relay_state)
    relay_pins[2].value(relay_state)
    relay_pins[3].value(relay_state)

def on_message(topic, msg):
    print("Ontvangen bericht - Topic: ", topic, ", Bericht: ", msg)
    try:
        if topic.startswith(MQTT_TOPIC_RELAY_PREFIX):
            relay_number = topic.decode()
            relay_number = relay_number.split("/")[-2]
            print(relay_number)
            
            relay_status = str(msg.decode())
            
            print(relay_status)
            
            toggle_relay(int(relay_number), int(relay_status))
            print("toggeled : ", relay_number, " ", relay_status)
    except Exception as e:
        print("error ", e)

            
    



while True:
    if wifi_started == True:
        try:
            if connected == False :
                toggle_relay_full(False)
                connect_mqtt()
                ap_led.value(0)
                wifi_led.value(1)
                
                connected = True
            if current_amount_tick == sleep_interval_sensor_readings:
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
                current_amount_tick = 0

            mqtt_client.check_msg()
            time.sleep(sleep_interval_mqtt)
            current_amount_tick +=1
        except Exception as e:
            print(e)
            wifi_led.value(0)
            ap_led.value(0)
            print("reconnecting")
            do_connect(ssid,passwd)
            connected = False
        except KeyboardInterrupt:
            print("quitting")
            wifi_led.value(0)
            toggle_relay_full(False)
            print("safe shutdown succesfull")
            break

    
