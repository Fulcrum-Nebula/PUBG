# PUBG Crosshair

Windows / Python 3。运行 `Crosshair.bat`（只需 `pynput`；`py -3 -m pip install -r requirements.txt`）。

- M：切换地图模式（隐藏准星）；Esc：退出地图模式。
- 地图模式下**按住 F2**：只叠密室点位，背景透明；松开隐藏。
- 按住 F2 时滚轮：切换地图点位层；右键按住仍临时隐藏准星。

现有艾伦格与维寒迪点位。点位来源是用户给的参考图，经彩圈筛选及图片复核；仅收图例中“密室”类别，其他地图待核实后逐张加入。图像像素坐标定义在 `map_layers.py`，运行时不加载原图。

**校准限制**：默认按参考图居中、按屏幕的 85% 等比缩放；这只是上一版参考图显示时的位置，尚未与 PUBG 原生地图边界标定。若点位偏离，请改 `Crosshair.py` 中的 `MAP_SCALE`、`MAP_OFFSET_X`、`MAP_OFFSET_Y`；不同地图比例可能要分别校准。游戏地图缩放或拖动后，固定点位也不会跟着移动。程序不读游戏内存。

测试：`py -3 -m unittest -v test_crosshair`。Windows 游戏内叠加显示仍须实机验证。
