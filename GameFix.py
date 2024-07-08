import tkinter as tk
from tkinter import ttk
import AutoHP
import keyboard
import threading
import queue
import win32gui
import win32con

class ExpandedGameFix:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x800")
        self.root.title("MapleLegends Fix")

        # Apply dark theme
        self.apply_dark_theme()

        self.scriptOn = tk.BooleanVar(value=False)
        self.scriptOnMessage = tk.StringVar(value="Script is OFF")
        self.red_level = tk.DoubleVar(value=0)
        self.blue_level = tk.DoubleVar(value=0)
        self.red_threshold = tk.IntVar(value=AutoHP.RED_THRESHOLD)
        self.blue_threshold = tk.IntVar(value=AutoHP.BLUE_THRESHOLD)
        self.target_window = tk.StringVar(value=AutoHP.TARGET_WINDOW_TITLE)
        self.x_offset = tk.IntVar(value=AutoHP.x_offset)
        self.y_offset = tk.IntVar(value=AutoHP.y_offset)
        self.width = tk.IntVar(value=AutoHP.width)
        self.height = tk.IntVar(value=AutoHP.height)

        self.log_queue = queue.Queue()

        self.overlay = None
        self.overlay_canvas = None

        self.create_widgets()

        # Bind the sliders to update the overlay
        self.x_offset.trace_add("write", self.update_overlay)
        self.y_offset.trace_add("write", self.update_overlay)
        self.width.trace_add("write", self.update_overlay)
        self.height.trace_add("write", self.update_overlay)

        self.x_offset.trace_add("write", self.round_value)
        self.y_offset.trace_add("write", self.round_value)
        self.width.trace_add("write", self.round_value)
        self.height.trace_add("write", self.round_value)

        keyboard.add_hotkey('F10', self.toggle)

        self.update_log()

    def apply_dark_theme(self):
        self.style = ttk.Style()
        self.style.theme_create("darktheme", parent="alt", settings={
            "TLabel": {"configure": {"background": "#2b2b2b", "foreground": "#ffffff"}},
            "TButton": {"configure": {"background": "#444444", "foreground": "#ffffff",
                                      "padding": 10, "font": ("Arial", 10, "bold")},
                        "map": {"background": [("active", "#666666")]}},
            "TEntry": {"configure": {"fieldbackground": "#444444", "foreground": "#ffffff",
                                     "insertcolor": "#ffffff"}},
            "TScale": {"configure": {"troughcolor": "#444444", "sliderlength": 20,
                                     "sliderrelief": "flat", "sliderthickness": 20}},
            "TLabelframe": {"configure": {"background": "#2b2b2b", "foreground": "#ffffff"}},
            "TLabelframe.Label": {"configure": {"background": "#2b2b2b", "foreground": "#ffffff"}},
        })
        self.style.theme_use("darktheme")
        # Configure the root window
        self.root.configure(bg="#1e1e1e")

    def create_widgets(self):
        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(status_frame, textvariable=self.scriptOnMessage, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, text="Health:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.red_level).pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, text="Mana:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.blue_level).pack(side=tk.LEFT, padx=5)

        # Control Frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Button(control_frame, text="Start Script", command=self.scriptStart).pack(side=tk.LEFT, padx=45)
        ttk.Button(control_frame, text="Stop Script", command=self.scriptStop).pack(side=tk.RIGHT, padx=45)

        # Threshold Frame
        threshold_frame = ttk.LabelFrame(self.root, text="Thresholds")
        threshold_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(threshold_frame, text="Red Threshold:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Scale(threshold_frame, from_=0, to=100, variable=self.red_threshold, command=self.update_thresholds).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(threshold_frame, textvariable=self.red_threshold).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(threshold_frame, text="Blue Threshold:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Scale(threshold_frame, from_=0, to=100, variable=self.blue_threshold, command=self.update_thresholds).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(threshold_frame, textvariable=self.blue_threshold).grid(row=1, column=2, padx=5, pady=5)

        # Settings Frame
        settings_frame = ttk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(settings_frame, text="Target Window:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.target_window).grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # X Offset
        ttk.Label(settings_frame, text="X Offset:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.x_offset, width=5).grid(row=1, column=1, padx=5, pady=5)
        ttk.Scale(settings_frame, from_=0, to=2000, variable=self.x_offset, orient="horizontal").grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        # Y Offset
        ttk.Label(settings_frame, text="Y Offset:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.y_offset, width=5).grid(row=2, column=1, padx=5, pady=5)
        ttk.Scale(settings_frame, from_=0, to=2000, variable=self.y_offset, orient="horizontal").grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Width
        ttk.Label(settings_frame, text="Width:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.width, width=5).grid(row=3, column=1, padx=5, pady=5)
        ttk.Scale(settings_frame, from_=1, to=1000, variable=self.width, orient="horizontal").grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        # Height
        ttk.Label(settings_frame, text="Height:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.height, width=5).grid(row=4, column=1, padx=5, pady=5)
        ttk.Scale(settings_frame, from_=1, to=1000, variable=self.height, orient="horizontal").grid(row=4, column=2, padx=5, pady=5, sticky="ew")

        ttk.Button(settings_frame, text="Update Settings", command=self.update_settings).grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Button(settings_frame, text="Toggle Overlay", command=self.toggle_overlay).grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Button(settings_frame, text="List All Windows", command=self.list_window_names).grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Make the second column (with the entry widgets) and third column (with the sliders) expandable
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(2, weight=3)

        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=10, bg="#2b2b2b", fg="#ffffff", insertbackground="#ffffff")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def round_value(self, *args):
        for var in (self.x_offset, self.y_offset, self.width, self.height):
            var.set(round(var.get()))

    def toggle_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.overlay_canvas = None
        else:
            self.create_overlay()

    def create_overlay(self):
        try:
            target_title = self.target_window.get()
            windows = self.find_window_wildcard(target_title)
            
            if windows:
                window = windows[0]  # Use the first matching window
                left, top, right, bottom = win32gui.GetWindowRect(window)
                x = left + self.x_offset.get()
                y = top + self.y_offset.get()
                width = self.width.get()
                height = self.height.get()

                self.overlay = tk.Toplevel(self.root)
                self.overlay.overrideredirect(True)
                self.overlay.attributes("-alpha", 0.3)
                self.overlay.attributes("-topmost", True)

                self.overlay_canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='yellow')
                self.overlay_canvas.pack(fill=tk.BOTH, expand=True)

                self.update_overlay()

                win32gui.SetWindowPos(self.overlay.winfo_id(), win32con.HWND_TOPMOST, x, y, width, height, 0)
            else:
                self.log_queue.put("Target window not found.")
        except Exception as e:
            self.log_queue.put(f"Error creating overlay: {str(e)}")

    def update_overlay(self, *args):
        if self.overlay and self.overlay_canvas:
            try:
                target_title = self.target_window.get()
                windows = self.find_window_wildcard(target_title)

                if windows:
                    window = windows[0]  # Use the first matching window
                    left, top, right, bottom = win32gui.GetWindowRect(window)

                    # Get values with error handling
                    try:
                        x = left + int(float(self.x_offset.get()))
                        y = top + int(float(self.y_offset.get()))
                        width = max(1, int(float(self.width.get())))
                        height = max(1, int(float(self.height.get())))
                    except ValueError:
                        # If conversion fails, just return without updating
                        return

                    self.overlay.geometry(f"{width}x{height}+{x}+{y}")
                    self.overlay_canvas.delete("all")
                    self.overlay_canvas.create_rectangle(2, 2, width-2, height-2, outline="red", width=4)

                    win32gui.SetWindowPos(self.overlay.winfo_id(), win32con.HWND_TOPMOST, x, y, width, height, 0)
                else:
                    self.log_queue.put("Target window not found during update.")
            except Exception as e:
                self.log_queue.put(f"Error updating overlay: {str(e)}")

    def scriptStart(self):
        self.scriptOn.set(True)
        self.scriptOnMessage.set("Script is ON")
        self.log_queue.put("Script started")
        self.scriptController()

    def scriptStop(self):
        self.scriptOn.set(False)
        self.scriptOnMessage.set("Script is OFF")
        self.log_queue.put("Script stopped")

    def scriptController(self):
        if self.scriptOn.get():
            thread = threading.Thread(target=self.run_auto_hp)
            thread.start()
        self.root.after(500, self.scriptController)

    def run_auto_hp(self):
        result = AutoHP.main()
        if result:
            self.red_level.set(result[0])
            self.blue_level.set(result[1])

    def toggle(self):
        if not self.scriptOn.get():
            self.scriptStart()
        else:
            self.scriptStop()

    def update_thresholds(self, *args):
        AutoHP.RED_THRESHOLD = self.red_threshold.get()
        AutoHP.BLUE_THRESHOLD = self.blue_threshold.get()
        self.log_queue.put(f"Thresholds updated - Red: {AutoHP.RED_THRESHOLD}, Blue: {AutoHP.BLUE_THRESHOLD}")

    def update_settings(self):
        AutoHP.TARGET_WINDOW_TITLE = self.target_window.get()
        AutoHP.x_offset = self.x_offset.get()
        AutoHP.y_offset = self.y_offset.get()
        AutoHP.width = self.width.get()
        AutoHP.height = self.height.get()
        self.log_queue.put("Settings updated")

    def update_log(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
        self.root.after(100, self.update_log)

    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    self.log_queue.put(f"Window: {window_text}")
        win32gui.EnumWindows(winEnumHandler, None)

    def find_window_wildcard(self, wildcard):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if wildcard.lower() in window_text.lower():
                    hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    def show_selected_area(self):
        try:
            target_title = self.target_window.get()
            self.log_queue.put(f"Searching for window: {target_title}")
            
            windows = find_window_wildcard(target_title)
            if windows:
                    window = windows[0]  # Use the first matching window
                    left, top, right, bottom = win32gui.GetWindowRect(window)
                    x = left + self.x_offset.get()
                    y = top + self.y_offset.get()
                    width = self.width.get()
                    height = self.height.get()
                    self.log_queue.put(f"Window found. Position: ({left}, {top}, {right}, {bottom})")
                    self.log_queue.put(f"Selected area: ({x}, {y}, {width}, {height})")
                    # Create a transparent window to show the selected area
                    overlay = tk.Toplevel(self.root)
                    overlay.geometry(f"{width}x{height}+{x}+{y}")
                    overlay.overrideredirect(True)
                    overlay.attributes("-alpha", 0.5)
                    overlay.attributes("-topmost", True)
                    canvas = tk.Canvas(overlay, highlightthickness=0, bg='yellow')
                    canvas.pack(fill=tk.BOTH, expand=True)
                    canvas.create_rectangle(2, 2, width-2, height-2, outline="red", width=4)
                    overlay.lift()
                    overlay.update()
                    win32gui.SetWindowPos(overlay.winfo_id(), win32con.HWND_TOPMOST, x, y, width, height, 0)
                    self.log_queue.put("Overlay created and should be visible")
                    self.root.after(3000, overlay.destroy)
            else:
                    self.log_queue.put("Target window not found. Listing all visible windows:")
                    self.list_window_names()
        except Exception as e:
            self.log_queue.put(f"Error showing selected area: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpandedGameFix(root)
    root.mainloop()