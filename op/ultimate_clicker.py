import customtkinter as ctk
import threading
import time
import random
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener, KeyCode

# ==========================================
# ⚙️ THEME SETUP
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UltimateAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Auto Clicker - Pro Edition")
        self.geometry("450x680") # Increased height for new features
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # System Variables
        self.clicking = False
        self.binding_hotkey = False
        self.mouse = MouseController()
        self.hotkey = KeyCode(char='f8')
        self.click_count = 0
        
        self.build_ui()
        self.start_listener_thread()

    def build_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="ULTIMATE CLICKER", font=ctk.CTkFont(size=22, weight="bold"))
        self.header.pack(pady=(15, 5))
        
        self.status_label = ctk.CTkLabel(self, text="🔴 STOPPED", text_color="#ff4c4c", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(pady=(0, 10))

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=420, height=420)
        self.tabview.pack(padx=15, pady=5)
        self.tabview.add("Main")
        self.tabview.add("Settings")
        self.tabview.add("Security")

        self.build_main_tab()
        self.build_settings_tab()
        self.build_security_tab()

        # --- START & STOP BUTTONS ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self.action_frame, text="▶ START", fg_color="green", hover_color="darkgreen", 
            font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.start_clicking
        )
        self.start_button.grid(row=0, column=0, padx=15)

        self.stop_button = ctk.CTkButton(
            self.action_frame, text="⏹ STOP", fg_color="#d93636", hover_color="#8b0000", 
            font=ctk.CTkFont(weight="bold"), width=140, height=40, command=self.stop_clicking
        )
        self.stop_button.grid(row=0, column=1, padx=15)

    def build_main_tab(self):
        tab = self.tabview.tab("Main")

        # --- INTERVAL ---
        ctk.CTkLabel(tab, text="Click Interval", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        interval_frame = ctk.CTkFrame(tab, fg_color="transparent")
        interval_frame.pack(pady=5)

        self.hrs_var, self.mins_var = ctk.StringVar(value="0"), ctk.StringVar(value="0")
        self.secs_var, self.ms_var = ctk.StringVar(value="0"), ctk.StringVar(value="100") 

        ctk.CTkEntry(interval_frame, textvariable=self.hrs_var, width=45).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(interval_frame, text="h").grid(row=0, column=1, padx=(0, 5))
        ctk.CTkEntry(interval_frame, textvariable=self.mins_var, width=45).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(interval_frame, text="m").grid(row=0, column=3, padx=(0, 5))
        ctk.CTkEntry(interval_frame, textvariable=self.secs_var, width=45).grid(row=0, column=4, padx=2)
        ctk.CTkLabel(interval_frame, text="s").grid(row=0, column=5, padx=(0, 5))
        ctk.CTkEntry(interval_frame, textvariable=self.ms_var, width=55).grid(row=0, column=6, padx=2)
        ctk.CTkLabel(interval_frame, text="ms").grid(row=0, column=7)

        # --- OPTIONS ---
        options_frame = ctk.CTkFrame(tab, fg_color="transparent")
        options_frame.pack(pady=10)

        ctk.CTkLabel(options_frame, text="Mouse Button:").grid(row=0, column=0, padx=5)
        self.btn_var = ctk.StringVar(value="Left")
        ctk.CTkOptionMenu(options_frame, variable=self.btn_var, values=["Left", "Right", "Middle"], width=100).grid(row=0, column=1, padx=5)

        ctk.CTkLabel(options_frame, text="Click Type:").grid(row=1, column=0, padx=5, pady=5)
        self.type_var = ctk.StringVar(value="Single")
        ctk.CTkOptionMenu(options_frame, variable=self.type_var, values=["Single", "Double"], width=100).grid(row=1, column=1, padx=5, pady=5)

        # --- REPEAT MODE ---
        ctk.CTkLabel(tab, text="Click Limit", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))
        repeat_frame = ctk.CTkFrame(tab, fg_color="transparent")
        repeat_frame.pack(pady=5)

        self.repeat_mode = ctk.StringVar(value="infinite")
        ctk.CTkRadioButton(repeat_frame, text="Repeat until stopped", variable=self.repeat_mode, value="infinite").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkRadioButton(repeat_frame, text="Repeat times:", variable=self.repeat_mode, value="limited").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.repeat_count_var = ctk.StringVar(value="100")
        ctk.CTkEntry(repeat_frame, textvariable=self.repeat_count_var, width=70).grid(row=1, column=1)

    def build_settings_tab(self):
        tab = self.tabview.tab("Settings")

        # --- HOTKEY BINDER ---
        ctk.CTkLabel(tab, text="Trigger Settings", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        self.trigger_type = ctk.StringVar(value="toggle")
        ctk.CTkRadioButton(tab, text="Toggle (Press once to start, once to stop)", variable=self.trigger_type, value="toggle").pack(pady=5)
        ctk.CTkRadioButton(tab, text="Hold (Rapid-fire only while holding key)", variable=self.trigger_type, value="hold").pack(pady=5)

        self.bind_btn = ctk.CTkButton(tab, text="Current Hotkey: F8 (Click to Rebind)", command=self.start_bind)
        self.bind_btn.pack(pady=15)

        # --- WINDOW SETTINGS ---
        ctk.CTkLabel(tab, text="Window", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.topmost_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(tab, text="Keep Window Always on Top", variable=self.topmost_var, command=self.toggle_topmost).pack(pady=5)

    def build_security_tab(self):
        tab = self.tabview.tab("Security")

        # --- CURSOR POSITION ---
        ctk.CTkLabel(tab, text="Cursor Locking", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        self.pos_mode = ctk.StringVar(value="current")
        ctk.CTkRadioButton(tab, text="Current mouse location", variable=self.pos_mode, value="current").pack(pady=5)
        
        pos_frame = ctk.CTkFrame(tab, fg_color="transparent")
        pos_frame.pack(pady=5)
        ctk.CTkRadioButton(pos_frame, text="Pick exact coordinates", variable=self.pos_mode, value="custom").grid(row=0, column=0, padx=5)
        self.x_var, self.y_var = ctk.StringVar(value="0"), ctk.StringVar(value="0")
        ctk.CTkLabel(pos_frame, text="X:").grid(row=0, column=1)
        ctk.CTkEntry(pos_frame, textvariable=self.x_var, width=50).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(pos_frame, text="Y:").grid(row=0, column=3)
        ctk.CTkEntry(pos_frame, textvariable=self.y_var, width=50).grid(row=0, column=4, padx=5)

        # --- ANTI-DETECT ---
        ctk.CTkLabel(tab, text="Anti-Ban Protection", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        
        self.humanize_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(tab, text="Timing Jitter (Randomize interval by ±15%)", variable=self.humanize_var).pack(pady=10)

        jitter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        jitter_frame.pack(pady=5)
        ctk.CTkLabel(jitter_frame, text="Spatial Jitter (Randomize cursor position by Pixels):").grid(row=0, column=0, padx=5)
        self.spatial_jitter_var = ctk.StringVar(value="0")
        ctk.CTkEntry(jitter_frame, textvariable=self.spatial_jitter_var, width=50).grid(row=0, column=1)

    # ==========================================
    # 🎮 CORE LOGIC & ENGINE
    # ==========================================
    def toggle_topmost(self):
        self.attributes("-topmost", self.topmost_var.get())

    def start_bind(self):
        self.binding_hotkey = True
        self.bind_btn.configure(text="Press any key to bind...", fg_color="orange")

    def get_interval(self):
        try:
            return (float(self.hrs_var.get() or 0) * 3600) + (float(self.mins_var.get() or 0) * 60) + float(self.secs_var.get() or 0) + (float(self.ms_var.get() or 0) / 1000.0)
        except ValueError:
            return 0.1 

    def clicker_loop(self):
        button_map = {"Left": Button.left, "Right": Button.right, "Middle": Button.middle}
        active_btn = button_map.get(self.btn_var.get(), Button.left)
        is_double = (self.type_var.get() == "Double")
        limit_clicks = (self.repeat_mode.get() == "limited")
        
        try: max_clicks = int(self.repeat_count_var.get() or 0)
        except: max_clicks = 0

        use_custom_pos = (self.pos_mode.get() == "custom")
        try: custom_x, custom_y = int(self.x_var.get()), int(self.y_var.get())
        except: use_custom_pos = False

        try: spat_jitter = int(self.spatial_jitter_var.get())
        except: spat_jitter = 0

        self.click_count = 0
        base_interval = self.get_interval()

        while self.clicking:
            if limit_clicks and self.click_count >= max_clicks:
                self.after(0, self.stop_clicking)
                break

            # Handle Custom Cursor Position & Spatial Jitter
            if use_custom_pos:
                target_x, target_y = custom_x, custom_y
            else:
                target_x, target_y = self.mouse.position

            if spat_jitter > 0:
                target_x += random.randint(-spat_jitter, spat_jitter)
                target_y += random.randint(-spat_jitter, spat_jitter)
            
            # Only update mouse position if we are forcing coordinates or adding jitter
            if use_custom_pos or spat_jitter > 0:
                self.mouse.position = (target_x, target_y)

            self.mouse.click(active_btn, 2 if is_double else 1)
            self.click_count += 1

            delay = base_interval
            if self.humanize_var.get() and base_interval > 0:
                delay = base_interval * random.uniform(0.85, 1.15)
            
            time.sleep(delay)

    def start_clicking(self):
        if self.clicking or self.get_interval() <= 0: return 
        self.clicking = True
        
        # Update text dynamically based on the hotkey
        key_name = str(self.hotkey).replace("'", "")
        self.status_label.configure(text=f"🟢 RUNNING ({key_name} to Stop)", text_color="#4cff4c")
        threading.Thread(target=self.clicker_loop, daemon=True).start()

    def stop_clicking(self):
        self.clicking = False
        key_name = str(self.hotkey).replace("'", "")
        self.status_label.configure(text=f"🔴 STOPPED ({key_name} to Start)", text_color="#ff4c4c")

    def toggle_state(self):
        if self.clicking: self.stop_clicking()
        else: self.start_clicking()

    # --- KEYBOARD LISTENER LOGIC ---
    def on_press(self, key):
        if self.binding_hotkey:
            self.hotkey = key
            self.binding_hotkey = False
            key_name = str(key).replace("'", "")
            self.bind_btn.configure(text=f"Current Hotkey: {key_name} (Click to Rebind)", fg_color=["#3a7ebf", "#1f538d"])
            self.stop_clicking() # Refresh status text
            return

        if key == self.hotkey:
            if self.trigger_type.get() == "toggle":
                self.after(0, self.toggle_state)
            elif self.trigger_type.get() == "hold":
                if not self.clicking:
                    self.after(0, self.start_clicking)

    def on_release(self, key):
        if key == self.hotkey and self.trigger_type.get() == "hold":
            self.after(0, self.stop_clicking)

    def start_listener_thread(self):
        listener = Listener(on_press=self.on_press, on_release=self.on_release)
        listener.daemon = True
        listener.start()

if __name__ == "__main__":
    app = UltimateAutoClicker()
    app.mainloop()