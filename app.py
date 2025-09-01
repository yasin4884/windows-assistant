import requests
import logging
import sqlite3
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (prompt TEXT, response TEXT)''')
    conn.commit()
    conn.close()

def gemma3(prompt):
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={"model": "gemma3:4b", "prompt": prompt, "stream": False})
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Error in Gemma3: {e}")
        return None

def save_to_db(prompt, response):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (prompt, response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()

def find_best_keyword_match(user_input, ai_response):

    user_input_lower = user_input.lower()
    ai_response_lower = ai_response.lower() if ai_response else ""
    
    keywords = [
        ("نوت پد", "notepad"),
        ("notepad", "notepad"),
        ("ماشین حساب", "calculator"),
        ("calculator", "calculator"),
        ("calc", "calculator"),
        ("تسک منیجر", "task manager"),
        ("task manager", "task manager"),
        ("taskmgr", "task manager"),
        ("خط فرمان", "command prompt"),
        ("command prompt", "command prompt"),
        ("cmd", "command prompt"),
        ("پاورشل", "powershell"),
        ("powershell", "powershell"),
        ("رجیستری", "registry"),
        ("registry", "registry"),
        ("regedit", "registry"),
        ("کنترل پنل", "control panel"),
        ("control panel", "control panel"),
        ("فایل اکسپلورر", "file explorer"),
        ("file explorer", "file explorer"),
        ("explorer", "file explorer"),
        ("مای کامپیوتر", "my computer"),
        ("my computer", "my computer"),
        ("this pc", "this pc"),
        
        ("مدیریت دیسک", "disk management"),
        ("disk management", "disk management"),
        ("diskmgmt", "disk management"),
        ("مدیریت کامپیوتر", "computer management"),
        ("computer management", "computer management"),
        ("سرویس‌ها", "services"),
        ("services", "services"),
        ("مدیر دستگاه", "device manager"),
        ("device manager", "device manager"),
        ("devmgmt", "device manager"),
        
        ("صفحه نمایش", "display"),
        ("display", "display"),
        ("صدا", "sound"),
        ("sound", "sound"),
        ("شبکه", "network"),
        ("network", "network"),
        ("وای فای", "wifi"),
        ("wifi", "wifi"),
        ("بلوتوث", "bluetooth"),
        ("bluetooth", "bluetooth"),
        ("باتری", "battery"),
        ("battery", "battery"),
        
        ("تنظیمات", "settings"),
        ("settings", "settings"),
    ]
    
    for keyword, mapped_value in keywords:
        if keyword in user_input_lower:
            return mapped_value
    
    for keyword, mapped_value in keywords:
        if keyword in ai_response_lower:
            return mapped_value
    
    return None

def map_to_command(keyword):

    if not keyword:
        return None
        
    command_map = {
        "notepad": "notepad",
        "calculator": "calc",
        "task manager": "taskmgr",
        "command prompt": "cmd",
        "powershell": "powershell",
        "registry": "regedit",
        "control panel": "control",
        "file explorer": "explorer",
        "my computer": "explorer",
        "this pc": "explorer",
        
        "disk management": "start diskmgmt.msc",
        "computer management": "start compmgmt.msc",
        "services": "start services.msc",
        "device manager": "start devmgmt.msc",
        
        "settings": "start ms-settings:",
        "display": "start ms-settings:display",
        "sound": "start ms-settings:sound",
        "network": "start ms-settings:network",
        "wifi": "start ms-settings:network-wifi",
        "bluetooth": "start ms-settings:bluetooth",
        "battery": "start ms-settings:batterysaver",
    }
    
    return command_map.get(keyword.lower())

def execute_command(command):
    if command:
        try:
            subprocess.run(command, shell=True, check=True)
            logger.info(f"اجرای موفق: {command}")
            print(f"دستور اجرا شد: {command}")
        except subprocess.CalledProcessError as e:
            logger.error(f"خطا در اجرای دستور: {e}")
            print(f" خطا در اجرای دستور: {e}")
    else:
        print(" دستور معتبر پیدا نشد.")

def process_input():
    init_db()
    user_prompt = input("دستور خود را وارد کنید: ")
    
    print(" در حال پردازش...")
    ai_response = gemma3(user_prompt)
    
    if ai_response:
        print(f"AI Response: {ai_response[:100]}...") 
        save_to_db(user_prompt, ai_response)
        
        best_keyword = find_best_keyword_match(user_prompt, ai_response)
        print(f"🔍 کلمه کلیدی یافت شده: {best_keyword}")
        
        command = map_to_command(best_keyword) if best_keyword else None
        print(f" فرمان: {command}")
        
        execute_command(command)
    else:
        print(" خطا در دریافت پاسخ از مدل.")

if __name__ == "__main__":
    process_input()
