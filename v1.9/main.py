"""
Vertical Farming code.

Made by Fabian Boshoven

Date last modified : 22-10-2023

"""
import dht  # dht11 or dht22 libary 
from machine import Pin, ADC, UART
import time
from umqtt.simple import MQTTClient
import boot # boot file for reading config and setting pico in AP mode or WLAN mode

from hardware import *
from app_config import *

wifi_started = False
reset_pin = 7
checked_reset = 0
reset = Pin(reset_pin, Pin.IN,Pin.PULL_DOWN) # reset pin on the pcb if pressed during startup the pico reset and enters AP mode

toggle_relay_full(False) # test relay control on startup 

sleep_interval_mqtt = 1 # sleep intervall for mqtt if set to high the relay state takes longer to update

sleep_interval_sensor_readings = 4  # sleep interval for sensor reading and how long it takes to publish to mqtt each time

max_ticks = sleep_interval_sensor_readings / sleep_interval_mqtt # calculate ticks

current_amount_tick = 0



#uart setup

serial.write(startuptext)
print(startuptext)
time.sleep(5)

wifi_pin = 9
ap_pin = 10
wifi_led = Pin(wifi_pin, Pin.OUT)
ap_led = Pin(ap_pin, Pin.OUT)
wifi_led.value(0)
ap_led.value(0)


if reset.value() == 1:
    print("ap activated")
    serial.write("ap activated \r\n")
    write_config("ap", "", "", "", "")
    ap_led.value(1)
    checked_reset = 1
elif reset.value() == 0:
    checked_reset = 1

wifi_mode, ssid, passwd, broker_ip, client_id = select_mode()
MQTT_BROKER = ""
MQTT_TOPIC_TEMP = "vf/" + client_id +"/sensor/dht22/temp"
MQTT_TOPIC_HUMIDITY = "vf/" + client_id +"/sensor/dht22/humidity"
MQTT_TOPIC_GAS = "vf/"+ client_id +"/sensor/mq135"
MQTT_TOPIC_RELAY_PREFIX = "vf/"+ client_id +"/relay/"
MQTT_TOPIC_INTERNAL_TEMP = "vf/"+ client_id +"/sensor/internal_temperature"
MQTT_TOPIC_DS18B20_TEMP = "vf/"+ client_id +"/sensor/ds18b20"
MQTT_TOPIC_SETPOINT_TEMP = "vf/"+ client_id +"/setpoint/temperature"
MQTT_TOPIC_SETPOINT_HUMIDITY = "vf/"+ client_id +"/setpoint/humidity"
MQTT_TOPIC_SETPOINT_GASS = "vf/"+ client_id +"/setpoint/gass"
MQTT_BROKER = broker_ip
mqtt_client = MQTTClient(client_id, MQTT_BROKER, keepalive=60)

if wifi_mode == "wlan":
    do_connect(ssid,passwd)
    wifi_started = True

connected = False
global topic
global message 
def connect_mqtt():
    try:
        mqtt_client.connect()
        mqtt_client.set_callback(on_message)
        mqtt_client.subscribe(MQTT_TOPIC_RELAY_PREFIX + "#")
        mqtt_client.subscribe(MQTT_TOPIC_SETPOINT_TEMP)
        mqtt_client.subscribe(MQTT_TOPIC_SETPOINT_HUMIDITY)
        mqtt_client.subscribe(MQTT_TOPIC_SETPOINT_GASS)
        time.sleep(1)
        print("connected")
        serial.write("connected \r\n")
    except:
        print("mqtt connection error could not connect to mqtt broker")
        serial.write("mqtt connection error could not connect to mqtt broker")


    


def on_message(topic, msg):
    
    print("Ontvangen bericht - Topic: ", topic, ", Bericht: ", msg)
    serial.write("Ontvangen bericht - Topic: " + str(topic) + ", Bericht: " + str(msg) + "\r\n")
    try:
        if topic.startswith(MQTT_TOPIC_RELAY_PREFIX):
            relay_number = topic.decode()
            relay_number = relay_number.split("/")[-2]
            print(relay_number)
            serial.write(relay_number + "\n")
            relay_status = str(msg.decode())
            
            print(relay_status)
            
            toggle_relay(int(relay_number), int(relay_status))
            print("toggeled : ", relay_number, " ", relay_status)
            serial.write("toggeled : " + str(relay_number) + " " + str(relay_status) + "\r\n")
        topic_test = topic
        message_test = msg
    except Exception as e:
        print("error ", e)
        serial.write("error " + str(e)+ "\r\n")
    

            
    
while True:
    global topic
    global message 
    if wifi_started == True:
        try:
            if connected == False :
                toggle_relay_full(False)
                connect_mqtt()
                ap_led.value(0)
                wifi_led.value(1)
                
                connected = True
            
            if current_amount_tick == sleep_interval_sensor_readings:
                # read dht sensor data 
                temperature, humidity = read_dht22()
                print("temp dht22 : ", temperature , " humidity : ", humidity)
                serial.write("temp dht22 : "+ str(temperature) + " humidity : " + str(humidity) + "\r\n")

                # Publish dht data to mqtt
                mqtt_client.publish(MQTT_TOPIC_HUMIDITY, str(humidity))
                mqtt_client.publish(MQTT_TOPIC_TEMP, str(temperature))
                
                
                # read mq135
                gas_value = read_gas_sensor()
                print("gas : ", gas_value)
                serial.write("gas : "+ str(gas_value) + "\r\n")

                # Publish mq135
                mqtt_client.publish(MQTT_TOPIC_GAS, str(gas_value))
                
                #read internal temp
                internal_temp = read_internal_temp()
                
                #publish temp  
                mqtt_client.publish(MQTT_TOPIC_INTERNAL_TEMP, str(internal_temp))
                print("temp internal : ", internal_temp)
                serial.write("temp internal : "+ str(internal_temp) + "\r\n")
                
                #publish temp from ds18b20
                temp_ds18b20 = read_ds18b20()
                mqtt_client.publish(MQTT_TOPIC_DS18B20_TEMP, str(temp_ds18b20))
                print("temp ds18b20 : ", temp_ds18b20)
                serial.write("temp ds18b20 : "+ str(temp_ds18b20) + "\r\n")
                #reset ticker
                current_amount_tick = 0
                
    #             readed_serial = serial.read()
    #             if readed_serial != None:
    #                 readed_serial = readed_serial.decode('utf-8').strip()
    #                 print(readed_serial)
    #                 serial.write(readed_serial + "\r\n")
    #                 if readed_serial =="q":       
    #                     print("quitting")
    #                     serial.write("quitting \r\n")
    #                     wifi_led.value(0)
    #                     toggle_relay_full(False)
    #                     print("safe shutdown succesfull")
    #                     serial.write("safe shutdown succsesfull \r\n")
    #                     break
    #                 if readed_serial == "a":
    #                     print("going into acess point mode connect to vertical farming network")
    #                     serial.write("Going into access point mode. Connect to vertical farming network \r\n")
    #                     write_config("ap", "", "", "", "")
    #                     ap_led.value(1)
    #                     wifi_led.value(0)
    #                     select_mode()
                        

            mqtt_client.check_msg()
            time.sleep(sleep_interval_mqtt)
            current_amount_tick +=1
        
            
        except Exception as e:
            print(e)
            serial.write(str(e) + "\r\n")
            wifi_led.value(0)
            ap_led.value(0)
            print("reconnecting")
            serial.write("reconnecting \r\n")
            
            do_connect(ssid,passwd)
            connected = False
        except KeyboardInterrupt:
            print("quitting")
            serial.write("quitting \r\n")
            wifi_led.value(0)
            toggle_relay_full(False)
            print("safe shutdown succesfull ")
            serial.write("safe shutdown succesfull \r\n")
            break

    
