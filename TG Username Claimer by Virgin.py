# This Tool is copy right claimed, via License. Any Stealing or Reselling, will have Law Consequences.

# Buy my OSINT Tool under https://2sint.shop btw :)

# Much Fun.

import requests
import time
import os
import threading
import random
import pyautogui  # type: ignore
import webbrowser
import pyperclip  # type: ignore
import pytesseract
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

from kivy.clock import Clock  # type: ignore
from kivy.lang import Builder  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.core.window import Window  # type: ignore
from kivy.config import Config  # type: ignore
from kivy.animation import Animation  # type: ignore
from kivy.uix.label import Label  # type: ignorea
from kivy.uix.screenmanager import Screen, ScreenManager  # type: ignore
from kivy.app import App  # type: ignore

Config.set("input", "mouse", "mouse,multitouch_on_demand")

INPUT_FILE = r"usernames.txt"
SLEEP_BETWEEN = 1.0
MAX_RETRIES = 3

Window.clearcolor = (0, 0, 0, 1)

if not os.path.isfile(INPUT_FILE):
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")


def is_color_close(r, g, b, target, tol=10):
    return all(abs(c - t) <= tol for c, t in zip((r, g, b), target))


def check_username_result() -> bool:
    time.sleep(3)
    screenshot = pyautogui.screenshot(region=(300, 650, 600, 100))
    text = pytesseract.image_to_string(screenshot).lower()
    if "taken" in text or "invalid" in text or "used" in text:
        return False
    return True


def detect_claim_success(uname: str, log_callback=None, pixel_x=118, pixel_y=709) -> bool:
    try:
        time.sleep(2)
        region = (300, 650, 800, 150)
        img = pyautogui.screenshot(region=region)
        gray = img.convert("L")
        gray = ImageOps.autocontrast(gray, cutoff=2)
        gray = ImageEnhance.Contrast(gray).enhance(1.8)
        gray = gray.filter(ImageFilter.MedianFilter(size=3))
        bw = gray.point(lambda x: 0 if x < 150 else 255, "1")
        text = pytesseract.image_to_string(bw, config="--psm 6").lower().strip()

        if log_callback:
            log_callback(f"OCR-Result: '{text[:200]}'", (0.6, 0.6, 1, 1))

        success_keywords = [
            "saved", "success", "username set", "username updated", "erfolgreich",
            "gespeichert", "successfully", "updated", "done", "✓", "ist jetzt"
        ]
        failure_keywords = [
            "taken", "invalid", "used", "not available", "already taken", "could not",
            "can't", "couldn't", "error", "nicht", "fehler", "bereits verwendet", "unavailable"
        ]

        for k in success_keywords:
            if k in text:
                if log_callback:
                    log_callback(f"keyword found: '{k}'", (0, 1, 0, 1))
                return True
        for k in failure_keywords:
            if k in text:
                if log_callback:
                    log_callback(f"keyword not found '{k}'", (1, 0, 0, 1))
                return False

        def sample_avg(px, py, size=2):
            tot_r = tot_g = tot_b = count = 0
            for dx in range(-size, size + 1):
                for dy in range(-size, size + 1):
                    try:
                        r, g, b = pyautogui.pixel(px + dx, py + dy)
                        tot_r += r
                        tot_g += g
                        tot_b += b
                        count += 1
                    except Exception:
                        continue
            return (tot_r // count, tot_g // count, tot_b // count) if count else (0, 0, 0)

        try:
            r, g, b = sample_avg(pixel_x, pixel_y, size=2)
            if log_callback:
                log_callback(f"pixel @({pixel_x},{pixel_y}) -> R:{r} G:{g} B:{b}", (0.5, 0.5, 1, 1))
            if is_color_close(r, g, b, (255, 211, 225), tol=10):
                if log_callback:
                    log_callback("rosa recognized", (0, 1, 0, 1))
                return True
            if (r, g, b) == (255, 255, 255):
                if log_callback:
                    log_callback("white recognized", (1, 0, 0, 1))
                return False
        except Exception as e:
            if log_callback:
                log_callback(f"reading the pixel failed: {e}", (1, 0.6, 0.2, 1))

        if log_callback:
            log_callback("fallback, checking via http.", (1, 1, 0.4, 1))
        try:
            time.sleep(1)
            available = check_username(uname)
            if not available:
                if log_callback:
                    log_callback("http check unavailable now, claiming was a success.", (0, 1, 0, 1))
                return True
            else:
                if log_callback:
                    log_callback("http check available, claiming was a fail.", (1, 0, 0, 1))
                return False
        except Exception as e:
            if log_callback:
                log_callback(f"HTTP-Check failed: {e}", (1, 0.4, 0.2, 1))
            return False

    except Exception as ex:
        if log_callback:
            log_callback(f"detect_claim_success erorr: {ex}", (1, 0.2, 0.2, 1))
        return False


def auto_claim_in_web(uname: str, log_callback=None) -> bool:
    try:
        webbrowser.open("https://web.telegram.org/")
        time.sleep(3)

        positions = [(30, 147), (88, 205), (404, 148), (200, 682)]
        for x, y in positions:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            time.sleep(1)

        pyperclip.copy(uname)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.press("delete")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)

        
        pixel_x, pixel_y = 118, 709

        
        pyautogui.moveTo(pixel_x, pixel_y, duration=0.2)

        try:
            r, g, b = pyautogui.pixel(pixel_x, pixel_y)
        except Exception:
            r = g = b = 0

        if log_callback:
            log_callback(
                f"Pixel @({pixel_x},{pixel_y}) -> R:{r} G:{g} B:{b}", 
                (0.5, 0.5, 1, 1)
            )

                
        if abs(r - 79) <= 5 and abs(g - 174) <= 5 and abs(b - 78) <= 5:
            if log_callback:
                log_callback(
                    f"green recognized {uname}, pressing enter",
                    (0, 1, 0, 1)
                )
            pyautogui.moveTo(435, 1000, duration=0.2)
            pyautogui.click()
            os._exit(0)


        
        elif r > 180 and g < 100 and b < 100:
            if log_callback:
                log_callback(f"red recognized {uname}, closing tab", (1, 0, 0, 1))
            pyautogui.hotkey("ctrl", "w")
            time.sleep(0.5)
            pyautogui.moveTo(1080, 800, duration=0.2)
            pyautogui.click()
            time.sleep(1)
            return False

        
        else:
            if log_callback:
                log_callback(f"undefinable color{r},{g},{b}) – tab closed and testing", (1, 1, 0, 1))
            pyautogui.hotkey("ctrl", "w")
            time.sleep(0.2)
            pyautogui.moveTo(1080, 800, duration=0.2)
            pyautogui.click()
            time.sleep(1)
            success = detect_claim_success(uname, log_callback, pixel_x, pixel_y)
            return success

    except Exception as e:
        if log_callback:
            log_callback(f"error in auto_claim_in_web: {e}", (1, 0, 0, 1))
        return False



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
                text: "Made by Virgin, @cpusocket on discord"
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
                text: "watermark by Virgin/2Sint"
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

                BoxLayout:
                    size_hint_y: None
                    height: dp(64)
                    padding: 0
                    Widget:
                    Button:
                        id: continue_btn
                        text: "Continue"
                        size_hint: None, None
                        width: dp(220)
                        height: dp(42)
                        background_normal: ""
                        background_color: 0,0.5,0,1
                        color: 1,1,1,1
                        on_release: root.continue_checking()
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
        self.current_index = 0  
        self._running_thread = None

    def continue_checking(self):
        self.log("continue pressed.", (0, 1, 1, 1))
        
        Clock.schedule_once(lambda dt: self._set_start_btn_running(), 0)
        threading.Thread(target=self.run_checking, args=(self.current_index + 1,), daemon=True).start()

    def _set_start_btn_running(self):
        try:
            self.ids.start_btn.disabled = True
            self.ids.start_btn.text = "Checking..."
        except Exception:
            pass

    def _add_row_to_container(self, container_id, text, color=(1, 1, 1, 1)):
        def _do_add(dt):
            container = self.ids.get(container_id)
            if container is None:
                return
            lbl = Label(text=text, color=color, size_hint_y=None, height=dp(28),
                        halign="left", valign="middle")
            lbl.text_size = (container.width - dp(8) if container.width else Window.width - 200, None)
            container.add_widget(lbl)
            container.height = container.minimum_height
        Clock.schedule_once(_do_add)

    def log(self, msg, color=(1, 1, 1, 1)):
        Clock.schedule_once(lambda dt: self._add_row_to_container("log_container", msg, color))

    def add_available(self, uname):
        Clock.schedule_once(lambda dt: self._add_row_to_container("available_container", uname, (0, 1, 0, 1)))

    def start_checking(self):
        self.ids.start_btn.disabled = True
        self.ids.start_btn.text = "Checking..."
        if not os.path.isfile(INPUT_FILE):
            self.log(f"File not found: {INPUT_FILE}", (1, 0.3, 0.3, 1))
            self.ids.start_btn.disabled = False
            self.ids.start_btn.text = "Start Checking"
            return
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            self.usernames = [line.strip() for line in f if line.strip()]
        self.open_usernames = []
        self.ids.progress.value = 0
        self.ids.log_container.clear_widgets()
        self.ids.available_container.clear_widgets()
        self.log("Starting Check...", (1, 1, 1, 1))

        threading.Thread(target=self.run_checking, args=(0,), daemon=True).start()

    def run_checking(self, start_index=0):
        total = len(self.usernames)
        for idx in range(start_index, total):
            uname = self.usernames[idx]
            self.current_index = idx  
            retries = 0
            is_open = False
            while retries < MAX_RETRIES:
                try:
                    is_open = check_username(uname)
                    break
                except Exception as e:
                    retries += 1
                    self.log(f"Mistake while asking for {uname}: {e}", (0.8, 0.8, 0.8, 1))
                    time.sleep(1)

            if is_open:
                self.open_usernames.append(uname)
                self.add_available(uname)
                self.log(f"{uname} is not used", (0, 1, 0, 1))

                

                self.log(f"starting automatic claiming {uname}...", (1, 1, 0.6, 1))
                
                threading.Thread(target=auto_claim_in_web, args=(uname, self.log), daemon=True).start()
                return  
            else:
                self.log(f"{uname} is used", (1, 0, 0, 1))

            progress_val = (idx / total) * 100 if total > 0 else 100
            Clock.schedule_once(lambda dt, v=progress_val: self._set_progress(v))
            time.sleep(SLEEP_BETWEEN)

        

        Clock.schedule_once(lambda dt: self._enable_start_btn())

    def _set_progress(self, val):
        self.ids.progress.value = val

    def _enable_start_btn(self):
        self.ids.start_btn.disabled = False
        self.ids.start_btn.text = "start claiming"


class MainApp(App):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    MainApp().run()
