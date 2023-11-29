from time import sleep
import network
import machine
import usocket as socket
from app_config import *

class AccessPoint:
    def __init__(self, html_file, config_file):
        self.html_file = html_file
        self.config_file = config_file

    def load_html(self):
        file = open(self.html_file)
        html_page = file.read()
        file.close()
        return html_page

    def create_ap(self, ssid, passwd):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        ap_mode = network.WLAN(network.AP_IF)
        ap_mode.active(False)
        sleep(1)
        ap_mode.config(essid=ssid, password=passwd) 
        ap_mode.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))
        ap_mode.active(True)
        return "OK"
    
    def run_web_server(self, html_page):
         # Create a web server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', 80))
        server_socket.listen(1)
        print("Web server started")
        while True:
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
                            password = password.replace("%21", "!") # note fix if wifi password contains a "!" maybe with more characters errors but not yet tested 
                            password = password.replace(" ", "") # remove spaces from password so currently no spacing in the wifi password
                            broker_ip = broker_ip.replace(" ", "") # broker ip must not contain spaces otherwise invalid ip adress there are never spaces in a ip adress
                            client_id = client_id.replace(" ", "") # same for client id otherwise error publishing to mqtt broker
                            
                            print(f"Attempting to connect to SSID: {ssid} with password: {password}")
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
    

if __name__ == "__main__":
    ap = AccessPoint("index.html", "config.json")
    html_page = ap.load_html()
    ap.create_ap("vertical_farming", "davinci1234")
    ap.run_web_server(html_page)
