import tkinter as tk
import threading
from pynput import mouse

# ── 全局常量 ────────────────────────────────────────────────
COLOR        = "#00FF00"   # 准星颜色
DOT_RADIUS   = 0.5           # 中心点半径（像素）
INNER_RADIUS = 10           # 线段内圈半径（点边缘到线段起点的距离）
OUTER_RADIUS = 20          # 线段外圈半径（点边缘到线段终点的距离）
LINE_WIDTH   = 1           # 线段粗细（像素）   
# ────────────────────────────────────────────────────────────


class CrosshairOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crosshair")

        # 全屏透明窗口，置顶，穿透鼠标点击
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.overrideredirect(True)          # 无边框
        self.root.attributes("-topmost", True)    # 置顶
        self.root.attributes("-transparentcolor", "black")  # 黑色透明
        self.root.attributes("-alpha", 1.0)
        self.root.config(bg="black")
        self.root.wm_attributes("-disabled", True)         # 鼠标点击穿透

        self.canvas = tk.Canvas(
            self.root,
            width=screen_w,
            height=screen_h,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.cx = screen_w // 2
        self.cy = screen_h // 2
        self.visible = True

        self._draw()
        self._start_mouse_listener()

    # ── 绘制准星 ────────────────────────────────────────────
    def _draw(self):
        self.canvas.delete("crosshair")
        if not self.visible:
            return

        cx, cy = self.cx, self.cy
        r  = DOT_RADIUS
        i  = INNER_RADIUS
        o  = OUTER_RADIUS
        lw = LINE_WIDTH
        c  = COLOR
        tag = "crosshair"

        # 中心点
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=c, outline="", tags=tag
        )

        # 上
        self.canvas.create_line(cx, cy - i, cx, cy - o, fill=c, width=lw, tags=tag)
        # 下
        self.canvas.create_line(cx, cy + i, cx, cy + o, fill=c, width=lw, tags=tag)
        # 左
        self.canvas.create_line(cx - i, cy, cx - o, cy, fill=c, width=lw, tags=tag)
        # 右
        self.canvas.create_line(cx + i, cy, cx + o, cy, fill=c, width=lw, tags=tag)

    # ── 鼠标监听（右键控制隐藏/显示） ──────────────────────
    def _start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if button == mouse.Button.right:
                self.visible = not pressed
                self.root.after(0, self._draw)

        listener = mouse.Listener(on_click=on_click)
        listener.daemon = True
        listener.start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    CrosshairOverlay().run()
