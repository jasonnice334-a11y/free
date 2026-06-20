import re, requests, base64, subprocess, sys, socket, os

# Screen ကို ရှင်းထုတ်ပြီး Logo ပြခြင်း
def print_logo():
    # Windows အတွက် 'cls', Linux/Android အတွက် 'clear' သုံးမယ်
    os.system('cls' if os.name == 'nt' else 'clear')
    
    logo = """\033[1;32m
  ███████╗██████╗ ███████╗███████╗
  ██╔════╝██╔══██╗██╔════╝██╔════╝
  █████╗  ██████╔╝█████╗  █████╗  
  ██╔══╝  ██╔══██╗██╔══╝  ██╔══╝  
  ██║     ██║  ██║███████╗███████╗
  ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
    \033[1;36m>> WiFi Bypass Tool - [Manus Edition] <<\033[0m
    """
    print(logo)

# Gateway IP ရှာဖွေခြင်း
def get_gateway_ip():
    try:
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                hex_ip = fields[2]
                ip_parts = [str(int(hex_ip[i:i+2], 16)) for i in range(0, 8, 2)]
                return ".".join(reversed(ip_parts))
    except Exception:
        pass
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ".".join(local_ip.split('.')[:-1]) + ".1"
    except Exception:
        return None

def replace_mac(url, new_mac):
    url = re.sub(r'(?<=mac=)[^&]+', new_mac, url)       
    return url

def get_session_id(fixed_url, user_mac):
    session_url = replace_mac(fixed_url, user_mac)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(session_url, headers=headers, timeout=15)
        session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response.url).group(1)
        return session_id
    except Exception:
        return None

def login_voucher(session_id, voucher):
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "accept": "*/*",
        "content-type": "application/json",
        "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={session_id}",
        "user-agent": 'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        with requests.post(post_url, json=data, headers=headers) as response:
            return re.search('token=(.*?)&', response.text).group(1)
    except:
        return None

def main():
    print_logo()
    
    FIXED_SESSION_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=984a6b458027&gw_sn=H1T078800132C&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.142&mac=ca:51:aa:ff:b8:51&slot_num=33&nasip=192.168.1.161&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C016&chap_challenge=%5C135%5C061%5C367%5C376%5C225%5C324%5C217%5C041%5C213%5C145%5C002%5C251%5C074%5C104%5C267%5C152"
    
    gateway_ip = get_gateway_ip()
    
    user_mac = input("\033[1;33m[+] Enter your MAC Address: \033[0m").strip()
    voucher_code = input("\033[1;33m[+] Enter Voucher Code: \033[0m").strip()
    
    if not user_mac or not voucher_code:
        print("\033[1;31m[!] MAC and Voucher are required!\033[0m")
        return

    if not gateway_ip:
        gateway_ip = input("\033[1;33m[+] Could not auto-detect. Enter Gateway IP: \033[0m").strip()

    print(f"\033[1;34m[*] Using Gateway IP: {gateway_ip}\033[0m")
    
    print("\033[1;34m[*] Getting Session ID...\033[0m")
    session_id = get_session_id(FIXED_SESSION_URL, user_mac)
    
    if not session_id:
        print("\033[1;31m[!] Failed to get Session ID.\033[0m")
        return
    
    print(f"\033[1;32m[+] Session ID: {session_id}\033[0m")
    
    print("\033[1;34m[*] Logging in with Voucher...\033[0m")
    active_token = login_voucher(session_id, voucher_code)
    
    if not active_token:
        print("\033[1;31m[!] Voucher Login Failed.\033[0m")
        return
    
    print("\033[1;34m[*] Sending Final Auth Request...\033[0m")
    auth_url = f"http://{gateway_ip}:2060/wifidog/auth?"
    params = {'token': active_token}
    
    try:
        final_res = requests.get(auth_url, params=params, timeout=10).url
        if any(x in final_res.lower() for x in ["success", "baidu.com", "portal-as"]):
            print("\033[1;32m[+++] Internet Bypass Successful! Enjoy!\033[0m")
        else:
            print(f"\033[1;33m[?] Response: {final_res}\033[0m")
            print("\033[1;32m[+] Bypass might be successful.\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Connection Error: {e}\033[0m")

if __name__ == "__main__":
    main()
