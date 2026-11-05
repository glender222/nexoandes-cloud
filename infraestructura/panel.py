#!/usr/bin/env python3
"""Ventana local; las operaciones se ejecutan con el mismo controlador de consola."""
import json
from pathlib import Path
import subprocess
import threading
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, GLib
except (ImportError, ValueError):
    print("El panel necesita Python con GTK 3 (python3-gi y gir1.2-gtk-3.0). Usa ./nexoandes --help mientras tanto.", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]


class Panel(Gtk.Window):
    def __init__(self):
        super().__init__(title="NexoAndes · Control de nubes")
        self.set_default_size(950, 640)
        self.set_border_width(16)
        self.busy = False
        self.connect("delete-event", self.close)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(box)
        title = Gtk.Label()
        title.set_markup("<big><b>NexoAndes · Laboratorio multicloud</b></big>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)
        config = json.loads((ROOT / "infraestructura/privado/config.json").read_text())
        enabled = [name.upper() for name, value in config.items() if value.get("habilitada")]
        label = Gtk.Label(label="Nubes habilitadas: " + ", ".join(enabled) + ".")
        label.set_xalign(0)
        box.pack_start(label, False, False, 0)
        note = Gtk.Label(label="Encender crea o reactiva servicios. Apagar conserva datos y respaldos; el almacenamiento puede seguir cobrando.")
        note.set_line_wrap(True)
        note.set_xalign(0)
        box.pack_start(note, False, False, 0)
        actions = Gtk.Box(spacing=8)
        box.pack_start(actions, False, False, 0)
        self.buttons = []
        for text, args in [
            ("Comprobar accesos", ["comprobar"]),
            ("Ver plan", ["plan", "encender"]),
            ("Encender", ["encender"]),
            ("Apagar", ["apagar"]),
            ("Ver estado guardado", ["estado"]),
        ]:
            button = Gtk.Button(label=text)
            button.connect("clicked", self.start, args)
            actions.pack_start(button, True, True, 0)
            self.buttons.append(button)
        self.status = Gtk.Label(label="Preparado. Las credenciales de cada nube deben estar vigentes.")
        self.status.set_xalign(0)
        box.pack_start(self.status, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        self.log = Gtk.TextView(editable=False, monospace=True)
        self.log.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.buffer = self.log.get_buffer()
        scroll.add(self.log)
        box.pack_start(scroll, True, True, 0)

    def append(self, text):
        self.buffer.insert(self.buffer.get_end_iter(), text)
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.log.scroll_mark_onscreen(mark)
        self.buffer.delete_mark(mark)
        return False

    def start(self, _button, args):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.set_sensitive(False)
        self.status.set_text("En curso: " + " ".join(args) + ". Conserva esta ventana abierta.")
        self.append("\n$ ./nexoandes " + " ".join(args) + "\n")
        threading.Thread(target=self.worker, args=(args,), daemon=True).start()

    def worker(self, args):
        try:
            with subprocess.Popen([str(ROOT / "nexoandes"), *args], cwd=ROOT, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, bufsize=1) as process:
                for line in process.stdout:
                    GLib.idle_add(self.append, line)
                code = process.wait()
        except OSError as error:
            GLib.idle_add(self.append, str(error) + "\n")
            code = 1
        GLib.idle_add(self.finished, code)

    def finished(self, code):
        self.busy = False
        for button in self.buttons:
            button.set_sensitive(True)
        self.status.set_text("Operación completada." if code == 0 else "La operación falló. Revisa el registro antes de reintentar.")
        return False

    def close(self, *_args):
        if self.busy:
            self.status.set_text("Espera a que termine Terraform; cerrar ahora podría interrumpir la operación.")
            return True
        Gtk.main_quit()
        return False


if __name__ == "__main__":
    window = Panel()
    window.show_all()
    Gtk.main()
