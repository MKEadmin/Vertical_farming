import json
import network
import machine
import usocket as socket
from time import sleep
import time

# HTML page for network selection
html_page = """
<!DOCTYPE html>
<html>
<head><title>Wi-Fi Setup</title></head>
<body>
<h2>Connect to Wi-Fi Network:</h2>
<form method="GET" action="/connect">
SSID: <input type="text" name="ssid"><br><br>
Password: <input type="password" name="password"><br><br>
<input type="submit" value="Connect">
</form>
</body>
</html>
"""

passwd_loaded = False
connect_to_wifi = False

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
    


def load_config():
    with open('config.json', 'r') as f:
        data = json.load(f)
        wifi_mode = data['pico']['wlan']['wifi_mode']
        ssid = data['pico']['wlan']['ssid']
        passwd = data['pico']['wlan']['passwd']
        return wifi_mode, ssid, passwd
    
def write_config(wifi_mode, ssid, passwd):
    config_data = {
        'pico': {
            'wlan': {
                'wifi_mode': wifi_mode,
                'ssid': ssid,
                'passwd': passwd
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
    while passwd_loaded == False:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024).decode()
        response_header = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
        
        if "GET / " in request:
            html_response = html_page
            client_socket.send(response_header + html_response)
        elif "GET /connect?" in request:
            query_string = request.split("GET /connect?")[1].split("HTTP/1.1")[0]
            query_params = query_string.split("&")
            
            ssid = None
            password = None
            
            for param in query_params:
                key, value = param.split("=")
                if key == "ssid":
                    ssid = value
                elif key == "password":
                    password = value
                    break  # Stop processing after extracting the password
            
            if ssid and password:
                ssid = ssid.replace("%21", "!")  # Manually decode %21 to !
                password = password.replace("%21", "!")  # Manually decode %21 to !
                password = password.replace(" ", "")
                
                print(f"Attempting to connect to SSID: {ssid} with password: {password}")
                client_socket.send(response_header + "trying to connect to wlan Ap mode will be shut down. If green light turns on it is connected to wifi")
                sleep(1)
                client_socket.close()  # Close the client socket
                server_socket.close()  # Close the server socket
                write_config("wlan",ssid, password)
                machine.reset()
                break
                    
               
            else:
                print("SSID or password not provided.")
                client_socket.send(response_header + "SSID and password not provided boot again and try again.")
                client_socket.close()  # Close the client socket
        
        client_socket.close()  # Close the client socket for all other cases


        
        
    
    
#create_ap()
        
def select_mode():
    wifi_mode, ssid, passwd = load_config()
    print(load_config())
    if wifi_mode == "ap" and ssid == "" and passwd == "":
        create_ap()
        print("starting acces point ")
        #create_web_server()
        print("web server created")
        run_web_server()
        print("server running")
        
        
    elif wifi_mode == "wlan" and ssid != "" and passwd != "":
        print("starting wlan")
        return wifi_mode ,ssid, passwd
        print("true")

