"""透明点位层数据。坐标来自 950×966 艾伦格参考图的彩圈像素中心。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MapLayer:
    name: str
    width: int
    height: int
    points: tuple[tuple[int, int], ...]


# 原图圈的蓝色连通域中心（取整）；绝非 PUBG 内存中的世界坐标。
MAPS = (
    MapLayer("艾伦格 · 密室", 950, 966, (
        (584, 57), (124, 198), (461, 217), (755, 230), (273, 247),
        (625, 395), (137, 409), (324, 435), (526, 517), (783, 575),
        (287, 603), (110, 652), (495, 700), (360, 796), (650, 800),
    )),
    # 米拉玛：红色分段空心环；不含加油站、载具与滑翔机图标。
    MapLayer("米拉玛 · 密室", 1280, 1280, (
        (515, 168), (724, 226), (281, 266), (988, 306), (439, 392),
        (809, 501), (219, 517), (603, 613), (973, 667), (421, 782),
        (696, 815), (207, 834), (824, 985), (509, 1044), (219, 1136),
    )),
    # 泰戈图像左侧 x=0..395 为说明面板；坐标已减去 396。
    # 原图红环和黄环均位于 Secret Room Locations 图内，颜色含义未注明。
    MapLayer("泰戈 · 密室", 884, 868, (
        (109, 81), (258, 103), (540, 145), (800, 193), (61, 359),
        (826, 358), (488, 558), (54, 594), (736, 633), (553, 738),
        (236, 745), (729, 837), (380, 180), (90, 272), (689, 422),
    )),
    # 荣都：地图底部原图被裁去约 50px（推断），先按 1280×1230 原图坐标绘制。
    # 仅红色分段环，不含右下角图例；与游戏地图的精确变换待校准。
    MapLayer("荣都 · 密室", 1280, 1230, (
        (911, 141), (476, 146), (231, 213), (790, 322), (595, 417),
        (1106, 431), (223, 509), (1041, 671), (732, 690), (226, 753),
        (473, 807), (895, 955), (197, 1021), (531, 1099), (776, 1159),
    )),
    # 维寒迪：仅取图例 SECRET ROOMS 对应的青色虚线环；不含熊洞、实验营地。
    MapLayer("维寒迪 · 密室", 1280, 1280, (
        (850, 207), (433, 246), (982, 385), (644, 504), (218, 603),
        (1075, 610), (739, 777), (374, 885), (955, 923), (619, 1026),
    )),
)


def map_rect(screen_w, screen_h, layer, scale=0.85, offset_x=0, offset_y=0):
    """默认按此前参考图的居中等比缩放；手调 scale/offset 以匹配游戏地图。"""
    factor = min(screen_w * scale / layer.width, screen_h * scale / layer.height, 1.0)
    w, h = layer.width * factor, layer.height * factor
    return ((screen_w - w) / 2 + offset_x, (screen_h - h) / 2 + offset_y, w, h)


def screen_points(screen_w, screen_h, layer, scale=0.85, offset_x=0, offset_y=0):
    x0, y0, w, h = map_rect(screen_w, screen_h, layer, scale, offset_x, offset_y)
    return tuple((x0 + x * w / layer.width, y0 + y * h / layer.height)
                 for x, y in layer.points)
