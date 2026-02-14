<h1 align="center">sofinco-discord-bypass</h1>
<h2 align="center">Auto-refreshing TOTP generator for Discord 2FA</h2>

---

### How to get your 2FA key:
1. The highlighted text in the image below is what you need to put in `key.txt`
2. Remove all spaces from the key before saving it
3. For multiple accounts, use format: `account_name: KEY` (one per line)

---

![image](https://github.com/severityc/Discord-2FA-Receiver/assets/158026132/17722808-ecab-4e56-b939-35b05b7f395c)

---

### ⚙️ Installation
1. Install [Python 3.11.6](https://www.python.org/downloads/release/python-3116/) and add it to path
2. Run `install.bat` or `pip install -r requirements.txt`
3. Put your 2FA key in `key.txt`
4. Run `main.py`

---

### ✨ Features
- Auto-copy codes to clipboard
- Real-time countdown timer
- Smart refresh (only updates when code changes)
- Key validation and error handling
- Visual progress bar with color indicators
- QR code generator for easy backup/transfer
- Multiple accounts support

---

### 🚨 Important
1. Keep your key safe - losing it means losing access to your Discord account
2. Never use public hosting services like [replit](https://replit.com) with your actual keys
3. Use encryption feature to protect your keys with a password

---

inspired by https://github.com/GeeGeeNL/Discord-2FA-Bypasser

made by [sofinco](https://github.com/levouinse)
