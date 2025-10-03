import requests
import time
import os
import threading
import random
import subprocess

from kivy.clock import Clock # type: ignore
from kivy.lang import Builder # type: ignore
from kivy.metrics import dp # type: ignore
from kivy.core.window import Window # type: ignore
from kivy.config import Config # type: ignore
from kivy.animation import Animation # type: ignore
from kivy.uix.label import Label # type: ignore
from kivy.uix.screenmanager import Screen, ScreenManager # type: ignore
from kivy.app import App # type: ignore

Config.set("input", "mouse", "mouse,multitouch_on_demand")

INPUT_FILE = r"usernames.txt"
OUTPUT_FILE = "available.txt"
SLEEP_BETWEEN = 1.0
MAX_RETRIES = 3

Window.clearcolor = (0, 0, 0, 1)

if not os.path.isfile(INPUT_FILE):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")


def check_username(username: str) -> bool:
    url = f"https://fragment.com/username/{username}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 429:
            raise Exception("Rate Limited (HTTP 429)")
        elif resp.status_code >= 500:
            raise Exception(f"Server Error {resp.status_code}")
        body = resp.text.lower()
    except Exception as e:
        raise Exception(f"Mistake while asking for {username}: {e}")
    return "unavailable" in body


KV = r"""
ScreenManager:
    SplashScreen:
    MainScreen:

<SplashScreen>:
    name: "splash"
    FloatLayout:
        id: splash_root
        canvas.before:
            Color:
                rgba: 0,0,0,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            id: loading_label
            text: "TG Username Checker"
            font_size: dp(28)
            bold: True
            color: 1,1,1,1
            opacity: 0
            size_hint: None, None
            pos_hint: {"center_x": .5, "center_y": .6}

        AnchorLayout:
            anchor_x: "center"
            anchor_y: "bottom"
            padding: dp(12)
            Label:
                id: made_label
                text: "Made by Virgin, @operatingsecure on telegram"
                font_size: dp(16)
                color: 1,1,1,0.6
                opacity: 0
                size_hint: None, None

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(12), 0
            canvas.before:
                Color:
                    rgba: 0.03,0.03,0.03,1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "This Tool is not working 100%, be beware of this. 99% success rate."
                color: 1,1,1,1
                bold: True
                halign: "left"
                valign: "middle"
                text_size: self.size

        BoxLayout:
            orientation: "horizontal"
            spacing: dp(12)
            padding: dp(12)

            BoxLayout:
                orientation: "vertical"
                size_hint_x: 0.35
                padding: dp(6)
                canvas.before:
                    Color:
                        rgba: 0,0,0,1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.17,0.17,0.17,1
                    Line:
                        width: 1.0
                        rectangle: self.x, self.y, self.width, self.height

                Label:
                    text: "Available"
                    size_hint_y: None
                    height: dp(40)
                    color: 1,1,1,1
                    bold: True
                    halign: "center"
                    valign: "middle"
                    text_size: self.size

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: available_container
                        cols: 1
                        spacing: dp(4)
                        size_hint_y: None
                        height: self.minimum_height
                        row_default_height: dp(28)

            BoxLayout:
                orientation: "vertical"
                padding: dp(8)
                spacing: dp(8)
                canvas.before:
                    Color:
                        rgba: 0,0,0,1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.17,0.17,0.17,1
                    Line:
                        width: 1.0
                        rectangle: self.x, self.y, self.width, self.height

                ProgressBar:
                    id: progress
                    max: 100
                    value: 0
                    size_hint_y: None
                    height: dp(6)

                Label:
                    text: "Logs"
                    size_hint_y: None
                    height: dp(30)
                    color: 1,1,1,1
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: log_container
                        cols: 1
                        spacing: dp(4)
                        size_hint_y: None
                        height: self.minimum_height
                        row_default_height: dp(28)

                BoxLayout:
                    size_hint_y: None
                    height: dp(64)
                    padding: 0
                    Widget:
                    Button:
                        id: start_btn
                        text: "Start Checking"
                        size_hint: None, None
                        width: dp(220)
                        height: dp(42)
                        background_normal: ""
                        background_color: 0,0,0,0
                        color: 1,1,1,1
                        canvas.before:
                            Color:
                                rgba: 1,1,1,1
                            Line:
                                width: 1.0
                                rectangle: (self.x+2, self.y+2, self.width-4, self.height-4)
                        on_release: root.start_checking()
                    Widget:
"""


class SnowDot(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_snow = True


class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self._post_init, 0)

    def _post_init(self, dt):
        self._flakes = []
        if "loading_label" in self.ids:
            lbl = self.ids.loading_label
            lbl.texture_update()
            lbl.size = (lbl.texture_size[0], lbl.texture_size[1])
            anim = (
                Animation(opacity=1, d=1.2, t="out_quad") +
                Animation(d=1.5) +
                Animation(opacity=0, d=1.0, t="in_quad")
            )
            anim.start(lbl)
        if "made_label" in self.ids:
            ml = self.ids.made_label
            ml.texture_update()
            ml.size = (ml.texture_size[0], ml.texture_size[1])
            Clock.schedule_once(lambda dt: (
                Animation(opacity=1, d=1.5, t="out_quad") +
                Animation(d=2.0) +
                Animation(opacity=0, d=1.2, t="in_quad")
            ).start(ml), 1.0)
        self._snow_event = Clock.schedule_interval(self.spawn_snow_dot, 0.12)
        Clock.schedule_once(self.goto_main, 4.0)

    def spawn_snow_dot(self, dt):
        root = self.ids.get("splash_root")
        if not root:
            return
        fs = random.randint(8, 16)
        x = random.randint(0, max(0, Window.width - 20))
        start_y = Window.height + 10
        dot = SnowDot(text="•", font_size=fs, color=(1, 1, 1, random.uniform(0.45, 0.95)), size_hint=(None, None))
        dot.texture_update()
        dot.size = (dot.texture_size[0] + 4, dot.texture_size[1] + 4)
        dot.pos = (x, start_y)
        root.add_widget(dot)
        self._flakes.append(dot)
        end_y = -50
        duration = random.uniform(3.0, 6.0)
        drift_x = x + random.randint(-30, 30)
        anim = Animation(y=end_y, x=drift_x, d=duration, t="linear")
        anim.bind(on_complete=lambda a, w: self._remove_flake(w))
        anim.start(dot)

    def _remove_flake(self, widget):
        root = self.ids.get("splash_root")
        try:
            if hasattr(self, "_flakes") and widget in self._flakes:
                self._flakes.remove(widget)
            if root and widget in list(root.children):
                root.remove_widget(widget)
        except Exception:
            pass

    def goto_main(self, dt):
        try:
            if hasattr(self, "_snow_event"):
                self._snow_event.cancel()
        except Exception:
            pass
        root = self.ids.get("splash_root")
        if root:
            for flake in list(getattr(self, "_flakes", [])):
                try:
                    if flake.parent is not None:
                        root.remove_widget(flake)
                except Exception:
                    pass
            self._flakes = []
        if self.manager:
            self.manager.current = "main"

        Clock.schedule_once(lambda dt: os.startfile(INPUT_FILE), 1.0)



class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usernames = []
        self.open_usernames = []

    def _add_row_to_container(self, container_id, text, color=(1, 1, 1, 1)):
        container = self.ids.get(container_id)
        if container is None:
            return
        lbl = Label(text=text, color=color, size_hint_y=None, height=dp(28), halign="left", valign="middle")
        lbl.text_size = (container.width - dp(8) if container.width else Window.width - 200, None)
        container.add_widget(lbl)
        container.height = container.minimum_height

    def log(self, msg, color=(1, 1, 1, 1)):
        self._add_row_to_container("log_container", msg, color)

    def add_available(self, uname):
        self._add_row_to_container("available_container", uname, (0, 1, 0, 1))

    def start_checking(self):
        self.ids.start_btn.disabled = True
        if not os.path.isfile(INPUT_FILE):
            self.log(f"File not found: {INPUT_FILE}", (1, 0.3, 0.3, 1))
            self.ids.start_btn.disabled = False
            return
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            self.usernames = [line.strip() for line in f if line.strip()]
        self.open_usernames = []
        self.ids.progress.value = 0
        self.ids.log_container.clear_widgets()
        self.ids.available_container.clear_widgets()
        self.log("Starting Check...", (1, 1, 1, 1))
        threading.Thread(target=self.run_checking, daemon=True).start()

    def run_checking(self):
        total = len(self.usernames)
        for idx, uname in enumerate(self.usernames, start=1):
            retries = 0
            is_open = False
            while retries < MAX_RETRIES:
                try:
                    is_open = check_username(uname)
                    break
                except Exception as e:
                    retries += 1
                    Clock.schedule_once(lambda dt, m=f"Mistake while asking for {uname}: {e}": self.log(m, (0.8, 0.8, 0.8, 1)))
                    time.sleep(2)
            if is_open:
                self.open_usernames.append(uname)
                Clock.schedule_once(lambda dt, u=uname: self.add_available(u))
                Clock.schedule_once(lambda dt, m=f"{uname} ist not used ": self.log(m, (0, 1, 0, 1)))
            else:
                Clock.schedule_once(lambda dt, m=f"{uname} ist used ": self.log(m, (1, 0, 0, 1)))
            progress_val = (idx / total) * 100 if total > 0 else 100
            Clock.schedule_once(lambda dt, v=progress_val: self._set_progress(v))
            time.sleep(SLEEP_BETWEEN)
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for uname in self.open_usernames:
                    f.write(uname + "\n")
            os.startfile(OUTPUT_FILE)
        except Exception as e:
            Clock.schedule_once(lambda dt, m=f"Mistake while saving {e}": self.log(m, (1, 0.5, 0.2, 1)))
        Clock.schedule_once(lambda dt: self.log(f"Done, available: {len(self.open_usernames)} from {total} (saved in: {OUTPUT_FILE})", (1, 1, 1, 1)))
        Clock.schedule_once(lambda dt: self._enable_button())

    def _set_progress(self, val):
        try:
            self.ids.progress.value = float(val)
        except Exception:
            self.ids.progress.value = 0

    def _enable_button(self):
        self.ids.start_btn.disabled = False
        self.ids.start_btn.text = "Check again"


class TGUserNameChecker(App):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    TGUserNameChecker().run()
