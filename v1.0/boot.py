import json
import network
import machine
import usocket as socket
from time import sleep
import time
from machine import UART, Pin
# HTML page for network selection
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Vertical Farming Setup Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            text-align: center;
            margin: 0;
            padding: 0;
        }

        h1 {
            font-family: 'Arial', sans-serif;
            color: #333;
        }

        form {
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            margin: 0 auto;
        }

        label {
            display: block;
            margin-top: 10px;
            font-size: 18px;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }

        input[type="submit"] {
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
            margin-top: 15px;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        pre {
            font-family: 'Arial', sans-serif;
            color: #666;
            margin-top: 20px;
        }

        a {
            text-decoration: none;
            color: #007bff;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
<h1>Connect to Wi-Fi and mqtt on your network:</h1>
<main>
<pre>
Enter below your credentials. 
</pre>
<form method="POST" action="/connect">
    <label for="ssid">SSID:</label>
    <input type="text" name="ssid" id="ssid" placeholder="davinci" required><br>

    <label for="password">Password:</label>
    <input type="password" name="password" id="password" placeholder="davinci123456789" required><br>

    <label for="broker_ip">Mqtt broker IP:</label>
    <input type="text" name="broker_ip" id="broker_ip" placeholder="192.168.1......." required><br>
    <label for="client_id">Mqtt client id:</label>
    <input type="text" name="client_id" id="client_id" placeholder="pico_0" required><br>

    <input type="submit" value="Connect"><br>
</form>
<pre>
    Setup page made by Fabian Boshoven.

    Note: When you click <span style="color: #333; font-weight: bold;">Connect</span>, the webpage stops, and the microcontroller reboots to connect to your Wi-Fi network and your MQTT broker.

    Once the green LED turns on from the PCB, it means it is connected to Wi-Fi.

    For the latest release of Vertical Farming, see my <a href="https://github.com/MKEadmin/Vertical_farming">GitHub page</a>.
</pre>
</main>
</body>
</html>
"""



startuptext = """\
#    # ###### #####  ##### #  ####    ##   #         ######   ##   #####  #    # # #    #  ####\r\n
#    # #      #    #   #   # #    #  #  #  #         #       #  #  #    # ##  ## # ##   # #    #\r\n
#    # #####  #    #   #   # #      #    # #         #####  #    # #    # # ## # # # #  # #\r\n
#    # #      #####    #   # #      ###### #         #      ###### #####  #    # # #  # # #  ###\r\n
 #  #  #      #   #    #   # #    # #    # #         #      #    # #   #  #    # # #   ## #    #\r\n
  ##   ###### #    #   #   #  ####  #    # ######    #      #    # #    # #    # # #    #  ####\r\n\
        _\|/_\r\n
       /_____\\\r\n
       \o o/\r\n
    <<\___/>>\r\n
        | |\r\n
        | |\r\n
        | |\r\n
       <_>\r\n
\r\n
Made by Fabian Boshoven \r\n
\r\n
Enter "q" to quit the program or "a" to go in access point mode and change the settings  \r\n

If you want to change setting within acces point mode. Connect to vertical farming network and enter "192.168.4.1" in your browser \r\n

You can also hold the pushbutton on boot to go into acces point mode \r\n
"""


     
passwd_loaded = False
connect_to_wifi = False

serial = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

def do_connect(ssid,passwd):
    time.sleep(1)
    
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    time.sleep(1)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, passwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    serial.write('network config:'+ str(sta_if.ifconfig()) + "\r\n")
    
def create_ap():
    from time import sleep
        # Initialize Wi-Fi and access point
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)

    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    sleep(1)
    ap.config(essid="vertical_farming", password="davinci1234")
    ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))
    ap.active(True)
    

    print("Access Point started")
    serial.write("Access Point started \r\n")


def load_config():
    with open('config.json', 'r') as f:
        data = json.load(f)
        wifi_mode = data['pico']['wlan']['wifi_mode']
        ssid = data['pico']['wlan']['ssid']
        passwd = data['pico']['wlan']['passwd']
        broker_ip = data['pico']['wlan']['broker_ip']
        client_id = data['pico']['wlan']['client_id']
        return wifi_mode, ssid, passwd, broker_ip, client_id
    
def write_config(wifi_mode, ssid, passwd, broker_ip,client_id):
    config_data = {
        'pico': {
            'wlan': {
                'wifi_mode': wifi_mode,
                'ssid': ssid,
                'passwd': passwd,
                'broker_ip' : broker_ip,
                'client_id' : client_id
                
            }
        }
    }

    with open('config.json', 'w') as f:
        json.dump(config_data, f)



   
    


def run_web_server():
     # Create a web server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 80))
    server_socket.listen(1)
    print("Web server started")
    serial.write("Web server started \r\n")
    while passwd_loaded == False:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024).decode()
        response_header = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
        
        if "POST /connect" in request:
            content_length_index = request.find("Content-Length:")
            if content_length_index >= 0:
                content_length_end = request.find("\r\n", content_length_index)
                content_length_value = request[content_length_index:content_length_end].split(" ")[1]
                try:
                    content_length = int(content_length_value)
                    request_body = client_socket.recv(content_length).decode()
                    
                    # Parse the request body to extract form data
                    query_params = request_body.split("&")
                    
                    ssid = None
                    password = None
                    broker_ip = None
                    
                    for param in query_params:
                        key, value = param.split("=")
                        if key == "ssid":
                            ssid = value
                        elif key == "password":
                            password = value
                        elif key == "broker_ip":
                            broker_ip = value
                        elif key == "client_id":
                            client_id = value
                    
                    if ssid and password and broker_ip and client_id:
                        ssid = ssid.replace("%21", "!")
                        password = password.replace("%21", "!")
                        password = password.replace(" ", "")
                        broker_ip = broker_ip.replace(" ", "")
                        client_id = client_id.replace(" ", "")
                        
                        print(f"Attempting to connect to SSID: {ssid} with password: {password}")
                        serial.write(f"Attempting to connect to SSID: {ssid} with password: {password} \r\n")
                        client_socket.send(response_header + "Trying to connect to WLAN. Ap mode will be shut down. If the green light turns on, it is connected to Wi-Fi.")
                        sleep(10)
                        client_socket.close()
                        server_socket.close()
                        write_config("wlan", ssid, password, broker_ip, client_id)
                        machine.reset()
                        break
                    else:
                        print("SSID, password, or broker IP not provided.")
                        serial.write("SSID, password, or broker IP not provided. \r\n")
                        client_socket.send(response_header + "SSID, password, or broker IP not provided. Boot again and try again.")
                        client_socket.close()
                except ValueError:
                    print("Invalid Content-Length value:", content_length_value)
            else:
                print("Content-Length header not found in the request.")
        
        elif "GET / " in request:
            client_socket.send(response_header + html_page)
        
        client_socket.close()


        
        
    
    
#create_ap()
        
def select_mode():
    wifi_mode, ssid, passwd, broker_ip, client_id = load_config()
    print(load_config())
    if wifi_mode == "ap" and ssid == "" and passwd == "":
        create_ap()
        print("starting acces point ")
        serial.write("starting acces point \r\n")
        
        print("Web server created")
        serial.write("Web server created \r\n")
        print("Connect to vertical Farming network and go to : " + "192.168.4.1")
        serial.write("Connect to vertical Farming network and go to : " + "192.168.4.1 \r\n")
        run_web_server()
        
        
        
    elif wifi_mode == "wlan" and ssid != "" and passwd != "":
        print("starting wlan")
        serial.write("starting wlan \r\n")
        return wifi_mode ,ssid, passwd, broker_ip, client_id
        

