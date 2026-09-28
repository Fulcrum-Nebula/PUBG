import queue
import tkinter as tk
from pynput import keyboard, mouse
from map_layers import MAPS, screen_points

COLOR = "#00FF00"
DOT_RADIUS = 0.5
INNER_RADIUS = 10
OUTER_RADIUS = 20
LINE_WIDTH = 1

# 屏幕坐标校准：默认沿用此前参考图的居中等比缩放。
# 游戏内地图若位置或大小不同，调整下面三项；不读游戏内存。
MAP_SCALE = 0.85
MAP_OFFSET_X = 0
MAP_OFFSET_Y = 0
POINT_RADIUS = 9
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
        self.screen_w, self.screen_h = screen_w, screen_h
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
            layer = MAPS[self.state.map_index]
            for x, y in screen_points(self.screen_w, self.screen_h, layer,
                                      MAP_SCALE, MAP_OFFSET_X, MAP_OFFSET_Y):
                r = POINT_RADIUS
                # 黑色画布为窗口色键；只绘制标记，底图透出。
                self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                        outline="#00FFFF", width=3, tags="overlay")
                self.canvas.create_oval(x-2, y-2, x+2, y+2,
                                        fill="#FF4040", outline="", tags="overlay")
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