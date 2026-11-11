from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.switch import Switch
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import json
import os

try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                         Permission.WRITE_EXTERNAL_STORAGE])
    ANDROID = True
except Exception:
    ANDROID = False

SETTINGS_FILE = "settings.json"


class Calculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.expression = ""
        self.dark = True
        self.btn_bg = '#2E86DE'
        self.btn_fg = '#FFFFFF'
        self.wallpaper = None
        self.load_settings()
        self.apply_theme()

        self.bg = Image(allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)
        if self.wallpaper and os.path.exists(self.wallpaper):
            self.bg.source = self.wallpaper

        self.display = Label(
            text="0", font_size='40sp', halign='right', valign='middle',
            size_hint=(1, 0.22), color=self.disp_color, padding=(10, 0)
        )
        self.display.bind(size=lambda *a: setattr(self.display, 'text_size', (self.display.width, None)))
        self.add_widget(self.display)

        self.grid = GridLayout(cols=4, size_hint=(1, 0.70), spacing=4, padding=4)
        keys = ['C', '⌫', '⚙', '/',
                '7', '8', '9', '*',
                '4', '5', '6', '-',
                '1', '2', '3', '+',
                '0', '.', '=']
        for k in keys:
            self.grid.add_widget(self._make_button(k))
        self.add_widget(self.grid)

        eq = self._make_button('=')
        eq.size_hint_y = None
        eq.height = 60
        self.add_widget(eq)

    def apply_theme(self):
        if self.dark:
            self.main_bg = get_color_from_hex('#121212')
            self.disp_color = get_color_from_hex('#FFFFFF')
        else:
            self.main_bg = get_color_from_hex('#F5F5F5')
            self.disp_color = get_color_from_hex('#000000')
        Window.clearcolor = self.main_bg

    def _make_button(self, text):
        btn = Button(
            text=text, font_size='24sp',
            background_normal='',
            background_color=get_color_from_hex(self.btn_bg),
            color=get_color_from_hex(self.btn_fg),
        )
        btn.bind(on_release=lambda b, t=text: self.on_key(t))
        return btn

    def on_key(self, key):
        if key == 'C':
            self.expression = ""
        elif key == '⌫':
            self.expression = self.expression[:-1]
        elif key == '=':
            self._calculate(); return
        elif key == '⚙':
            self.open_settings(); return
        else:
            self.expression += key
        self.display.text = self.expression or "0"

    def _calculate(self):
        try:
            allowed = "0123456789+-*/.()"
            if self.expression and all(c in allowed for c in self.expression):
                result = str(eval(self.expression))
                self.display.text = result
                self.expression = result
            else:
                self.display.text = "Ошибка"; self.expression = ""
        except Exception:
            self.display.text = "Ошибка"; self.expression = ""

    def open_settings(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        theme_row = BoxLayout(size_hint=(1, 0.2), spacing=10)
        theme_row.add_widget(Label(text="Тёмная тема"))
        sw = Switch(active=self.dark)
        sw.bind(active=self.toggle_theme)
        theme_row.add_widget(sw)

        btn_color = Button(text="Цвет кнопок", size_hint=(1, 0.2))
        btn_color.bind(on_release=lambda *a: self.pick_color('btn_bg'))

        btn_fg = Button(text="Цвет текста кнопок", size_hint=(1, 0.2))
        btn_fg.bind(on_release=lambda *a: self.pick_color('btn_fg'))

        btn_wall = Button(text="Обои из галереи", size_hint=(1, 0.2))
        btn_wall.bind(on_release=lambda *a: self.pick_wallpaper())

        close = Button(text="Закрыть", size_hint=(1, 0.2))
        popup = Popup(title="Настройки", content=content, size_hint=(0.9, 0.75))
        close.bind(on_release=popup.dismiss)

        content.add_widget(theme_row)
        content.add_widget(btn_color)
        content.add_widget(btn_fg)
        content.add_widget(btn_wall)
        content.add_widget(close)
        popup.open()

    def toggle_theme(self, instance, value):
        self.dark = value
        self.apply_theme()
        self.display.color = self.disp_color
        self.save_settings()

    def pick_color(self, attr):
        content = BoxLayout(orientation='vertical')
        cp = ColorPicker()
        ok = Button(text="OK", size_hint=(1, 0.15))
        content.add_widget(cp); content.add_widget(ok)
        popup = Popup(title="Выбор цвета", content=content, size_hint=(0.9, 0.9))

        def apply(*a):
            r, g, b, _ = cp.color
            hex_color = '#{:02X}{:02X}{:02X}'.format(int(r*255), int(g*255), int(b*255))
            setattr(self, attr, hex_color)
            self._repaint_buttons()
            self.save_settings()
            popup.dismiss()

        ok.bind(on_release=apply)
        popup.open()

    def pick_wallpaper(self):
        start_path = "/storage/emulated/0" if ANDROID else "."
        content = BoxLayout(orientation='vertical')
        fc = FileChooserListView(path=start_path,
                                 filters=['*.png', '*.jpg', '*.jpeg'])
        btn = Button(text="Выбрать", size_hint=(1, 0.15))
        content.add_widget(fc); content.add_widget(btn)
        popup = Popup(title="Выбери обои", content=content, size_hint=(0.95, 0.95))

        def select(*a):
            if fc.selection:
                self.wallpaper = fc.selection[0]
                self.bg.source = self.wallpaper
                self.bg.reload()
                self.save_settings()
            popup.dismiss()

        btn.bind(on_release=select)
        popup.open()

    def _repaint_buttons(self):
        for layout in [self.grid]:
            for b in layout.children:
                if isinstance(b, Button):
                    b.background_color = get_color_from_hex(self.btn_bg)
                    b.color = get_color_from_hex(self.btn_fg)

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({
                    "dark": self.dark,
                    "btn_bg": self.btn_bg,
                    "btn_fg": self.btn_fg,
                    "wallpaper": self.wallpaper,
                }, f)
        except Exception:
            pass

    def load_settings(self):
        try:
            with open(SETTINGS_FILE) as f:
                d = json.load(f)
                self.dark = d.get("dark", True)
                self.btn_bg = d.get("btn_bg", '#2E86DE')
                self.btn_fg = d.get("btn_fg", '#FFFFFF')
                self.wallpaper = d.get("wallpaper", None)
        except Exception:
            pass


class CustomCalculatorApp(App):
    def build(self):
        self.title = "Custom Calculator"
        return Calculator()


if __name__ == '__main__':
    CustomCalculatorApp().run()
