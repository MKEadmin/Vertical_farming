import json

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
        

if __name__ == "__main__":
    write_config("wlan","blabla1234","snotneus","192.168.1.10","pico_0")
    print(load_config())