#Ref: https://www.learncodewithmike.com/2021/10/python-scrape-free-proxy-ip.html
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import requests
import re
DIR = f"""{str(pathlib.Path(__file__).parent.resolve())}/file/"""
def get_proxy_ip() :
    response = requests.get("https://www.sslproxies.org/")

    proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response.text)  #「\d+」代表數字一個位數以上

    valid_ips = []
    for index, ip in enumerate(proxy_ips):
        if len(valid_ips) == 10:
            break;
        try:
            result = requests.get('https://ip.seeip.org/jsonip?',
                       proxies={'http': ip, 'https': ip},
                       timeout=5)
            print(result.json())
            valid_ips.append(ip)
        except:
            print(f"{ip} invalid")
    return valid_ips

def save_list_to_txt(valid_ips):
    with open(f"""{DIR}proxy_list.txt""", 'w') as file:
        for ip in valid_ips:
            file.write(ip + '\n')
        file.close()

if __name__ == '__main__':
    valid_ips = get_proxy_ip()
    save_list_to_txt(valid_ips)