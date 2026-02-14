import pyotp
import os
import time
import sys
import pyperclip
import qrcode
import getpass
from colorama import Fore, Style, init
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

init(autoreset=True)
os.system('clear' if os.name != 'nt' else 'cls')

ENCRYPTED_FILE = 'key.enc'
SALT_FILE = '.salt'

def derive_key(password, salt):
    kdf = PBKDF2(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_keys(data, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    with open(SALT_FILE, 'wb') as sf:
        sf.write(salt)
    with open(ENCRYPTED_FILE, 'wb') as ef:
        ef.write(encrypted)
    return True

def decrypt_keys(password):
    try:
        with open(SALT_FILE, 'rb') as sf:
            salt = sf.read()
        with open(ENCRYPTED_FILE, 'rb') as ef:
            encrypted = ef.read()
        key = derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted).decode()
    except:
        return None

def get_current_code(key):
    totp = pyotp.TOTP(key)
    return totp.now()

def get_time_remaining():
    return 30 - (int(time.time()) % 30)

def get_progress_bar(time_left, total=30, length=20):
    filled = int((time_left / total) * length)
    bar = '█' * filled + '░' * (length - filled)
    color = Fore.GREEN if time_left > 10 else Fore.YELLOW if time_left > 5 else Fore.RED
    return f"{color}{bar}{Fore.RESET}"

def generate_qr(key, account_name="Discord"):
    uri = pyotp.totp.TOTP(key).provisioning_uri(name=account_name, issuer_name="Discord 2FA")
    qr = qrcode.QRCode(box_size=1, border=1)
    qr.add_data(uri)
    qr.make()
    qr.print_ascii(invert=True)

def read_key_from_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
            if not content or content.startswith('replace this'):
                print(f"{Fore.RED}[ERROR]{Fore.RESET} key.txt is empty or not configured")
                sys.exit(1)
            
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            accounts = {}
            
            for line in lines:
                if ':' in line:
                    name, key = line.split(':', 1)
                    accounts[name.strip()] = key.strip().replace(' ', '')
                else:
                    accounts['default'] = line.replace(' ', '')
            
            return accounts
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR]{Fore.RESET} key.txt not found")
        sys.exit(1)

def parse_accounts(content):
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    accounts = {}
    for line in lines:
        if ':' in line:
            name, key = line.split(':', 1)
            accounts[name.strip()] = key.strip().replace(' ', '')
        else:
            accounts['default'] = line.replace(' ', '')
    return accounts

# Check if encryption exists
if os.path.exists(ENCRYPTED_FILE):
    password = getpass.getpass(f"{Fore.YELLOW}Enter password to decrypt keys:{Fore.RESET} ")
    decrypted = decrypt_keys(password)
    if not decrypted:
        print(f"{Fore.RED}[ERROR]{Fore.RESET} Wrong password or corrupted file")
        sys.exit(1)
    accounts = parse_accounts(decrypted)
elif os.path.exists('key.txt'):
    # First time setup - offer encryption
    print(f"{Fore.YELLOW}[SECURITY]{Fore.RESET} Would you like to encrypt your keys? (recommended)")
    choice = input(f"{Fore.YELLOW}Encrypt keys? (y/n):{Fore.RESET} ").strip().lower()
    
    if choice == 'y':
        with open('key.txt', 'r') as f:
            content = f.read().strip()
        
        if content.startswith('replace this'):
            print(f"{Fore.RED}[ERROR]{Fore.RESET} Please configure key.txt first")
            sys.exit(1)
        
        password = getpass.getpass(f"{Fore.YELLOW}Create encryption password:{Fore.RESET} ")
        confirm = getpass.getpass(f"{Fore.YELLOW}Confirm password:{Fore.RESET} ")
        
        if password != confirm:
            print(f"{Fore.RED}[ERROR]{Fore.RESET} Passwords don't match")
            sys.exit(1)
        
        if encrypt_keys(content, password):
            os.remove('key.txt')
            print(f"{Fore.GREEN}[SUCCESS]{Fore.RESET} Keys encrypted successfully")
            print(f"{Fore.CYAN}[INFO]{Fore.RESET} Original key.txt has been deleted")
            print(f"{Fore.CYAN}[INFO]{Fore.RESET} Restart the program to continue\n")
            sys.exit(0)
    else:
        accounts = read_key_from_file('key.txt')
else:
    print(f"{Fore.RED}[ERROR]{Fore.RESET} No key file found")
    sys.exit(1)

print(f"{Fore.CYAN}╔══════════════════════════════════════════════╗{Fore.RESET}")
print(f"{Fore.CYAN}║{Fore.RESET}     Discord 2FA Bypass - sofinco            {Fore.CYAN}║{Fore.RESET}")
print(f"{Fore.CYAN}╚══════════════════════════════════════════════╝{Fore.RESET}\n")

if len(accounts) > 1:
    print(f"{Fore.CYAN}[ACCOUNTS]{Fore.RESET} Found {len(accounts)} account(s)")
    for idx, name in enumerate(accounts.keys(), 1):
        print(f"  {idx}. {name}")
    print()

print(f"{Fore.CYAN}[OPTIONS]{Fore.RESET}")
print(f"  1. Start TOTP generator")
print(f"  2. Generate QR code for backup")
print(f"  3. Exit\n")

choice = input(f"{Fore.YELLOW}Select option (1-3):{Fore.RESET} ").strip()

if choice == '2':
    if len(accounts) == 1:
        name, key = list(accounts.items())[0]
        print(f"\n{Fore.CYAN}[QR CODE]{Fore.RESET} Scan this with your authenticator app:\n")
        generate_qr(key, name)
    else:
        print(f"\n{Fore.CYAN}[SELECT ACCOUNT]{Fore.RESET}")
        for idx, name in enumerate(accounts.keys(), 1):
            print(f"  {idx}. {name}")
        acc_choice = int(input(f"\n{Fore.YELLOW}Select account:{Fore.RESET} ").strip()) - 1
        name = list(accounts.keys())[acc_choice]
        key = accounts[name]
        print(f"\n{Fore.CYAN}[QR CODE]{Fore.RESET} Scan this with your authenticator app:\n")
        generate_qr(key, name)
    print(f"\n{Fore.GREEN}[SUCCESS]{Fore.RESET} QR code generated successfully")
    sys.exit(0)
elif choice == '3':
    sys.exit(0)

os.system('clear' if os.name != 'nt' else 'cls')

selected_account = None
if len(accounts) > 1:
    print(f"{Fore.CYAN}[SELECT ACCOUNT]{Fore.RESET}")
    for idx, name in enumerate(accounts.keys(), 1):
        print(f"  {idx}. {name}")
    acc_choice = int(input(f"\n{Fore.YELLOW}Select account:{Fore.RESET} ").strip()) - 1
    selected_account = list(accounts.keys())[acc_choice]
    key = accounts[selected_account]
else:
    selected_account = list(accounts.keys())[0]
    key = accounts[selected_account]

os.system('clear' if os.name != 'nt' else 'cls')

account_display = f" [{selected_account}]" if selected_account != 'default' else ""
print(f"{Fore.CYAN}[INFO]{Fore.RESET} Auto-copy enabled{account_display}")
print(f"{Fore.CYAN}[INFO]{Fore.RESET} Press Ctrl+C to exit\n")

last_code = None

try:
    while True:
        current_code = get_current_code(key)
        time_left = get_time_remaining()
        progress = get_progress_bar(time_left)
        
        if current_code != last_code:
            pyperclip.copy(current_code)
            print(f"{Fore.LIGHTGREEN_EX}[NEW CODE]{Fore.RESET} {current_code} {progress} {Fore.YELLOW}{time_left}s{Fore.RESET} {Fore.GREEN}✓ copied{Fore.RESET}")
            last_code = current_code
        else:
            print(f"\r{Fore.LIGHTGREEN_EX}[TOTP]{Fore.RESET} {current_code} {progress} {Fore.YELLOW}{time_left}s {Fore.RESET}", end='', flush=True)
        
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n\n{Fore.CYAN}[INFO]{Fore.RESET} Exiting...")
    sys.exit(0)
