import os
import unittest


# 状态机测试不需要真实键盘或窗口；dummy 后端无 Windows 键码定义。
os.environ.setdefault("PYNPUT_BACKEND", "dummy")
import Crosshair as mod
from pynput import keyboard


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = mod.OverlayState(3)
        self.f2 = object()
        self.esc = object()
        mod.POINTS_KEY = self.f2
        mod.EXIT_KEY = self.esc
        self.m = keyboard.KeyCode.from_vk(mod.MAP_VK)

    def tap_m(self):
        self.state.key_press(self.m)
        self.state.key_release(self.m)

    def test_map_toggle_repeat_and_escape(self):
        self.state.key_press(self.m)
        self.state.key_press(self.m)
        self.assertTrue(self.state.map_mode)
        self.assertFalse(self.state.show_crosshair)
        self.state.key_release(self.m)
        self.state.key_press(self.esc)
        self.assertFalse(self.state.map_mode)
        self.assertTrue(self.state.show_crosshair)
        self.tap_m()
        self.tap_m()
        self.assertFalse(self.state.map_mode)

    def test_f2_hold_and_scroll_only_in_points_mode(self):
        self.state.key_press(self.f2)
        self.assertFalse(self.state.show_points)
        self.tap_m()
        self.state.key_press(self.f2)
        self.assertTrue(self.state.show_points)
        self.state.scroll(-1)
        self.assertEqual(self.state.map_index, 1)
        self.state.scroll(1)
        self.assertEqual(self.state.map_index, 0)
        self.state.key_release(self.f2)
        self.assertFalse(self.state.show_points)
        self.state.scroll(-1)
        self.assertEqual(self.state.map_index, 0)

    def test_exit_releases_points_and_right_click_is_independent(self):
        self.tap_m()
        self.state.key_press(self.f2)
        self.state.key_press(self.esc)
        self.assertFalse(self.state.show_points)
        self.assertTrue(self.state.show_crosshair)
        self.state.right_held = True
        self.tap_m()
        self.tap_m()
        self.assertFalse(self.state.show_crosshair)
        self.state.right_held = False
        self.assertTrue(self.state.show_crosshair)

    def test_single_map_scroll_and_coordinates(self):
        self.assertEqual(len(mod.MAPS[0].points), 15)
        from map_layers import screen_points
        points = screen_points(1920, 1080, mod.MAPS[0])
        self.assertEqual(len(points), 15)
        self.assertTrue(all(0 <= x <= 1920 and 0 <= y <= 1080 for x, y in points))
        from map_layers import map_rect
        for layer in mod.MAPS:
            x, y, w, h = map_rect(1920, 1080, layer)
            self.assertTrue(0 <= x and 0 <= y and x + w <= 1920 and y + h <= 1080)
            self.assertEqual(len(screen_points(1920, 1080, layer)), len(layer.points))
        self.assertEqual([len(layer.points) for layer in mod.MAPS], [15, 15, 15, 15, 10])
        state = mod.OverlayState(len(mod.MAPS))
        state.map_mode = state.f2_held = True
        state.scroll(-1)
        self.assertEqual(state.map_index, 1)
        state.scroll(1)
        self.assertEqual(state.map_index, 0)


if __name__ == "__main__":
    unittest.main()
