import queue
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk
from pynput import keyboard, mouse

COLOR = "#00FF00"
DOT_RADIUS = 0.5
INNER_RADIUS = 10
OUTER_RADIUS = 20
LINE_WIDTH = 1

# 顺序就是滚轮切换顺序；后续图片直接放进 maps/ 并在这里登记。
MAPS = [("艾伦格 · 密室", "maps/erangel-secret-rooms.png")]
MAP_KEY = "m"
MAP_VK = 0x4D  # Windows 虚拟键码：M；输入法使 char=None 时仍能识别
POINTS_KEY = keyboard.Key.f2
EXIT_KEY = keyboard.Key.esc


class OverlayState:
    """独立于图形界面的状态机，键盘与鼠标事件只由 Tk 主线程消费。"""

    def __init__(self, map_count):
        self.map_count = map_count
        self.map_index = 0
        self.map_mode = False
        self.f2_held = False
        self.right_held = False
        self.m_held = False

    @property
    def show_crosshair(self):
        return not (self.map_mode or self.right_held)

    @property
    def show_points(self):
        return self.map_mode and self.f2_held

    def key_press(self, key):
        if getattr(key, "vk", None) == MAP_VK or (getattr(key, "char", None) or "").lower() == MAP_KEY:
            if not self.m_held:  # 避免按住 M 时按键自动重复切换
                self.m_held = True
                self.map_mode = not self.map_mode
                if not self.map_mode:
                    self.f2_held = False
        elif key == EXIT_KEY and self.map_mode:
            self.map_mode = False
            self.f2_held = False
        elif key == POINTS_KEY and self.map_mode:
            self.f2_held = True

    def key_release(self, key):
        if getattr(key, "vk", None) == MAP_VK or (getattr(key, "char", None) or "").lower() == MAP_KEY:
            self.m_held = False
        elif key == POINTS_KEY:
            self.f2_held = False

    def scroll(self, direction):
        if self.show_points and self.map_count > 1:
            self.map_index = (self.map_index + (1 if direction < 0 else -1)) % self.map_count


class CrosshairOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crosshair")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.config(bg="black")
        self.root.wm_attributes("-disabled", True)
        self.canvas = tk.Canvas(self.root, width=screen_w, height=screen_h,
                                bg="black", highlightthickness=0)
        self.canvas.pack()
        self.cx, self.cy = screen_w // 2, screen_h // 2
        self.state = OverlayState(len(MAPS))
        self.events = queue.Queue()
        self.images = []  # 持有 PhotoImage 引用，否则 Tk 会释放图片
        for name, filename in MAPS:
            path = Path(__file__).resolve().parent / filename
            with Image.open(path) as source:
                image = source.convert("RGB")
                image.thumbnail((int(screen_w * .85), int(screen_h * .85)), Image.Resampling.LANCZOS)
                self.images.append(ImageTk.PhotoImage(image, master=self.root))
        self._draw()
        self.keyboard_listener = keyboard.Listener(
            on_press=lambda key: self.events.put(("press", key)),
            on_release=lambda key: self.events.put(("release", key)))
        self.mouse_listener = mouse.Listener(
            on_click=lambda x, y, button, pressed: self.events.put(("click", button, pressed)),
            on_scroll=lambda x, y, dx, dy: self.events.put(("scroll", dy)))
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.root.after(15, self._consume_events)

    def _consume_events(self):
        changed = False
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            kind = event[0]
            if kind == "press":
                self.state.key_press(event[1])
            elif kind == "release":
                self.state.key_release(event[1])
            elif kind == "click" and event[1] == mouse.Button.right:
                self.state.right_held = event[2]
            elif kind == "scroll":
                self.state.scroll(event[1])
            changed = True
        if changed:
            self._draw()
        self.root.after(15, self._consume_events)

    def _draw(self):
        self.canvas.delete("overlay")
        if self.state.show_points:
            name, _ = MAPS[self.state.map_index]
            self.canvas.create_image(self.cx, self.cy,
                                     image=self.images[self.state.map_index], tags="overlay")
            self.canvas.create_text(self.cx, 35, text=f"{name}  |  F2 松开隐藏 · 滚轮切图",
                                    fill="#00FF00", font=("Arial", 16, "bold"), tags="overlay")
        if self.state.show_crosshair:
            cx, cy = self.cx, self.cy
            r, i, o, lw = DOT_RADIUS, INNER_RADIUS, OUTER_RADIUS, LINE_WIDTH
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=COLOR, outline="", tags="overlay")
            for x1, y1, x2, y2 in ((cx, cy-i, cx, cy-o), (cx, cy+i, cx, cy+o),
                                   (cx-i, cy, cx-o, cy), (cx+i, cy, cx+o, cy)):
                self.canvas.create_line(x1, y1, x2, y2, fill=COLOR, width=lw, tags="overlay")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.keyboard_listener.stop()
            self.mouse_listener.stop()


if __name__ == "__main__":
    CrosshairOverlay().run()