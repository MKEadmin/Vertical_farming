import json
import network
import machine
import usocket as socket
from time import sleep
import time
from machine import UART, Pin
from accesspoint import *
from app_config import *

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
    



def select_mode():
    wifi_mode, ssid, passwd, broker_ip, client_id = load_config()
    print(load_config())
    if wifi_mode == "ap" and ssid == "" and passwd == "":
        ap = AccessPoint("index.html", "config.json")
        html_page = ap.load_html()
        ap.create_ap("vertical_farming", "davinci1234")
        ap.run_web_server(html_page)
        
        
        
    elif wifi_mode == "wlan" and ssid != "" and passwd != "":
        print("starting wlan")
        serial.write("starting wlan \r\n")
        return wifi_mode ,ssid, passwd, broker_ip, client_id
        

