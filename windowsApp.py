import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import subprocess
import threading
import json
from pathlib import Path
import os
import sys

class HotkeyManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hotkey Manager")
        self.root.geometry("600x400")
        
        # Configure dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'button': '#2d2d2d',
            'entry': '#2d2d2d',
            'hover': '#3d3d3d'
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TFrame', background=self.colors['bg'])
        self.style.configure('TLabel', 
                           background=self.colors['bg'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10))
        self.style.configure('TButton',
                           background=self.colors['button'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10))
        self.style.configure('TEntry',
                           fieldbackground=self.colors['entry'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10))
        
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize hotkeys dictionary and load saved hotkeys
        self.hotkeys = {}
        self.load_hotkeys()
        
        self.setup_gui()
        self.start_listener()

    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                              text="Hotkey Manager",
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Command key input
        ttk.Label(input_frame, text="Command Key:").pack(side=tk.LEFT)
        self.command_key = ttk.Entry(input_frame, width=10)
        self.command_key.pack(side=tk.LEFT, padx=(10, 20))
        
        # Action input
        ttk.Label(input_frame, text="Action:").pack(side=tk.LEFT)
        self.action = ttk.Entry(input_frame, width=30)
        self.action.pack(side=tk.LEFT, padx=(10, 20))
        
        # Add button
        add_button = ttk.Button(input_frame, 
                              text="Add Hotkey",
                              command=self.add_hotkey)
        add_button.pack(side=tk.LEFT)
        
        # Hotkeys list
        self.hotkeys_frame = ttk.Frame(main_frame)
        self.hotkeys_frame.pack(fill=tk.BOTH, expand=True)
        self.update_hotkeys_list()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, 
                               textvariable=self.status_var,
                               font=('Segoe UI', 9))
        status_label.pack(pady=(20, 0))

    def update_hotkeys_list(self):
        # Clear existing list
        for widget in self.hotkeys_frame.winfo_children():
            widget.destroy()
        
        # Headers
        headers_frame = ttk.Frame(self.hotkeys_frame)
        headers_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(headers_frame, 
                 text="Hotkey", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 100))
        ttk.Label(headers_frame, 
                 text="Action", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # List hotkeys
        for key, action in self.hotkeys.items():
            row_frame = ttk.Frame(self.hotkeys_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            hotkey_text = f"Ctrl+Shift+Alt+{key}"
            ttk.Label(row_frame, text=hotkey_text).pack(side=tk.LEFT, padx=(0, 20))
            ttk.Label(row_frame, text=action).pack(side=tk.LEFT, padx=(0, 20))
            
            delete_btn = ttk.Button(row_frame, 
                                  text="Delete",
                                  command=lambda k=key: self.delete_hotkey(k))
            delete_btn.pack(side=tk.RIGHT)

    def add_hotkey(self):
        key = self.command_key.get().strip().upper()
        action = self.action.get().strip()
        
        if not key or not action:
            messagebox.showerror("Error", "Both command key and action are required")
            return
            
        if len(key) != 1:
            messagebox.showerror("Error", "Command key must be a single character")
            return
            
        self.hotkeys[key] = action
        self.save_hotkeys()
        self.update_hotkeys_list()
        self.command_key.delete(0, tk.END)
        self.action.delete(0, tk.END)
        self.status_var.set(f"Added hotkey: Ctrl+Shift+Alt+{key}")

    def delete_hotkey(self, key):
        del self.hotkeys[key]
        self.save_hotkeys()
        self.update_hotkeys_list()
        self.status_var.set(f"Deleted hotkey: Ctrl+Shift+Alt+{key}")

    def save_hotkeys(self):
        config_path = Path.home() / '.hotkey_manager.json'
        with open(config_path, 'w') as f:
            json.dump(self.hotkeys, f)

    def load_hotkeys(self):
        config_path = Path.home() / '.hotkey_manager.json'
        if config_path.exists():
            with open(config_path) as f:
                self.hotkeys = json.load(f)

    def execute_action(self, action):
        try:
            if action.lower() == 'calc':
                if sys.platform == 'win32':
                    subprocess.Popen('calc.exe')
                else:
                    subprocess.Popen(['gnome-calculator'])
            elif action.lower() == 'chrome':
                if sys.platform == 'win32':
                    subprocess.Popen(['chrome'])
                else:
                    subprocess.Popen(['google-chrome'])
            else:
                subprocess.Popen(action, shell=True)
            self.status_var.set(f"Executed: {action}")
        except Exception as e:
            self.status_var.set(f"Error executing action: {str(e)}")

    def check_hotkey(self, e):
        if keyboard.is_pressed('ctrl+shift+alt'):
            key = e.name.upper()
            if key in self.hotkeys:
                self.execute_action(self.hotkeys[key])

    def start_listener(self):
        keyboard.on_press(self.check_hotkey)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HotkeyManager()
    app.run()
