import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pydexcom import Dexcom
import subprocess
import threading
from pathlib import Path
from config_handler import save_config, save_config_constants
from config_handler import load_config, load_config_constants


BASE_DIR = Path(__file__).resolve().parent
PYTHON_BIN = BASE_DIR / 'venv' / 'bin' / 'python'
SCR_OPT = BASE_DIR / 'scrOpt.py'
DEXPY = BASE_DIR / 'dexpy.py'

command_if_o = f"lxterminal -e '{str(PYTHON_BIN)} {str(SCR_OPT)}'"
command_else = f"lxterminal -e '{str(PYTHON_BIN)} {str(DEXPY)}'"


def check_login(username, password, region):
    try:
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        save_config(username, password, region)
        return True
    except:
        return False

def check_constants(low_value, seconds_value):
    save_config_constants(low_value, seconds_value)

def try_login():
    try:
        username, password, region = load_config()
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        save_config(username, password, region)
        return True
    except:
        return False
        
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.logged_in = False
        if try_login():
            self.logged_in = True
            self.show_main_ui()
        else:
            self.show_main_ui_first()

    def show_main_ui_first(self):
        self.clear_window()
        self.root.title("Hauptmenü")

        label = tk.Label(self.root, text="Thanks for starting the application! You will now need to configure the programm.", font=('Arial', 16), wraplength=550)
        label.pack(pady=25)

        label2 = tk.Label(self.root, text="This tool helps wake you up when your blood sugar is low. It works with Dexcom data (online through Dexcom-Share or via cable with your Dexcom Receiver) and sounds an alarm if your level drops below a certain bloodsugar, stopping only after you solve a simple math question.", font=('Arial', 14), wraplength=500)
        label2.pack(pady=(25, 0))

        btn1 = tk.Button(self.root, text="Beginn", command=self.create_constants, font=('Arial'))
        btn1.pack(pady=70)
        
    def create_constants(self):
        self.clear_window()
        self.root.title("Hauptmenü")
        
        self.auswahl1 = tk.StringVar()
        self.auswahl2 = tk.StringVar()
        
        label = tk.Label(self.root, text="Please configure at what bloodsugar you want the low alarm to trigger and how long it should take in minutes for the alarm to trigger after deactivation if still low.", font=('Arial', 16), wraplength=550)
        label.pack(pady=25)
        
        optionen1 = ["55", "60", "65", "70", "75", "80", "85", "90", "95", "100"]
        tk.Label(self.root, text="Low alert at:").pack()
        combobox = ttk.Combobox(self.root, textvariable=self.auswahl1, values=optionen1, state="readonly")
        combobox.pack(padx=20, pady=20)
        
        optionen2 = ["5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"]
        tk.Label(self.root, text="Repeat low alarm after how many minutes:").pack()
        combobox = ttk.Combobox(self.root, textvariable=self.auswahl2, values=optionen2, state="readonly")
        combobox.pack(padx=20, pady=20)
        
        next_button = tk.Button(self.root, text="Confirm", command=self.try_login_constants)
        next_button.pack(pady=10)
    
    def try_login_constants(self):
        low_threshold=self.auswahl1.get()
        cooldown_seconds=self.auswahl2.get()
        check_constants(int(low_threshold), int(cooldown_seconds))
        if try_login():
            self.show_main_ui()
        else:
            self.create_login_ui()
                
    def create_login_ui(self):
        self.clear_window()

        label = tk.Label(self.root, text="Enter your Dexcom Login or Skip this step. If you skip you won't be able to use the Dexcom-Share capabilities.", font=('Arial'), wraplength=600)
        label.pack(pady=20)

        tk.Label(self.root, text="Benutzername:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Passwort:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Label(self.root, text="Region:").pack()
        self.region_entry = tk.Entry(self.root)
        self.region_entry.pack()

        login_button = tk.Button(self.root, text="Login", command=self.try_login)
        login_button.pack(pady=10)

        skip_button = tk.Button(self.root, text="Skip", command=self.skip_login)
        skip_button.pack(pady=10)

    def try_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        region = self.region_entry.get()

        if check_login(username, password, region):
            self.logged_in = True
            self.show_main_ui()
        else:
            messagebox.showerror("Fehler", "Login failed. Please try again.")

    def skip_login(self):
        self.logged_in = False
        self.show_main_ui()

    def show_main_ui(self):
        self.clear_window()
        self.root.title("Hauptmenü")

        label = tk.Label(self.root, text="You can now choose which one to start.", font=('Arial', 16), wraplength=550)
        label.pack(pady=(25, 83))

        btn1 = tk.Button(self.root, text="Offline via Dexcom-Receiver", font=('Arial', 14), command=self.execute_action1)
        btn1.pack(pady=13)

        btn2 = tk.Button(self.root, text="Online via Dexcom Share", font=('Arial', 14), command=self.require_login_before_action2)
        btn2.pack(pady=13)
        
        btn3 = tk.Button(self.root, text="Logout", font=('Arial', 14), command=self.logout)
        btn3.pack(pady=(60, 25))
        
        separator = ttk.Separator(root, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        low_value, cooldown_seconds = load_config_constants()
        
        label1 = tk.Label(self.root, text=f"The alarm threshold is {low_value} and the cooldown is set to {cooldown_seconds} minutes.", font=('Arial', 14), wraplength=550)
        label1.pack(pady=15)
        
        btn4 = tk.Button(self.root, text="Change alarm settings", font=('Arial', 14), command=self.create_constants)
        btn4.pack(pady=25)
    
    def logout(self):
        save_config("empty", "empty", "empty")
        self.create_login_ui()

    def execute_action1(self):
        subprocess.run(command_else, shell=True)
        print("Aktion 1 ausgeführt (kein Login benötigt).")
        self.root.destroy()

    def require_login_before_action2(self):
        if self.logged_in:
            subprocess.run(command_if_o, shell=True)
            print("Aktion 2 ausgeführt (Login war erfolgreich).")
            self.root.destroy()
        else:
            messagebox.showwarning("Login benötigt", "Bitte logge dich ein, um diese Aktion auszuführen.")
            self.create_login_ui()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x550")
    app = LoginApp(root)
    root.mainloop()
