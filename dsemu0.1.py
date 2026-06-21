#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AC's DS Emulator 0.1 - no$gba Style
Light / Dark / Blue Mode
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class ACDSAssembler:
    def assemble(self, source: str) -> bytes:
        program = bytearray()
        for line in source.splitlines():
            line = line.strip().split(';')[0].strip()
            if not line: continue
            parts = line.replace(',', ' ').split()
            mnem = parts[0].upper()
            if mnem == "NOP": program += bytes([0x00, 0, 0, 0])
            elif mnem == "MOV": program += bytes([0x01, int(parts[1][1:])&0xF, 0, int(parts[2])&0xFF])
            elif mnem == "ADD": program += bytes([0x02, int(parts[1][1:])&0xF, 0, int(parts[2])&0xFF])
            elif mnem == "RECT": program += bytes([0x07, int(parts[1][1:])&0xF, int(parts[2][1:])&0xF, int(parts[3])&0xFF])
            elif mnem == "HALT": program += bytes([0xFF, 0, 0, 0])
        return bytes(program)


class ACDSVM:
    def __init__(self):
        self.x = 90
        self.y = 70
        self.halted = False
        self.program = b""
        self.pc = 0

    def load(self, bytecode: bytes):
        self.program = bytecode
        self.pc = 0
        self.halted = False

    def step(self):
        if self.halted or not self.program or self.pc >= len(self.program):
            self.halted = True
            return
        opcode = self.program[self.pc]
        self.pc += 4

        if opcode == 0x01: self.x = self.program[self.pc-1] * 2
        elif opcode == 0x02: self.x = (self.x + self.program[self.pc-1]) % 220
        elif opcode == 0x07:
            self.x = self.program[self.pc-3] * 12
            self.y = self.program[self.pc-2] * 12
        elif opcode == 0xFF: self.halted = True

    def draw(self, canvas, scale=2):
        canvas.delete("all")
        s = scale
        canvas.create_rectangle(0, 0, 256*s, 192*s, fill="#000000")   # Top Screen
        canvas.create_rectangle(0, 192*s, 256*s, 384*s, fill="#111111") # Bottom Screen

        canvas.create_rectangle(self.x*s, self.y*s, (self.x+40)*s, (self.y+35)*s, fill="#00ffaa", outline="#ffffff", width=3)


class ACDSemu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AC's DS Emulator 0.1")
        self.root.geometry("620x460")
        self.root.minsize(620, 460)

        self.vm = ACDSVM()
        self.assembler = ACDSAssembler()
        self.running = False
        self.theme = "dark"

        self._build_ui()
        self._frame_loop()

    def _build_ui(self):
        # Toolbar
        tb = tk.Frame(self.root, bg="#2d2d2d", height=50)
        tb.pack(fill="x", padx=6, pady=6)

        ttk.Button(tb, text="▶ Run", command=self.toggle_run).pack(side="left", padx=4)
        ttk.Button(tb, text="⏹ Stop", command=self.stop).pack(side="left", padx=4)
        ttk.Button(tb, text="Step", command=self.step).pack(side="left", padx=4)
        ttk.Button(tb, text="Load .nds", command=self.load).pack(side="left", padx=4)
        ttk.Button(tb, text="Assemble", command=self.assemble).pack(side="left", padx=4)

        # Theme buttons
        ttk.Button(tb, text="🌙 Dark", command=self.dark_mode).pack(side="right", padx=2)
        ttk.Button(tb, text="☀️ Light", command=self.light_mode).pack(side="right", padx=2)
        ttk.Button(tb, text="🔵 Blue", command=self.blue_mode).pack(side="right", padx=2)

        # Screen
        self.screen_frame = tk.Frame(self.root, bg="#000000", relief="sunken", bd=6)
        self.screen_frame.pack(pady=12, padx=12)

        self.canvas = tk.Canvas(self.screen_frame, width=256*2, height=192*2, bg="#000000")
        self.canvas.pack()

        self.status = tk.Label(self.root, text="AC's DS Emulator 0.1 - no$gba Style", bg="#2d2d2d", fg="#e0e0e0", anchor="w", padx=10)
        self.status.pack(fill="x", side="bottom")

        self.editor = scrolledtext.ScrolledText(self.root, height=8, bg="#1a1a2e", fg="#e0e0e0")
        self.editor.pack(fill="x", padx=8, pady=6)
        self.editor.insert("1.0", """; DS Example
MOV R0, 90
MOV R1, 70
RECT R0, R1, 30
HALT
""")

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("NDS", "*.nds *.txt")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", code)
            self.assemble()

    def assemble(self):
        code = self.editor.get("1.0", "end").strip()
        try:
            bytecode = self.assembler.assemble(code)
            self.vm.load(bytecode)
            self.status.config(text=f"Loaded {len(bytecode)} bytes")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_run(self):
        self.running = not self.running
        self.status.config(text="RUNNING..." if self.running else "PAUSED")

    def stop(self):
        self.running = False
        self.status.config(text="Stopped")

    def step(self):
        self.vm.step()
        self.render()

    def render(self):
        self.vm.draw(self.canvas, scale=2)

    def _frame_loop(self):
        if self.running:
            for _ in range(8):
                self.vm.step()
            self.render()
        self.root.after(16, self._frame_loop)

    def dark_mode(self):
        self.root.configure(bg="#1e1e1e")
        self.status.config(bg="#2d2d2d", fg="#e0e0e0")

    def light_mode(self):
        self.root.configure(bg="#f0f0f0")
        self.status.config(bg="#e0e0e0", fg="#000000")

    def blue_mode(self):
        self.root.configure(bg="#001f3f")
        self.status.config(bg="#003366", fg="#a0d8ff")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ACDSemu().run()
