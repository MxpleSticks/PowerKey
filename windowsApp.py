import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import subprocess
import threading
import json
from pathlib import Path
import os
import sys
import winreg

class HotkeyManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PowerKey")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Enhanced dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',  # Added accent color
            'button': '#2d2d2d',
            'entry': '#2d2d2d',
            'hover': '#3d3d3d',
            'border': '#404040',  # Added border color
            'success': '#4CAF50',  # Added success color
            'error': '#f44336'    # Added error color
        }
        
        # Configure enhanced styles
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure frame style
        self.style.configure('TFrame', background=self.colors['bg'])
        
        # Configure modern label style
        self.style.configure('TLabel', 
                           background=self.colors['bg'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10))
        
        # Configure modern button style
        self.style.configure('TButton',
                           background=self.colors['button'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10),
                           padding=8)
        
        # Configure accent button style
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=8)
        
        # Configure entry style
        self.style.configure('TEntry',
                           fieldbackground=self.colors['entry'],
                           foreground=self.colors['fg'],
                           font=('Segoe UI', 10),
                           padding=8)
        
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize hotkeys dictionary and load saved hotkeys
        self.hotkeys = {}
        self.load_hotkeys()
        
        # Initialize startup state
        self.startup_enabled = self.check_startup_status()
        
        self.setup_gui()
        self.start_listener()

    def setup_gui(self):
        # Main container with padding
        container = ttk.Frame(self.root, padding="20", relief="flat", borderwidth=0)
        container.pack(fill=tk.BOTH, expand=True)

        # Header section with logo and title
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 30))

        title_label = ttk.Label(header_frame,
                                text="PowerKey",
                                font=('Segoe UI', 24, 'bold'),
                                foreground=self.colors['accent'])
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(header_frame,
                                text="Hotkey Manager",
                                font=('Segoe UI', 12),
                                foreground='#888888')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))

        # Frame to control button positioning
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)

        # Add startup toggle button
        self.startup_var = tk.StringVar(value="Startup: " + ("ON" if self.startup_enabled else "OFF"))
        startup_button = ttk.Button(button_frame,
                                    textvariable=self.startup_var,
                                    style='Accent.TButton',
                                    command=self.toggle_startup)
        startup_button.pack(side=tk.RIGHT, padx=(10, 0), pady=(15, 0))

        help_button = ttk.Button(button_frame,
                                text="?",
                                width=3,
                                style='Accent.TButton',
                                command=self.show_help)
        help_button.pack(side=tk.RIGHT, padx=(10, 0), pady=(15, 0))

        # Input section with modern layout
        input_frame = ttk.Frame(container)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Command key input with label above
        key_frame = ttk.Frame(input_frame)
        key_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(key_frame,
                text="HOTKEY COMBINATION",
                font=('Segoe UI', 8),
                foreground='#888888').pack(anchor=tk.W)

        key_input_frame = ttk.Frame(key_frame)
        key_input_frame.pack(fill=tk.X)

        ttk.Label(key_input_frame,
                text="Ctrl+Shift+Alt+",
                font=('Segoe UI', 10)).pack(side=tk.LEFT)

        self.command_key = ttk.Entry(key_input_frame, width=5)
        self.command_key.pack(side=tk.LEFT, padx=(5, 0))

        # Action input with label above
        action_frame = ttk.Frame(input_frame)
        action_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(action_frame,
                text="ACTION",
                font=('Segoe UI', 8),
                foreground='#888888').pack(anchor=tk.W)

        self.action = ttk.Entry(action_frame)
        self.action.pack(fill=tk.X)

        # Add button
        add_button = ttk.Button(input_frame,
                                text="Add Hotkey",
                                style='Accent.TButton',
                                command=self.add_hotkey)
        add_button.pack(side=tk.LEFT, padx=(10, 0), pady=(15, 0))

        # Separator
        separator = ttk.Frame(container, height=2)
        separator.pack(fill=tk.X, pady=20)
        separator.configure(style='Separator.TFrame')
        self.style.configure('Separator.TFrame', background=self.colors['border'])

        # Hotkeys list with headers
        list_frame = ttk.Frame(container)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Headers with modern styling
        headers_frame = ttk.Frame(list_frame)
        headers_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(headers_frame,
                text="HOTKEY",
                font=('Segoe UI', 8),
                foreground='#888888').pack(side=tk.LEFT, padx=(0, 150))

        ttk.Label(headers_frame,
                text="ACTION",
                font=('Segoe UI', 8),
                foreground='#888888').pack(side=tk.LEFT)

        # Scrollable frame for hotkeys
        canvas = tk.Canvas(list_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, padding="10")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Status bar with modern styling
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(container,
                                textvariable=self.status_var,
                                font=('Segoe UI', 9),
                                foreground='#888888')
        status_label.pack(pady=(20, 0))

        self.update_hotkeys_list()

    def check_startup_status(self):
        """Check if the application is set to run at startup"""
        if sys.platform != 'win32':
            return False
            
        app_path = sys.executable
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, "PowerKey")
                return value == f'"{app_path}"'
            except WindowsError:
                return False
            finally:
                winreg.CloseKey(key)
        except WindowsError:
            return False

    def toggle_startup(self):
        """Toggle the startup status of the application"""
        if sys.platform != 'win32':
            messagebox.showwarning("Warning", "Startup configuration is only supported on Windows")
            return
            
        app_path = sys.executable
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            if self.startup_enabled:
                # Remove from startup
                winreg.DeleteValue(key, "PowerKey")
                self.startup_enabled = False
                self.status_var.set("Removed from startup")
            else:
                # Add to startup
                winreg.SetValueEx(key, "PowerKey", 0, winreg.REG_SZ, f'"{app_path}"')
                self.startup_enabled = True
                self.status_var.set("Added to startup")
            
            winreg.CloseKey(key)
            self.startup_var.set("Startup: " + ("ON" if self.startup_enabled else "OFF"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify startup settings: {str(e)}")

    def update_hotkeys_list(self):
        # Clear existing list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # List hotkeys with modern styling
        for key, action in self.hotkeys.items():
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill=tk.X, pady=5)

            # Add subtle hover effect
            row_frame.bind('<Enter>', lambda e, f=row_frame: f.configure(style='Hover.TFrame'))
            row_frame.bind('<Leave>', lambda e, f=row_frame: f.configure(style='TFrame'))

            hotkey_text = f"Ctrl+Shift+Alt+{key}"
            ttk.Label(row_frame,
                    text=hotkey_text,
                    font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 20))

            ttk.Label(row_frame,
                    text=action,
                    font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 20))

            delete_btn = ttk.Button(row_frame,
                                text="×",
                                width=3,
                                command=lambda k=key: self.delete_hotkey(k))
            delete_btn.pack(side=tk.RIGHT)

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Use PowerKey")
        help_window.configure(bg=self.colors['bg'])
        
        window_width = 500
        window_height = 400
        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()
        center_x = int((screen_width/2) - (window_width/2))
        center_y = int((screen_height/2) - (window_height/2))
        
        help_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        help_window.resizable(False, False)
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.pack(expand=True, fill=tk.BOTH)
        
        title = ttk.Label(help_frame,
                         text="How to Use PowerKey",
                         font=('Segoe UI', 20, 'bold'),
                         foreground=self.colors['accent'])
        title.pack(pady=(0, 20))
        
        # Create a frame for the scrollable content
        content_frame = ttk.Frame(help_frame)
        content_frame.pack(expand=True, fill=tk.BOTH)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create text widget with scrollbar
        text_widget = tk.Text(content_frame,
                            wrap=tk.WORD,
                            yscrollcommand=scrollbar.set,
                            background=self.colors['bg'],
                            foreground=self.colors['fg'],
                            font=('Segoe UI', 10),
                            relief='flat',
                            padx=10,
                            pady=10,
                            height=15)
        text_widget.pack(expand=True, fill=tk.BOTH)
        
        # Configure scrollbar
        scrollbar.config(command=text_widget.yview)
        
        help_text = """
1. Creating a Hotkey:
   • Command Key: Enter a single character (e.g., 'C', 'S', '1')
   • Action: Enter one of the following:
      - Built-in commands: calc, chrome, edge
      - Any program path or system command

2. Using Hotkeys:
   • Press Ctrl + Shift + Alt + your command key
   • The action will execute immediately

3. Managing Hotkeys:
   • Delete: Click the × button next to any hotkey
   • Edit: Delete and re-add the hotkey with new settings

4. Startup Settings:
   • Click the Startup button to toggle auto-start with Windows
   • When ON, PowerKey will launch automatically at system startup
   • The setting persists between application restarts

5. Built-in Commands:
   • calc: Opens the system calculator
   • chrome: Launches Google Chrome browser

6. Custom Commands:
   • You can enter any valid system command or program path
   • Examples:
      - notepad.exe
      - "C:\\Program Files\\Some App\\App.exe"
      - cmd.exe /c echo Hello
      - explorer.exe "C:\\Documents"

7. Tips & Tricks:
   • Use simple, memorable keys for frequent actions
   • Test your commands before adding them as hotkeys
   • Keep track of your hotkey assignments
   • Avoid using system-reserved keys

8. Troubleshooting:
   • If a hotkey doesn't work:
      - Check if the program path is correct
      - Ensure you have necessary permissions
      - Verify the application isn't already running
   • For startup issues:
      - Check Windows Task Manager
      - Verify user account permissions
      - Check system event logs

9. Best Practices:
   • Keep your hotkey list organized
   • Regularly review and update your hotkeys
   • Back up your hotkey configurations
   • Use descriptive action names

10. System Requirements:
    • Windows: Full support for all features
    • Linux: Limited support (no Edge browser, different calculator)
    • Required permissions for startup feature
    • Administrative rights may be needed for some actions
"""
        
        # Insert help text
        text_widget.insert('1.0', help_text)
        
        # Make text widget read-only
        text_widget.configure(state='disabled')
        
        # Add a bottom button frame
        button_frame = ttk.Frame(help_frame)
        button_frame.pack(pady=(20, 0))
        
        close_button = ttk.Button(button_frame,
                                text="Close",
                                style='Accent.TButton',
                                command=help_window.destroy)
        close_button.pack()

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
            elif action.lower() == 'edge':
                if sys.platform == 'win32':
                    subprocess.Popen(['msedge'])
                else:
                    self.status_var.set("Microsoft Edge is not supported on this OS")
                    return
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
