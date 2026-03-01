# styles.py
import customtkinter as ctk

G_BLUE, G_RED = "#1A73E8", "#D93025"
G_BG, G_WINDOW_BG = "#FFFFFF", "#F8F9FA"
G_TEXT, G_SUBTEXT, G_BORDER = "#202124", "#5F6368", "#DADCE0"

FONT_H1 = ("Segoe UI", 28, "bold")
FONT_H2 = ("Segoe UI", 18, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_LABEL_BOLD = ("Segoe UI", 12, "bold") # <--- Add this line
FONT_BODY_BOLD = ("Segoe UI", 14, "bold")
G_BLUE, G_RED = "#1A73E8", "#D93025"
G_GREEN, G_YELLOW = "#1E8E3E", "#F9AB00"  # New Pulse Colors
G_BG, G_WINDOW_BG = "#FFFFFF", "#F8F9FA"
G_TEXT, G_SUBTEXT, G_BORDER = "#202124", "#5F6368", "#DADCE0"

# New Font for the big Pulse Numbers
FONT_PULSE = ("Segoe UI", 42, "bold")

def apply_material_button(btn, variant="primary"):
    if variant == "primary":
        btn.configure(fg_color=G_BLUE, text_color="white", hover_color="#1765CC", corner_radius=22, height=40)
    else:
        btn.configure(fg_color="transparent", text_color=G_TEXT, hover_color="#F1F3F4", corner_radius=22, height=40, border_width=1, border_color=G_BORDER)

def create_material_input(parent, label, ph):
    ctk.CTkLabel(parent, text=f"  {label}", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
    e = ctk.CTkEntry(parent, width=400, height=45, placeholder_text=ph, fg_color="white", border_color=G_BORDER, corner_radius=8)
    e.pack(pady=5)
    return e

def create_material_dropdown(parent, label, values):
    ctk.CTkLabel(parent, text=f"  {label}", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
    m = ctk.CTkOptionMenu(parent, values=values, width=400, height=45, fg_color="#F1F3F4", button_color="#F1F3F4", text_color=G_TEXT, corner_radius=8)
    m.pack(pady=5)
    return m