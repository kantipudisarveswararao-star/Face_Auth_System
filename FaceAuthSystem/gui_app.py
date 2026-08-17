import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import cv2
from PIL import Image, ImageTk
import os
import getpass

BG        = "#0A0E14"
CARD      = "#141925"
CARD2     = "#0F141D"
ACCENT    = "#3DDC97"
SUCCESS   = "#3DDC97"
DANGER    = "#FF5470"
WARNING   = "#F5B942"
TEXT      = "#F2F4F8"
SUBTEXT   = "#6B7589"
BORDER    = "#232938"

FONT_TITLE  = ("Segoe UI", 27, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)
FONT_LABEL  = ("Segoe UI", 10, "bold")
FONT_EYEBROW = ("Segoe UI", 9, "bold")   


def styled_entry(parent, show=None, width=28):
    e = tk.Entry(parent, show=show, width=width,
                 bg=CARD2, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_BODY,
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BORDER)
    return e

def styled_btn(parent, text, command, color=ACCENT, fg=BG, width=20, pady=8):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, activebackground=color,
                    activeforeground=fg, font=("Segoe UI", 11, "bold"),
                    relief="flat", cursor="hand2", width=width, pady=pady,
                    bd=0, highlightthickness=0)
    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def ghost_btn(parent, text, command, width=20, pady=8):
    """Secondary/outline-style button: transparent fill, accent border feel
    via a thin frame wrapper, used for less prominent actions."""
    wrap = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    btn = tk.Button(wrap, text=text, command=command,
                    bg=CARD, fg=TEXT, activebackground=CARD2,
                    activeforeground=ACCENT, font=("Segoe UI", 11, "bold"),
                    relief="flat", cursor="hand2", width=width, pady=pady,
                    bd=0, highlightthickness=0)
    btn.pack()
    btn.bind("<Enter>", lambda e: btn.config(fg=ACCENT))
    btn.bind("<Leave>", lambda e: btn.config(fg=TEXT))
    return wrap

def _lighten(hex_color):
    r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    r,g,b = min(255,r+26), min(255,g+26), min(255,b+26)
    return f"#{r:02x}{g:02x}{b:02x}"

def label(parent, text, font=FONT_BODY, color=TEXT, **kwargs):
    return tk.Label(parent, text=text, font=font, fg=color, bg=kwargs.pop("bg", BG), **kwargs)

def eyebrow(parent, text, color=ACCENT, bg=BG):
    """Small tracked uppercase marker used above section headings."""
    spaced = "  ".join(list(text.upper()))
    return tk.Label(parent, text=spaced, font=FONT_EYEBROW, fg=color, bg=bg)

def hline(parent, color=BORDER):
    return tk.Frame(parent, height=1, bg=color)

def status_badge(parent, text, color=ACCENT):
    f = tk.Frame(parent, bg=color, padx=10, pady=3)
    tk.Label(f, text=text.upper(), font=FONT_EYEBROW, fg=BG, bg=color).pack()
    return f

def corner_brackets(canvas, x0, y0, x1, y1, color=ACCENT, length=14, width=2):
    """Draws four corner brackets inside the given bounds — the recurring
    signature motif used in place of icon glyphs throughout the app."""
    canvas.create_line(x0, y0+length, x0, y0, x0+length, y0, fill=color, width=width)
    canvas.create_line(x1-length, y0, x1, y0, x1, y0+length, fill=color, width=width)
    canvas.create_line(x0, y1-length, x0, y1, x0+length, y1, fill=color, width=width)
    canvas.create_line(x1-length, y1, x1, y1, x1, y1-length, fill=color, width=width)


# ── Main Application 
class FaceAuthApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Face Auth System")
        self.geometry("960x640")
        self.minsize(860, 580)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 960) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"960x640+{x}+{y}")

        self._current_frame = None
        self._show_index()

    # ── Navigation 
    def _switch(self, FrameClass, *args, **kwargs):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = FrameClass(self, *args, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

    def _show_index(self):       self._switch(IndexScreen)
    def _show_home(self):        self._switch(HomeScreen)
    def _show_register(self):   self._switch(RegisterScreen)
    def _show_login(self):      self._switch(LoginScreen)
    def _show_dashboard(self, user): self._switch(DashboardScreen, user)
    def _show_user_login(self): self._switch(UserLoginScreen)
    def _show_welcome(self, user): self._switch(WelcomeScreen, user)


class ScanLine:
    """Draws an animated horizontal scan line on a canvas."""
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.w = width
        self.h = height
        self.y = 0
        self.line = canvas.create_line(0, 0, width, 0, fill=ACCENT, width=2)
        self._animate()

    def _animate(self):
        self.y = (self.y + 3) % self.h
        self.canvas.coords(self.line, 0, self.y, self.w, self.y)
        self.canvas.after(30, self._animate)


# ── Index / Landing Screen 
class IndexScreen(tk.Frame):
    """First screen shown on launch. Gives an overview of the system and
    routes the visitor to either the Admin area (existing HomeScreen) or
    the restricted User Login screen."""
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        # ── Header bar ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=CARD, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Frame(header, bg=ACCENT, height=2).place(x=0, y=0, relwidth=1)

        mark_canvas = tk.Canvas(header, width=34, height=34, bg=CARD,
                                 highlightthickness=0)
        mark_canvas.pack(side="left", padx=(24,12), pady=15)
        corner_brackets(mark_canvas, 2, 2, 32, 32, color=ACCENT, length=10, width=2)

        title_box = tk.Frame(header, bg=CARD)
        title_box.pack(side="left", pady=10)
        label(title_box, "FACE AUTH SYSTEM", font=("Segoe UI", 14, "bold"),
              color=TEXT, bg=CARD).pack(anchor="w")
        label(title_box, "AI-BASED FACIAL RECOGNITION AUTHENTICATION",
              font=("Segoe UI", 8, "bold"), color=SUBTEXT, bg=CARD).pack(anchor="w")

        status_badge(header, "Online", SUCCESS).pack(side="right", padx=24)

        # ── Scrollable body 
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(outer)
        scrollbar.pack(side="right", fill="y")
        canvas = tk.Canvas(outer, bg=BG, yscrollcommand=scrollbar.set,
                           highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)

        body = tk.Frame(canvas, bg=BG)
        canvas.create_window((0,0), window=body, anchor="nw", width=960)

        def on_config(e):
            canvas.config(scrollregion=canvas.bbox("all"))
        body.bind("<Configure>", on_config)

        def _on_mousewheel(e):
            try:
                canvas.yview_scroll(int(-e.delta/40), "units")
            except tk.TclError:
                pass

        def _bind_wheel(e):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(e):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        self.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        hero = tk.Frame(body, bg=BG)
        hero.pack(fill="x", padx=44, pady=(40, 8))
        eyebrow(hero, "Identity Verification", color=ACCENT, bg=BG).pack(anchor="w", pady=(0,10))
        label(hero, "Secure access,\nverified by your face.",
              font=("Segoe UI", 28, "bold"), color=TEXT, justify="left").pack(anchor="w")
        label(hero,
              "This system pairs password authentication with real-time facial\n"
              "recognition — a 128-dimensional encoding compared by distance — and\n"
              "logs every attempt for audit purposes.",
              font=FONT_BODY, color=SUBTEXT, justify="left").pack(anchor="w", pady=(14,0))

        hline(body, BORDER).pack(fill="x", padx=44, pady=28)

        # ── How it works 
        eyebrow(body, "Process", color=ACCENT, bg=BG).pack(anchor="w", padx=44, pady=(0,8))
        label(body, "How it works", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=44, pady=(0,14))

        steps = [
            ("01", "Admin registers users",
             "An administrator captures each user's face and sets their password."),
            ("02", "Live face capture",
             "The webcam feed detects a face and extracts a 128-dimensional encoding."),
            ("03", "Two-factor check",
             "Login requires both the correct password and a matching face encoding."),
            ("04", "Every attempt logged",
             "Granted and denied attempts are written to a tamper-evident access log."),
        ]
        steps_row = tk.Frame(body, bg=BG)
        steps_row.pack(fill="x", padx=44)
        for num, title, desc in steps:
            card = tk.Frame(steps_row, bg=CARD, padx=18, pady=18,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(card, text=num, font=("Segoe UI", 20, "bold"), bg=CARD,
                     fg=ACCENT).pack(anchor="w")
            tk.Label(card, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT,
                     anchor="w", justify="left", wraplength=170).pack(anchor="w", pady=(10,4))
            tk.Label(card, text=desc, font=FONT_SMALL, bg=CARD, fg=SUBTEXT,
                     anchor="w", justify="left", wraplength=170).pack(anchor="w")

        hline(body, BORDER).pack(fill="x", padx=44, pady=32)

        # ── Choose role ─────────────────────────────────────────────────
        eyebrow(body, "Get Started", color=ACCENT, bg=BG).pack(anchor="w", padx=44, pady=(0,8))
        label(body, "Continue as", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=44, pady=(0,14))

        roles_row = tk.Frame(body, bg=BG)
        roles_row.pack(fill="x", padx=44, pady=(0,44))

        admin_card = tk.Frame(roles_row, bg=CARD, padx=26, pady=24,
                              highlightthickness=1, highlightbackground=BORDER)
        admin_card.pack(side="left", fill="both", expand=True, padx=(0,10))
        eyebrow(admin_card, "Role", color=SUBTEXT, bg=CARD).pack(anchor="w")
        tk.Label(admin_card, text="Administrator", font=("Segoe UI", 16, "bold"), bg=CARD,
                 fg=TEXT).pack(anchor="w", pady=(10,4))
        tk.Label(admin_card, text="Register new users, log in via the admin\n"
                 "console, and manage the access log.",
                 font=FONT_SMALL, bg=CARD, fg=SUBTEXT, justify="left").pack(anchor="w", pady=(0,18))
        styled_btn(admin_card, "Continue as Admin", self.master._show_home,
                   color=ACCENT, fg=BG, width=20, pady=10).pack(anchor="w")

        user_card = tk.Frame(roles_row, bg=CARD, padx=26, pady=24,
                             highlightthickness=1, highlightbackground=BORDER)
        user_card.pack(side="left", fill="both", expand=True, padx=(10,0))
        eyebrow(user_card, "Role", color=SUBTEXT, bg=CARD).pack(anchor="w")
        tk.Label(user_card, text="User", font=("Segoe UI", 16, "bold"), bg=CARD,
                 fg=TEXT).pack(anchor="w", pady=(10,4))
        tk.Label(user_card, text="Already registered by an admin? Verify your\n"
                 "password and face to sign in.",
                 font=FONT_SMALL, bg=CARD, fg=SUBTEXT, justify="left").pack(anchor="w", pady=(0,18))
        ghost_btn(user_card, "User Login", self.master._show_user_login,
                  width=18, pady=9).pack(anchor="w")


# ── Home Screen ──
class HomeScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        # Left branding panel
        left = tk.Frame(self, bg=CARD, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Frame(left, bg=ACCENT, width=2).place(x=0, y=0, relheight=1)

        tk.Frame(left, bg=CARD).pack(expand=True)

        # Signature corner-bracket mark
        mark_canvas = tk.Canvas(left, width=80, height=80, bg=CARD,
                                 highlightthickness=0)
        mark_canvas.pack(pady=(0,18))
        corner_brackets(mark_canvas, 6, 6, 74, 74, color=ACCENT, length=18, width=2)
        mark_canvas.create_oval(28, 28, 52, 52, outline=ACCENT, width=1.5)

        label(left, "FACE AUTH", font=("Segoe UI", 22, "bold"),
              color=TEXT, bg=CARD).pack()
        eyebrow(left, "Admin Console", color=ACCENT, bg=CARD).pack(pady=(6, 26))

        hline(left, BORDER).pack(fill="x", padx=32, pady=4)

        features = [
            "Real-time Face Detection",
            "128-D Neural Encoding",
            "Dual-Factor Authentication",
            "Tamper-Proof Audit Log",
        ]
        for i, text in enumerate(features):
            row = tk.Frame(left, bg=CARD)
            row.pack(fill="x", padx=32, pady=7)
            tk.Label(row, text=f"{i+1:02d}", font=("Consolas", 10, "bold"),
                     bg=CARD, fg=ACCENT, width=3, anchor="w").pack(side="left")
            label(row, text, font=FONT_SMALL, color=SUBTEXT, bg=CARD).pack(
                side="left", padx=4)

        tk.Frame(left, bg=CARD).pack(expand=True)

        label(left, "v1.0   ·   OpenCV + face_recognition",
              font=FONT_SMALL, color=BORDER, bg=CARD).pack(pady=14)

        # Right action panel
        right = tk.Frame(self, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        center = tk.Frame(right, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        eyebrow(center, "Administrator", color=ACCENT, bg=BG).pack(pady=(0,10))
        label(center, "Welcome back", font=("Segoe UI", 30, "bold"),
              color=TEXT).pack(pady=(0, 6))
        label(center, "Choose an action to continue", font=FONT_BODY,
              color=SUBTEXT).pack(pady=(0, 36))

        card = tk.Frame(center, bg=CARD, padx=42, pady=38,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(ipadx=10)

        styled_btn(card, "Register New User",
                   self.master._show_register, color=ACCENT, fg=BG, pady=12,
                   width=24).pack(pady=(0, 14))

        ghost_btn(card, "Login with Face ID",
                  self.master._show_login, width=24, pady=11).pack(pady=(0, 4))

        hline(center, BORDER).pack(fill="x", pady=26)
        status_badge(center, "System Online", SUCCESS).pack()

        back_lbl = tk.Label(center, text="Back to start page", font=FONT_SMALL,
                             fg=SUBTEXT, bg=BG, cursor="hand2")
        back_lbl.pack(pady=(16,0))
        back_lbl.bind("<Enter>", lambda e: back_lbl.config(fg=ACCENT))
        back_lbl.bind("<Leave>", lambda e: back_lbl.config(fg=SUBTEXT))
        back_lbl.bind("<Button-1>", lambda e: self.master._show_index())

class CameraWidget(tk.Frame):
    """Live webcam feed with optional scan-line overlay."""
    def __init__(self, master, width=480, height=360, on_capture=None):
        super().__init__(master, bg=BG, width=width, height=height)
        self.pack_propagate(False)
        self.cam_w = width
        self.cam_h = height
        self.on_capture = on_capture
        self._cap = None
        self._running = False
        self._last_frame = None
        self._scan_y = 0
        self._build()

    def _build(self):
        self.canvas = tk.Canvas(self, width=self.cam_w, height=self.cam_h,
                                 bg="black", highlightthickness=2,
                                 highlightbackground=ACCENT)
        self.canvas.pack()

        # Overlay text
        self._overlay = self.canvas.create_text(
            self.cam_w // 2, self.cam_h - 20,
            text="", fill=ACCENT, font=FONT_MONO)

        # Scan line
        self._scan_line = self.canvas.create_line(
            0, 0, self.cam_w, 0, fill=ACCENT, width=2, state="hidden")

        # Status dot
        self._dot = self.canvas.create_oval(8,8,18,18, fill=DANGER, outline="")

    def start(self):
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self._show_error("Camera not accessible")
            return False
        self._running = True
        self.canvas.itemconfig(self._scan_line, state="normal")
        self.canvas.itemconfig(self._dot, fill=SUCCESS)
        threading.Thread(target=self._feed_loop, daemon=True).start()
        self._anim_scan()
        return True

    def stop(self):
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None

    def get_frame(self):
        return self._last_frame

    def set_overlay(self, text):
        self.canvas.itemconfig(self._overlay, text=text)

    def _feed_loop(self):
        from face_utils import detect_faces_haar
        while self._running:
            if self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret:
                    self._last_frame = frame.copy()
                    faces = detect_faces_haar(frame)
                    for (x,y,w,h) in faces:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(151,220,61),2)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    rgb = cv2.resize(rgb,(self.cam_w, self.cam_h))
                    img = ImageTk.PhotoImage(Image.fromarray(rgb))
                    try:
                        self.canvas.create_image(0,0,anchor="nw",image=img)
                        self.canvas.image = img
                        # keep scan line & overlay on top
                        self.canvas.tag_raise(self._scan_line)
                        self.canvas.tag_raise(self._overlay)
                        self.canvas.tag_raise(self._dot)
                    except tk.TclError:
                        break
            time.sleep(0.03)

    def _anim_scan(self):
        if not self._running:
            return
        self._scan_y = (self._scan_y + 4) % self.cam_h
        self.canvas.coords(self._scan_line, 0, self._scan_y,
                           self.cam_w, self._scan_y)
        self.after(30, self._anim_scan)

    def _show_error(self, msg):
        self.canvas.create_text(self.cam_w//2, self.cam_h//2,
                                 text=msg.upper(), fill=DANGER,
                                 font=FONT_HEAD)


# ── Register Screen ───
class RegisterScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._status_var = tk.StringVar(value="")
        self._build()

    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=CARD, height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ghost_btn(topbar, "Back", self._go_back, width=7, pady=4).pack(
                   side="left", padx=12, pady=8)
        eyebrow(topbar, "Admin", color=SUBTEXT, bg=CARD).pack(side="left", padx=(4,10))
        label(topbar, "Register New User", font=FONT_HEAD,
              color=TEXT, bg=CARD).pack(side="left")
        status_badge(topbar, "Live", SUCCESS).pack(side="right", padx=16, pady=10)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Left: camera
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        eyebrow(left, "Camera", color=ACCENT, bg=BG).pack(anchor="w", pady=(0,6))
        label(left, "Position your face within the frame",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", pady=(0,8))

        self.cam = CameraWidget(left, width=480, height=340)
        self.cam.pack()

        # Capture button below camera
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(pady=12)
        self._capture_btn = styled_btn(btn_row, "Capture Face",
                                        self._capture, color=ACCENT, fg=BG,
                                        width=20, pady=10)
        self._capture_btn.pack(side="left", padx=6)

        # Right: form
        right = tk.Frame(body, bg=CARD, padx=28, pady=24)
        right.pack(side="right", fill="y", padx=(16,0))
        right.config(highlightthickness=1, highlightbackground=BORDER)

        eyebrow(right, "Step 2", color=ACCENT, bg=CARD).pack(anchor="w")
        label(right, "Account Details", font=FONT_HEAD, color=TEXT, bg=CARD).pack(anchor="w", pady=(4,0))
        hline(right, BORDER).pack(fill="x", pady=12)

        def field(lbl, show=None):
            label(right, lbl, font=FONT_LABEL, color=SUBTEXT, bg=CARD).pack(anchor="w", pady=(8,2))
            e = styled_entry(right, show=show, width=26)
            e.pack(fill="x", ipady=6)
            return e

        self._name_entry     = field("Username")
        self._pass_entry     = field("Password", show="•")
        self._confirm_entry  = field("Confirm Password", show="•")

        hline(right, BORDER).pack(fill="x", pady=16)

        self._register_btn = styled_btn(right, "Complete Registration",
                                         self._register, color=SUCCESS, fg=BG,
                                         width=24, pady=11)
        self._register_btn.pack()

        # Status bar
        self._status_lbl = label(right, "", font=FONT_SMALL,
                                  color=SUBTEXT, bg=CARD)
        self._status_lbl.pack(pady=(12,0))

        # Captured preview label
        self._preview_lbl = tk.Label(right, bg=CARD)
        self._preview_lbl.pack(pady=4)

        # Face state
        self._face_encoding = None
        self._captured_frame = None

        # Start camera
        if not self.cam.start():
            self._set_status("Camera not available", DANGER)

        self.cam.set_overlay("CAPTURE FACE WHEN READY")

    def _go_back(self):
        self.cam.stop()
        self.master._show_home()

    def _set_status(self, msg, color=SUBTEXT):
        self._status_lbl.config(text=msg, fg=color)

    def _capture(self):
        frame = self.cam.get_frame()
        if frame is None:
            self._set_status("No frame from camera", DANGER)
            return
        self._set_status("Extracting face features...", WARNING)
        self.update()

        from face_utils import get_face_encoding
        encoding, info = get_face_encoding(frame)
        if encoding is None:
            self._set_status(info, DANGER)
            return

        self._face_encoding   = encoding
        self._captured_frame  = frame.copy()

        # Show small preview
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (120, 90))
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self._preview_lbl.config(image=img)
        self._preview_lbl.image = img

        self._set_status("Face captured — fill form & register", SUCCESS)
        self.cam.set_overlay("FACE CAPTURED")

    def _register(self):
        from database import username_exists, add_user
        from log_utils import log_result

        name    = self._name_entry.get().strip()
        pw      = self._pass_entry.get().strip()
        confirm = self._confirm_entry.get().strip()

        if not name:
            self._set_status("Username is required", DANGER); return
        if username_exists(name):
            self._set_status(f"Username '{name}' already exists", DANGER); return
        if pw != confirm:
            self._set_status("Passwords do not match", DANGER); return
        if len(pw) < 4:
            self._set_status("Password must be at least 4 characters", DANGER); return
        if self._face_encoding is None:
            self._set_status("Capture your face first", DANGER); return

        DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
        os.makedirs(DATASET_DIR, exist_ok=True)
        image_path = os.path.join(DATASET_DIR, f"{name}.jpg")
        cv2.imwrite(image_path, self._captured_frame)

        success = add_user(name, pw, self._face_encoding, image_path)
        if success:
            log_result(name, "GRANTED", reason="New user registered")
            self.cam.stop()
            self._show_success_popup(name)
        else:
            log_result(name, "DENIED", reason="Registration failed - duplicate")
            self._set_status("Registration failed", DANGER)

    def _show_success_popup(self, name):
        pop = tk.Toplevel(self, bg=CARD)
        pop.title("Registration Successful")
        pop.geometry("360x210")
        pop.resizable(False, False)
        pop.grab_set()
        pop.configure(highlightthickness=1, highlightbackground=BORDER)
        tk.Frame(pop, bg=ACCENT, height=3).pack(fill="x")
        status_badge(pop, "Registered", SUCCESS).pack(pady=(24,10))
        tk.Label(pop, text=f"Welcome, {name}",
                 font=FONT_HEAD, bg=CARD, fg=TEXT).pack()
        tk.Label(pop, text="Registration complete.",
                 font=FONT_SMALL, bg=CARD, fg=SUBTEXT).pack(pady=4)
        styled_btn(pop, "Go to Login", lambda: (pop.destroy(), self.master._show_login()),
                   color=SUCCESS, fg=BG, pady=8, width=16).pack(pady=12)


# ── Login Screen ──
class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=CARD, height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ghost_btn(topbar, "Back", self._go_back, width=7, pady=4).pack(
                   side="left", padx=12, pady=8)
        eyebrow(topbar, "Admin", color=SUBTEXT, bg=CARD).pack(side="left", padx=(4,10))
        label(topbar, "Face ID Login", font=FONT_HEAD,
              color=TEXT, bg=CARD).pack(side="left")
        status_badge(topbar, "Scanning", ACCENT).pack(side="right", padx=16, pady=10)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Left: camera
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        eyebrow(left, "Camera", color=ACCENT, bg=BG).pack(anchor="w", pady=(0,6))
        label(left, "Look directly at the camera",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", pady=(0,8))

        self.cam = CameraWidget(left, width=480, height=340)
        self.cam.pack()

        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(pady=12)
        self._verify_btn = styled_btn(btn_row, "Verify & Login",
                                       self._login, color=ACCENT, fg=BG,
                                       width=20, pady=10)
        self._verify_btn.pack(side="left", padx=6)

        # Right: credentials
        right = tk.Frame(body, bg=CARD, padx=28, pady=24)
        right.pack(side="right", fill="y", padx=(16,0))
        right.config(highlightthickness=1, highlightbackground=BORDER)

        eyebrow(right, "Step 2", color=ACCENT, bg=CARD).pack(anchor="w")
        label(right, "Credentials", font=FONT_HEAD, color=TEXT, bg=CARD).pack(anchor="w", pady=(4,0))
        hline(right, BORDER).pack(fill="x", pady=12)

        def field(lbl, show=None):
            label(right, lbl, font=FONT_LABEL, color=SUBTEXT, bg=CARD).pack(anchor="w", pady=(8,2))
            e = styled_entry(right, show=show, width=26)
            e.pack(fill="x", ipady=6)
            return e

        self._name_entry = field("Username")
        self._pass_entry = field("Password", show="•")

        hline(right, BORDER).pack(fill="x", pady=16)

        # Auth result display
        self._result_frame = tk.Frame(right, bg=CARD)
        self._result_frame.pack(fill="x")

        self._result_chip = tk.Frame(right, bg=CARD2, padx=12, pady=6)
        self._result_chip_lbl = tk.Label(self._result_chip, text="", font=FONT_EYEBROW,
                                          bg=CARD2, fg=SUBTEXT)
        self._result_chip_lbl.pack()
        self._result_chip.pack(pady=(0,10))

        self._result_lbl  = tk.Label(right, text="",  font=FONT_HEAD,
                                      bg=CARD, fg=TEXT, wraplength=220, justify="center")
        self._result_lbl.pack()
        self._dist_lbl    = tk.Label(right, text="",  font=FONT_MONO,
                                      bg=CARD, fg=SUBTEXT)
        self._dist_lbl.pack(pady=4)

        # Start camera
        if not self.cam.start():
            self._set_result("ERROR", "Camera unavailable", "", DANGER)
        self.cam.set_overlay("ENTER CREDENTIALS & VERIFY")

    def _go_back(self):
        self.cam.stop()
        self.master._show_home()

    def _set_result(self, icon, msg, dist_text, color):
        self._result_chip_lbl.config(text=icon, fg=color)
        self._result_chip.config(highlightthickness=1, highlightbackground=color)
        self._result_lbl.config(text=msg, fg=color)
        self._dist_lbl.config(text=dist_text)

    def _login(self):
        from database import get_user_by_name
        from face_utils import get_face_encoding, compare_faces
        from log_utils import log_result

        name = self._name_entry.get().strip()
        pw   = self._pass_entry.get().strip()

        if not name or not pw:
            self._set_result("PENDING", "Fill in all fields", "", WARNING)
            return

        user = get_user_by_name(name)
        if user is None:
            log_result(name, "DENIED", reason="Username not found")
            self._set_result("DENIED", "User not found", "", DANGER)
            return

        frame = self.cam.get_frame()
        if frame is None:
            self._set_result("ERROR", "No camera frame", "", DANGER)
            return

        self._set_result("CHECKING", "Verifying face...", "", WARNING)
        self.update()

        encoding, info = get_face_encoding(frame)
        if encoding is None:
            log_result(name, "DENIED", reason=f"Face extraction: {info}")
            self._set_result("DENIED", info, "", DANGER)
            return

        face_match, distance = compare_faces(user["face_encoding"], encoding)
        password_match       = (pw == user["password"])

        dist_txt = f"Distance: {distance:.4f}  (threshold 0.45)"

        if face_match and password_match:
            log_result(name, "GRANTED", similarity=distance,
                       reason="Face and password matched")
            self._set_result("GRANTED", f"Access Granted\nWelcome, {name}", dist_txt, SUCCESS)
            self.cam.stop()
            self.after(1200, lambda: self.master._show_dashboard(user))
        else:
            reasons = []
            if not face_match:     reasons.append("Face mismatch")
            if not password_match: reasons.append("Wrong password")
            reason_text = ", ".join(reasons)
            log_result(name, "DENIED", similarity=distance, reason=reason_text)
            self._set_result("DENIED", f"Access Denied\n{reason_text}", dist_txt, DANGER)
            self._shake()

    def _shake(self):
        """Brief shake animation on the verify button."""
        btn = self._verify_btn
        orig_x = btn.winfo_x()
        for dx in [6,-6,4,-4,2,-2,0]:
            btn.place(x=orig_x+dx)
            btn.update()
            time.sleep(0.04)


# ── Dashboard Screen ──
class DashboardScreen(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=CARD, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Frame(sidebar, bg=ACCENT, width=2).place(x=0, y=0, relheight=1)

        tk.Frame(sidebar, bg=CARD, height=20).pack()

        # Avatar circle
        av_canvas = tk.Canvas(sidebar, width=80, height=80, bg=CARD,
                               highlightthickness=0)
        av_canvas.pack(pady=(10,8))
        av_canvas.create_oval(4,4,76,76, outline=ACCENT, width=2)
        initials = self.user["name"][:2].upper()
        av_canvas.create_text(40,40, text=initials,
                               font=("Segoe UI",20,"bold"), fill=ACCENT)

        label(sidebar, self.user["name"], font=FONT_HEAD,
              color=TEXT, bg=CARD).pack()
        status_badge(sidebar, "Authenticated", SUCCESS).pack(pady=(6,20))

        hline(sidebar, BORDER).pack(fill="x", padx=16, pady=4)

        nav_items = [
            ("Overview",    self._show_overview),
            ("My Face",     self._show_face_image),
            ("Access Logs", self._show_logs),
        ]
        self._nav_btns = []
        for txt, cmd in nav_items:
            btn = tk.Button(sidebar, text=txt, command=cmd,
                            bg=CARD, fg=TEXT, activebackground=CARD2,
                            activeforeground=ACCENT, font=FONT_BODY,
                            relief="flat", anchor="w", padx=22, pady=11,
                            cursor="hand2", bd=0, highlightthickness=0)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e,b=btn: b.config(bg=CARD2, fg=ACCENT))
            btn.bind("<Leave>", lambda e,b=btn: b.config(bg=CARD, fg=TEXT))
            self._nav_btns.append(btn)

        tk.Frame(sidebar, bg=CARD).pack(expand=True)

        ghost_btn(sidebar, "Logout", self._logout, width=14, pady=8).pack(pady=16)

        # Main content area
        self._content = tk.Frame(self, bg=BG)
        self._content.pack(side="right", fill="both", expand=True)

        self._show_overview()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    def _logout(self):
        self.master._show_home()

    # ── Overview panel ──
    def _show_overview(self):
        self._clear_content()
        c = self._content

        eyebrow(c, "Admin Console", color=ACCENT, bg=BG).pack(anchor="w", padx=28, pady=(26,8))
        label(c, "Dashboard Overview", font=FONT_TITLE, color=TEXT).pack(
            anchor="w", padx=28, pady=(0,4))
        label(c, f"Session started  ·  {time.strftime('%Y-%m-%d %H:%M')}",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", padx=28, pady=(0,22))

        # Stats cards
        cards_row = tk.Frame(c, bg=BG)
        cards_row.pack(fill="x", padx=28)

        from log_utils import read_logs
        logs = read_logs(limit=100)
        granted = sum(1 for r in logs if r[2]=="GRANTED")
        denied  = sum(1 for r in logs if r[2]=="DENIED")

        stats = [
            ("Total Logins",   str(len(logs)),  ACCENT),
            ("Access Granted", str(granted),    SUCCESS),
            ("Access Denied",  str(denied),     DANGER),
        ]
        for title, val, color in stats:
            card = tk.Frame(cards_row, bg=CARD, padx=22, pady=18,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", padx=(0,12), fill="x", expand=True)
            tk.Frame(card, bg=color, height=2, width=28).pack(anchor="w", pady=(0,10))
            tk.Label(card, text=val,   font=("Segoe UI",30,"bold"),
                     bg=CARD, fg=color).pack(anchor="w")
            tk.Label(card, text=title, font=FONT_SMALL,
                     bg=CARD, fg=SUBTEXT).pack(anchor="w")

        hline(c, BORDER).pack(fill="x", padx=28, pady=22)

        eyebrow(c, "Latest", color=ACCENT, bg=BG).pack(anchor="w", padx=28, pady=(0,8))
        label(c, "Recent Activity", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=28, pady=(0,12))

        recent = read_logs(limit=5)
        if recent:
            for row in recent:
                timestamp, username, status, distance, reason = row
                color = SUCCESS if status=="GRANTED" else DANGER
                r = tk.Frame(c, bg=CARD, padx=18, pady=11,
                             highlightthickness=1, highlightbackground=BORDER)
                r.pack(fill="x", padx=28, pady=3)
                tk.Frame(r, bg=color, width=3).pack(side="left", fill="y", padx=(0,12))
                tk.Label(r, text=f"{timestamp}   {username}   {status}",
                         font=FONT_MONO, bg=CARD, fg=TEXT).pack(side="left")
                tk.Label(r, text=f"dist {distance}",
                         font=FONT_SMALL, bg=CARD, fg=SUBTEXT).pack(side="right")
        else:
            label(c, "No activity yet.", font=FONT_BODY,
                  color=SUBTEXT).pack(padx=28, pady=8, anchor="w")

    # ── Face Image panel ──
    def _show_face_image(self):
        self._clear_content()
        c = self._content

        eyebrow(c, "Identity", color=ACCENT, bg=BG).pack(anchor="w", padx=28, pady=(26,8))
        label(c, "Registered Face Image", font=FONT_TITLE, color=TEXT).pack(
            anchor="w", padx=28, pady=(0,4))
        label(c, "The face encoding anchor used for authentication",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", padx=28, pady=(0,20))

        path = self.user.get("image_path")
        if path and os.path.isfile(path):
            img_cv = cv2.imread(path)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            h, w   = img_cv.shape[:2]
            scale  = min(400/w, 340/h)
            img_cv = cv2.resize(img_cv, (int(w*scale), int(h*scale)))
            photo  = ImageTk.PhotoImage(Image.fromarray(img_cv))

            img_frame = tk.Frame(c, bg=CARD, highlightthickness=1,
                                  highlightbackground=BORDER)
            img_frame.pack(padx=28, pady=8, anchor="w")
            lbl = tk.Label(img_frame, image=photo, bg=CARD)
            lbl.image = photo
            lbl.pack(padx=4, pady=4)

            label(c, path, font=FONT_MONO,
                  color=SUBTEXT).pack(anchor="w", padx=28, pady=4)
        else:
            status_badge(c, "Image not found", DANGER).pack(padx=28, pady=40, anchor="w")

    # ── Logs panel ──
    def _show_logs(self):
        self._clear_content()
        c = self._content

        eyebrow(c, "Audit Trail", color=ACCENT, bg=BG).pack(anchor="w", padx=28, pady=(26,8))
        label(c, "Access Logs", font=FONT_TITLE, color=TEXT).pack(
            anchor="w", padx=28, pady=(0,4))
        label(c, "Most recent 20 authentication attempts",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", padx=28, pady=(0,16))

        # Table header
        cols    = ["Timestamp", "User", "Status", "Distance", "Reason"]
        widths  = [160, 100, 80, 80, 200]

        header = tk.Frame(c, bg=CARD2, highlightthickness=1,
                           highlightbackground=BORDER)
        header.pack(fill="x", padx=28)
        for col, w in zip(cols, widths):
            tk.Label(header, text=col, width=w//8, font=FONT_LABEL,
                     bg=CARD2, fg=ACCENT, anchor="w",
                     padx=8, pady=8).pack(side="left")

        # Scrollable rows
        outer = tk.Frame(c, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=(0,16))

        scrollbar = tk.Scrollbar(outer)
        scrollbar.pack(side="right", fill="y")

        canvas = tk.Canvas(outer, bg=BG, yscrollcommand=scrollbar.set,
                           highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)

        rows_frame = tk.Frame(canvas, bg=BG)
        canvas.create_window((0,0), window=rows_frame, anchor="nw")

        from log_utils import read_logs
        logs = read_logs(limit=20)

        if not logs:
            tk.Label(rows_frame, text="No log entries found.",
                     font=FONT_BODY, bg=BG, fg=SUBTEXT).pack(pady=20)
        else:
            for i, row in enumerate(logs):
                timestamp, username, status, distance, reason = row
                color  = SUCCESS if status=="GRANTED" else DANGER
                row_bg = CARD if i%2==0 else CARD2

                row_f = tk.Frame(rows_frame, bg=row_bg,
                                  highlightthickness=0)
                row_f.pack(fill="x")

                cells = [timestamp, username, "", distance, reason]
                for val, w in zip(cells, widths):
                    tk.Label(row_f, text=val, width=w//8, font=FONT_MONO,
                             bg=row_bg, fg=TEXT, anchor="w",
                             padx=8, pady=5).pack(side="left")
                    if val == "":   # status cell with badge
                        pass

                # Status badge in correct position 
                for w in row_f.winfo_children():
                    w.destroy()

                data_cells = [timestamp, username, status, distance, reason]
                for j,(val,w) in enumerate(zip(data_cells, widths)):
                    if j == 2:
                        f = tk.Frame(row_f, bg=row_bg, width=w)
                        f.pack(side="left", padx=4, pady=3)
                        tk.Label(f, text=val, font=FONT_SMALL,
                                 bg=color, fg=BG, padx=6, pady=2).pack()
                    else:
                        tk.Label(row_f, text=val, width=w//8, font=FONT_MONO,
                                 bg=row_bg, fg=TEXT, anchor="w",
                                 padx=8, pady=5).pack(side="left")

        rows_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


# ── User Login Screen 
class UserLoginScreen(tk.Frame):
    """A login-only screen for regular users. Users cannot register
    themselves here — accounts are created by an admin via HomeScreen ->
    RegisterScreen. On success this routes to WelcomeScreen instead of the
    admin DashboardScreen."""
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self._build()

    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=CARD, height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ghost_btn(topbar, "Back", self._go_back, width=7, pady=4).pack(
                   side="left", padx=12, pady=8)
        eyebrow(topbar, "User", color=SUBTEXT, bg=CARD).pack(side="left", padx=(4,10))
        label(topbar, "User Login", font=FONT_HEAD,
              color=TEXT, bg=CARD).pack(side="left")
        status_badge(topbar, "Scanning", ACCENT).pack(side="right", padx=16, pady=10)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Left: camera
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        eyebrow(left, "Camera", color=ACCENT, bg=BG).pack(anchor="w", pady=(0,6))
        label(left, "Look directly at the camera",
              font=FONT_SMALL, color=SUBTEXT).pack(anchor="w", pady=(0,8))

        self.cam = CameraWidget(left, width=480, height=340)
        self.cam.pack()

        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(pady=12)
        self._verify_btn = styled_btn(btn_row, "Verify & Login",
                                       self._login, color=ACCENT, fg=BG,
                                       width=20, pady=10)
        self._verify_btn.pack(side="left", padx=6)

        # Right: credentials
        right = tk.Frame(body, bg=CARD, padx=28, pady=24)
        right.pack(side="right", fill="y", padx=(16,0))
        right.config(highlightthickness=1, highlightbackground=BORDER)

        eyebrow(right, "Step 2", color=ACCENT, bg=CARD).pack(anchor="w")
        label(right, "Your Credentials", font=FONT_HEAD, color=TEXT, bg=CARD).pack(anchor="w", pady=(4,0))
        label(right, "Registered by your administrator", font=FONT_SMALL,
              color=SUBTEXT, bg=CARD).pack(anchor="w", pady=(4,0))
        hline(right, BORDER).pack(fill="x", pady=12)

        def field(lbl, show=None):
            label(right, lbl, font=FONT_LABEL, color=SUBTEXT, bg=CARD).pack(anchor="w", pady=(8,2))
            e = styled_entry(right, show=show, width=26)
            e.pack(fill="x", ipady=6)
            return e

        self._name_entry = field("Username")
        self._pass_entry = field("Password", show="•")

        hline(right, BORDER).pack(fill="x", pady=16)

        # Auth result display
        self._result_chip = tk.Frame(right, bg=CARD2, padx=12, pady=6)
        self._result_chip_lbl = tk.Label(self._result_chip, text="", font=FONT_EYEBROW,
                                          bg=CARD2, fg=SUBTEXT)
        self._result_chip_lbl.pack()
        self._result_chip.pack(pady=(0,10))

        self._result_lbl  = tk.Label(right, text="",  font=FONT_HEAD,
                                      bg=CARD, fg=TEXT, wraplength=220, justify="center")
        self._result_lbl.pack()
        self._dist_lbl    = tk.Label(right, text="",  font=FONT_MONO,
                                      bg=CARD, fg=SUBTEXT)
        self._dist_lbl.pack(pady=4)

        # Start camera
        if not self.cam.start():
            self._set_result("ERROR", "Camera unavailable", "", DANGER)
        self.cam.set_overlay("ENTER CREDENTIALS & VERIFY")

    def _go_back(self):
        self.cam.stop()
        self.master._show_index()

    def _set_result(self, icon, msg, dist_text, color):
        self._result_chip_lbl.config(text=icon, fg=color)
        self._result_chip.config(highlightthickness=1, highlightbackground=color)
        self._result_lbl.config(text=msg, fg=color)
        self._dist_lbl.config(text=dist_text)

    def _login(self):
        from database import get_user_by_name
        from face_utils import get_face_encoding, compare_faces
        from log_utils import log_result

        name = self._name_entry.get().strip()
        pw   = self._pass_entry.get().strip()

        if not name or not pw:
            self._set_result("PENDING", "Fill in all fields", "", WARNING)
            return

        user = get_user_by_name(name)
        if user is None:
            log_result(name, "DENIED", reason="Username not found")
            self._set_result("DENIED", "User not found", "", DANGER)
            return

        frame = self.cam.get_frame()
        if frame is None:
            self._set_result("ERROR", "No camera frame", "", DANGER)
            return

        self._set_result("CHECKING", "Verifying face...", "", WARNING)
        self.update()

        encoding, info = get_face_encoding(frame)
        if encoding is None:
            log_result(name, "DENIED", reason=f"Face extraction: {info}")
            self._set_result("DENIED", info, "", DANGER)
            return

        face_match, distance = compare_faces(user["face_encoding"], encoding)
        password_match       = (pw == user["password"])

        dist_txt = f"Distance: {distance:.4f}  (threshold 0.45)"

        if face_match and password_match:
            log_result(name, "GRANTED", similarity=distance,
                       reason="Face and password matched")
            self._set_result("GRANTED", f"Access Granted\nWelcome, {name}", dist_txt, SUCCESS)
            self.cam.stop()
            self.after(1200, lambda: self.master._show_welcome(user))
        else:
            reasons = []
            if not face_match:     reasons.append("Face mismatch")
            if not password_match: reasons.append("Wrong password")
            reason_text = ", ".join(reasons)
            log_result(name, "DENIED", similarity=distance, reason=reason_text)
            self._set_result("DENIED", f"Access Denied\n{reason_text}", dist_txt, DANGER)


# ── Welcome Screen (post-login landing page for regular users) ───────────────
# ── Welcome Screen (post-login landing page for regular users) ───────────────
class WelcomeScreen(tk.Frame):
    """Shown to a regular user right after a successful UserLoginScreen
    login. Provides a friendly welcome plus an 'About' section, and a way
    to view their own registered face image and recent access history."""
    def __init__(self, master, user):
        super().__init__(master, bg=BG)
        self.user = user
        self._build()

    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=CARD, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=ACCENT, height=2).place(x=0, y=0, relwidth=1)

        avatar = tk.Canvas(topbar, width=36, height=36, bg=CARD,
                           highlightthickness=0)
        avatar.pack(side="left", padx=(20,8), pady=10)
        avatar.create_oval(2,2,34,34, outline=ACCENT, width=2)
        avatar.create_text(18,18, text=self.user["name"][:2].upper(),
                           font=("Segoe UI",10,"bold"), fill=ACCENT)

        title_box = tk.Frame(topbar, bg=CARD)
        title_box.pack(side="left", padx=4)
        label(title_box, self.user['name'], font=FONT_HEAD,
              color=TEXT, bg=CARD).pack(anchor="w")
        eyebrow(title_box, "Signed In", color=SUCCESS, bg=CARD).pack(anchor="w")

        ghost_btn(topbar, "Logout", self._logout, width=9, pady=4).pack(
            side="right", padx=16, pady=10)

        # Scrollable body
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(outer)
        scrollbar.pack(side="right", fill="y")
        canvas = tk.Canvas(outer, bg=BG, yscrollcommand=scrollbar.set,
                           highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)

        body = tk.Frame(canvas, bg=BG)
        canvas.create_window((0,0), window=body, anchor="nw", width=960)
        body.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

        def _on_mousewheel(e):
            try:
                canvas.yview_scroll(int(-e.delta/40), "units")
            except tk.TclError:
                pass

        def _bind_wheel(e):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(e):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        self.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Hero
        hero = tk.Frame(body, bg=CARD, padx=34, pady=30,
                        highlightthickness=1, highlightbackground=BORDER)
        hero.pack(fill="x", padx=40, pady=(30,18))
        status_badge(hero, "Verified", SUCCESS).pack(anchor="w")
        tk.Label(hero, text=f"You're signed in, {self.user['name']}",
                 font=("Segoe UI", 22, "bold"), bg=CARD, fg=TEXT).pack(anchor="w", pady=(12,4))
        tk.Label(hero, text="Your identity was verified using your password and a "
                 "real-time facial recognition check.",
                 font=FONT_BODY, bg=CARD, fg=SUBTEXT, wraplength=820,
                 justify="left").pack(anchor="w")

        # About section
        eyebrow(body, "Session Details", color=ACCENT, bg=BG).pack(anchor="w", padx=40, pady=(6,8))
        label(body, "About this session", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=40, pady=(0,14))

        about_row = tk.Frame(body, bg=BG)
        about_row.pack(fill="x", padx=40, pady=(0,22))

        def info_card(parent, num, title, desc):
            card = tk.Frame(parent, bg=CARD, padx=20, pady=18,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(card, text=num, font=("Segoe UI", 18, "bold"), bg=CARD,
                     fg=ACCENT).pack(anchor="w")
            tk.Label(card, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT,
                     anchor="w").pack(anchor="w", pady=(8,4))
            tk.Label(card, text=desc, font=FONT_SMALL, bg=CARD, fg=SUBTEXT,
                     anchor="w", justify="left", wraplength=190).pack(anchor="w")
            return card

        info_card(about_row, "01", "How you were verified",
                  "Your password was checked, and your live webcam face encoding "
                  "was compared against the one captured at registration.")
        info_card(about_row, "02", "Account managed by admin",
                  "Your username, password and face data were registered by an "
                  "administrator. Contact them to update your details.")
        info_card(about_row, "03", "Activity is logged",
                  "Every login attempt, granted or denied, is recorded with a "
                  "timestamp for security auditing.")

        hline(body, BORDER).pack(fill="x", padx=40, pady=14)

        # My face + recent activity
        eyebrow(body, "Account", color=ACCENT, bg=BG).pack(anchor="w", padx=40, pady=(10,8))
        label(body, "Your Account", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=40, pady=(0,14))

        account_row = tk.Frame(body, bg=BG)
        account_row.pack(fill="x", padx=40, pady=(0,44))

        # Face preview card
        face_card = tk.Frame(account_row, bg=CARD, padx=22, pady=20,
                             highlightthickness=1, highlightbackground=BORDER)
        face_card.pack(side="left", fill="y", padx=(0,10))
        eyebrow(face_card, "Identity", color=SUBTEXT, bg=CARD).pack(anchor="w")
        tk.Label(face_card, text="Registered Face", font=FONT_LABEL,
                 bg=CARD, fg=TEXT).pack(anchor="w", pady=(6,10))

        path = self.user.get("image_path")
        if path and os.path.isfile(path):
            img_cv = cv2.imread(path)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            h, w   = img_cv.shape[:2]
            scale  = min(200/w, 160/h)
            img_cv = cv2.resize(img_cv, (int(w*scale), int(h*scale)))
            photo  = ImageTk.PhotoImage(Image.fromarray(img_cv))
            img_lbl = tk.Label(face_card, image=photo, bg=CARD,
                               highlightthickness=1, highlightbackground=ACCENT)
            img_lbl.image = photo
            img_lbl.pack()
        else:
            status_badge(face_card, "Image not found", DANGER).pack(anchor="w")

        # Recent activity card
        log_card = tk.Frame(account_row, bg=CARD, padx=22, pady=20,
                            highlightthickness=1, highlightbackground=BORDER)
        log_card.pack(side="left", fill="both", expand=True, padx=(10,0))
        eyebrow(log_card, "History", color=SUBTEXT, bg=CARD).pack(anchor="w")
        tk.Label(log_card, text="Your Recent Logins", font=FONT_LABEL,
                 bg=CARD, fg=TEXT).pack(anchor="w", pady=(6,10))

        from log_utils import read_logs
        my_logs = [r for r in read_logs(limit=50) if r[1] == self.user["name"]][:5]
        if my_logs:
            for row in my_logs:
                timestamp, username, status, distance, reason = row
                color = SUCCESS if status == "GRANTED" else DANGER
                r = tk.Frame(log_card, bg=CARD2, padx=12, pady=7)
                r.pack(fill="x", pady=2)
                tk.Frame(r, bg=color, width=3).pack(side="left", fill="y", padx=(0,10))
                tk.Label(r, text=timestamp, font=FONT_MONO,
                         bg=CARD2, fg=TEXT).pack(side="left")
                tk.Label(r, text=status, font=FONT_SMALL, bg=CARD2,
                         fg=color).pack(side="right")
        else:
            tk.Label(log_card, text="No login history yet.", font=FONT_SMALL,
                     bg=CARD, fg=SUBTEXT).pack(anchor="w")

    def _logout(self):
        self.master._show_index()