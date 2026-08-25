"""
DigiVaani Phone Doctor
A lightweight, no-root Android device health & cleanup companion.
Built by 64yadav | DigiVaani64
"""

import os
import shutil
import platform
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.utils import platform as kivy_platform

# ----------------------------------------------------------------------
# Brand colors (DigiVaani64 palette)
# ----------------------------------------------------------------------
NAVY = (0x0A / 255, 0x0E / 255, 0x2A / 255, 1)
PANEL = (0x1F / 255, 0x2A / 255, 0x44 / 255, 1)
VIOLET = (0x6C / 255, 0x3F / 255, 0xC5 / 255, 1)
SAFFRON = (0xFF / 255, 0x8C / 255, 0x28 / 255, 1)
WHITE = (1, 1, 1, 1)
GREY = (0.75, 0.78, 0.85, 1)
GREEN = (0.30, 0.85, 0.45, 1)
RED = (0.95, 0.35, 0.35, 1)

APP_VERSION = "1.0"

# Try to import optional libs used only on real Android devices/builds.
try:
    from plyer import battery
    HAS_PLYER_BATTERY = True
except Exception:
    HAS_PLYER_BATTERY = False

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False


# ----------------------------------------------------------------------
# Reusable UI helpers
# ----------------------------------------------------------------------
class BgBoxLayout(BoxLayout):
    """BoxLayout with a solid background color."""

    def __init__(self, bg=NAVY, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def section_title(text):
    return Label(
        text=text,
        bold=True,
        font_size="18sp",
        color=WHITE,
        size_hint_y=None,
        height=dp(36),
        halign="left",
        valign="middle",
    )


def info_row(label_text, value_text, value_color=WHITE):
    row = BoxLayout(size_hint_y=None, height=dp(30))
    lbl = Label(text=label_text, color=GREY, font_size="14sp", halign="left")
    lbl.bind(size=lbl.setter("text_size"))
    val = Label(text=value_text, color=value_color, font_size="14sp", bold=True, halign="right")
    val.bind(size=val.setter("text_size"))
    row.add_widget(lbl)
    row.add_widget(val)
    return row


class Card(BgBoxLayout):
    """A rounded-feel panel card used to group content."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(14))
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("size_hint_y", None)
        super().__init__(bg=PANEL, **kwargs)
        self.bind(minimum_height=self.setter("height"))


# ----------------------------------------------------------------------
# Data helpers (no-root, safe, Android + desktop friendly)
# ----------------------------------------------------------------------
def get_storage_info():
    """Returns (total_gb, used_gb, free_gb, percent_used) for primary storage."""
    try:
        path = "/storage/emulated/0" if os.path.isdir("/storage/emulated/0") else os.path.expanduser("~")
        total, used, free = shutil.disk_usage(path)
        total_gb = total / (1024 ** 3)
        used_gb = used / (1024 ** 3)
        free_gb = free / (1024 ** 3)
        percent = (used / total) * 100 if total else 0
        return total_gb, used_gb, free_gb, percent
    except Exception:
        return 0, 0, 0, 0


def get_battery_info():
    """Returns (percent, is_charging) using plyer if available."""
    if HAS_PLYER_BATTERY:
        try:
            status = battery.status
            pct = status.get("percentage")
            charging = status.get("isCharging")
            if pct is not None:
                return pct, bool(charging)
        except Exception:
            pass
    return None, None


def get_ram_info():
    """Returns (total_gb, used_gb, percent) if psutil is available, else None."""
    if HAS_PSUTIL:
        try:
            vm = psutil.virtual_memory()
            total_gb = vm.total / (1024 ** 3)
            used_gb = (vm.total - vm.available) / (1024 ** 3)
            return total_gb, used_gb, vm.percent
        except Exception:
            pass
    return None


def get_cpu_percent():
    if HAS_PSUTIL:
        try:
            return psutil.cpu_percent(interval=0.2)
        except Exception:
            pass
    return None


def find_large_files(root_dir, min_mb=50, limit=15):
    """Scan an accessible folder for large files (no-root safe)."""
    results = []
    try:
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(fpath)
                    if size >= min_mb * 1024 * 1024:
                        results.append((fpath, size))
                except OSError:
                    continue
            if len(results) >= 300:  # safety cap while scanning
                break
    except Exception:
        pass
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


def format_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


# ----------------------------------------------------------------------
# Main screen
# ----------------------------------------------------------------------
class RootLayout(BgBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", bg=NAVY, **kwargs)

        # ---- Header ----
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=(dp(16), dp(10)),
        )
        title = Label(
            text="[b]DigiVaani Phone Doctor[/b]",
            markup=True,
            font_size="22sp",
            color=VIOLET,
            size_hint_y=None,
            height=dp(34),
        )
        subtitle = Label(
            text=f"By 64yadav  |  v{APP_VERSION}  |  No-root device companion",
            font_size="12sp",
            color=GREY,
            size_hint_y=None,
            height=dp(20),
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        self.add_widget(header)

        # ---- Scrollable content ----
        scroll = ScrollView(size_hint=(1, 1))
        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=(dp(14), dp(10), dp(14), dp(20)),
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        self.add_widget(scroll)

        # ---- Cards ----
        self.storage_card = self._build_storage_card()
        self.battery_card = self._build_battery_card()
        self.ram_cpu_card = self._build_ram_cpu_card()
        self.scan_card = self._build_scan_card()

        self.content.add_widget(self.storage_card)
        self.content.add_widget(self.battery_card)
        self.content.add_widget(self.ram_cpu_card)
        self.content.add_widget(self.scan_card)

        # ---- Footer ----
        footer = Label(
            text="Website: 64yadav.github.io/DigiVaani   |   Telegram: t.me/DigiVaani",
            font_size="11sp",
            color=GREY,
            size_hint_y=None,
            height=dp(30),
        )
        self.add_widget(footer)

        # Auto-refresh every 3 seconds
        Clock.schedule_interval(lambda dt: self.refresh_all(), 3)
        self.refresh_all()

    # ------------------------------------------------------------
    def _build_storage_card(self):
        card = Card()
        card.add_widget(section_title("💾 Storage"))
        self.storage_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(14))
        card.add_widget(self.storage_bar)
        self.storage_used_row = info_row("Used", "-- GB")
        self.storage_free_row = info_row("Free", "-- GB")
        self.storage_total_row = info_row("Total", "-- GB")
        card.add_widget(self.storage_used_row)
        card.add_widget(self.storage_free_row)
        card.add_widget(self.storage_total_row)
        return card

    def _build_battery_card(self):
        card = Card()
        card.add_widget(section_title("🔋 Battery"))
        self.battery_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(14))
        card.add_widget(self.battery_bar)
        self.battery_row = info_row("Status", "Checking...")
        card.add_widget(self.battery_row)
        return card

    def _build_ram_cpu_card(self):
        card = Card()
        card.add_widget(section_title("⚙️ RAM & CPU"))
        self.ram_row = info_row("RAM Used", "--")
        self.cpu_row = info_row("CPU Load", "--")
        card.add_widget(self.ram_row)
        card.add_widget(self.cpu_row)
        return card

    def _build_scan_card(self):
        card = Card()
        card.add_widget(section_title("🧹 Large File Scan"))
        desc = Label(
            text="Scans accessible storage for files 50MB or bigger — helps you find what's eating space.",
            font_size="12sp",
            color=GREY,
            size_hint_y=None,
            height=dp(34),
        )
        desc.bind(size=desc.setter("text_size"))
        card.add_widget(desc)

        scan_btn = Button(
            text="Scan for Large Files",
            size_hint_y=None,
            height=dp(42),
            background_color=VIOLET,
            color=WHITE,
            bold=True,
        )
        scan_btn.bind(on_release=lambda *a: self.run_scan())
        card.add_widget(scan_btn)

        self.scan_results_label = Label(
            text="Tap the button above to scan.",
            font_size="12sp",
            color=GREY,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.scan_results_label.bind(
            width=lambda *a: self.scan_results_label.setter("text_size")(
                self.scan_results_label, (self.scan_results_label.width, None)
            )
        )
        self.scan_results_label.bind(texture_size=self._sync_scan_label_height)
        card.add_widget(self.scan_results_label)
        return card

    def _sync_scan_label_height(self, instance, value):
        instance.height = value[1]

    # ------------------------------------------------------------
    def refresh_all(self):
        self.refresh_storage()
        self.refresh_battery()
        self.refresh_ram_cpu()

    def refresh_storage(self):
        total, used, free, percent = get_storage_info()
        self.storage_bar.value = percent
        self._set_row_value(self.storage_used_row, f"{used:.1f} GB")
        self._set_row_value(self.storage_free_row, f"{free:.1f} GB")
        self._set_row_value(self.storage_total_row, f"{total:.1f} GB")

    def refresh_battery(self):
        pct, charging = get_battery_info()
        if pct is None:
            self.battery_row.children[0].text = "Not available on this build"
            return
        self.battery_bar.value = pct
        status_text = f"{pct}%" + (" (Charging)" if charging else "")
        color = GREEN if pct > 30 else RED
        self._set_row_value(self.battery_row, status_text, color)

    def refresh_ram_cpu(self):
        ram = get_ram_info()
        if ram:
            total_gb, used_gb, percent = ram
            self._set_row_value(self.ram_row, f"{used_gb:.1f}/{total_gb:.1f} GB ({percent:.0f}%)")
        else:
            self._set_row_value(self.ram_row, "Not available")

        cpu = get_cpu_percent()
        if cpu is not None:
            self._set_row_value(self.cpu_row, f"{cpu:.0f}%")
        else:
            self._set_row_value(self.cpu_row, "Not available")

    def _set_row_value(self, row, text, color=WHITE):
        value_label = row.children[0]  # last added child is index 0 (BoxLayout reverses order)
        value_label.text = text
        value_label.color = color

    # ------------------------------------------------------------
    def run_scan(self):
        self.scan_results_label.text = "Scanning... please wait"
        Clock.schedule_once(lambda dt: self._do_scan(), 0.1)

    def _do_scan(self):
        base = "/storage/emulated/0" if os.path.isdir("/storage/emulated/0") else os.path.expanduser("~")
        results = find_large_files(base, min_mb=50, limit=15)
        if not results:
            self.scan_results_label.text = "No files over 50MB found (or folder not accessible)."
            return

        lines = [f"Found {len(results)} large file(s):\n"]
        for path, size in results:
            short_name = os.path.basename(path)
            lines.append(f"  {format_size(size):>8}   {short_name}")
        self.scan_results_label.text = "\n".join(lines)


class DigiVaaniPhoneDoctorApp(App):
    title = "DigiVaani Phone Doctor"

    def build(self):
        Window.clearcolor = NAVY
        return RootLayout()


if __name__ == "__main__":
    DigiVaaniPhoneDoctorApp().run()
