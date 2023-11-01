import dht  # dht11 or dht22 libary 
from machine import Pin, ADC, UART
import machine
import onewire # libary for reading ds18b20 sensor
import ds18x20 # ds18b20 libary needs onewire in order to work
dht_sensor = dht.DHT11(Pin(2)) # DHT22 connection

# MQ135 sensor connection
mq135_sensor = ADC(Pin(26))

# Relay pins on the pcb for controlling fans, water, and light
relay_pins = [Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT), Pin(6, Pin.OUT)]

#internal temp sensor see https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
temp_internal = machine.ADC(4)

ds_pin = Pin(22)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

sensor_ds18b20 = ds_sensor.scan()
serial = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))



########################################
# test functions                       #
test_dht22 = True
test_internal_temp = True
test_gas_sensor = True
test_ds18b20 = True
sleep_time = 1
########################################
def read_dht22():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except:
        print("error reading dht22 check wiring or sensor !!!!")
        serial.write("error reading dht22 check wiring or sensor !!!! \r\n")
        return 0, 0 # value if something is wrong


def read_internal_temp():
    raw_temp = temp_internal.read_u16() * 3.3 / (65535)
    raw_temp = 27 - (raw_temp -0.706)/0.001721
    temp = round(raw_temp, 2)
    return temp
    

def read_gas_sensor():
    voltage = mq135_sensor.read_u16() / 65535 * 3.3
    raw_gas_sensor_value = voltage / 3.3 * 100
    gas_sensor_value = round(raw_gas_sensor_value, 2)
    
    if gas_sensor_value <= 5:
        print("gas sensor error check wiring or sensor")
        serial.write("gas sensor error check wiring or sensor")
        return 0
    else :
        return gas_sensor_value
def read_ds18b20():
    try:
        ds_sensor.convert_temp()
        for sensor in sensor_ds18b20:
            temp = ds_sensor.read_temp(sensor)
            return int(temp)
    except:
        print("error reading ds18b20 check sensor on pcb ")
        serial.write("error reading ds18b20 check sensor on pcb \r\n")
        return 0
def toggle_relay(relay_number, status):
    relay_pins[relay_number].value(status)
    
def toggle_relay_full(relay_state):
    relay_pins[0].value(relay_state)
    relay_pins[1].value(relay_state)
    relay_pins[2].value(relay_state)
    relay_pins[3].value(relay_state)
    
if __name__ == '__main__':
    print("testing functions")
    while True:
        try:
            if test_dht22:
                print(f'dht22 sensor : {str(read_dht22())}')
            if test_internal_temp:
                print(f'internal temp sensor : {str(read_internal_temp())}')
            if test_gas_sensor:
                print(f'gas sensor : {str(read_gas_sensor())}')
            if test_ds18b20:
                print(f'ds18b20 sensor : {str(read_ds18b20())}')
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("quitting .. ")
            break
        
            
            
        
            
            
        
    