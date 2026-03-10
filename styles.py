import customtkinter as ctk

# --- 1. Adaptive Color Palette ---
# Format: ("Light Mode Color", "Dark Mode Color")
G_BLUE = ("#1A73E8", "#8AB4F8")
G_RED = ("#D93025", "#F28B82")
G_GREEN = ("#1E8E3E", "#81C995")
G_YELLOW = ("#F9AB00", "#FDD663")
G_ORANGE = ("#F39C12", "#FFBB66")

# Backgrounds
G_BG = ("#FFFFFF", "#2D2D2D")        # Card/Container background
G_WINDOW_BG = ("#F8F9FA", "#1A1A1B") # Main application background

# Typography & Borders
G_TEXT = ("#202124", "#E8EAED")      # Near-black / Near-white
G_SUBTEXT = ("#3E4145", "#767677")   # The "Grey" text (brightened for Dark Mode)
G_CONTENTTEXT=("#111111", "#2F2F2F")   # For primary content text, slightly brighter than G_TEXT
G_BORDER = ("#DADCE0", "#3F3F40")    # Subtle borders
G_BUTTON_TEXT = ("#FFFFFF", "#202124") # For text on colored buttons

# --- 2. Typography ---
FONT_H1 = ("Segoe UI", 28, "bold")
FONT_H2 = ("Segoe UI", 18, "bold")
FONT_PULSE = ("Segoe UI", 42, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_BODY_BOLD = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_LABEL_BOLD = ("Segoe UI", 12, "bold")

# --- 3. Component Factories ---

def apply_material_button(btn, variant="primary"):
    if variant == "primary":
        btn.configure(
            fg_color=G_BLUE, 
            text_color=("white", "#202124"), # Dark text on light blue in Dark Mode
            hover_color=("#1765CC", "#AECBFA"), 
            corner_radius=22, 
            height=40
        )
    else:
        btn.configure(
            fg_color="transparent", 
            text_color=G_TEXT, 
            hover_color=("#F1F3F4", "#3C4043"), 
            corner_radius=22, 
            height=40, 
            border_width=1, 
            border_color=G_BORDER
        )

def create_material_input(parent, label, ph):
    ctk.CTkLabel(parent, text=f"  {label}", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
    # Changed fg_color to G_BG to allow it to turn dark
    e = ctk.CTkEntry(
        parent, width=400, height=45, 
        placeholder_text=ph, 
        fg_color=G_BG, 
        text_color=G_TEXT,
        border_color=G_BORDER, 
        corner_radius=8
    )
    e.pack(pady=5)
    return e

def create_material_dropdown(parent, label, values):
    ctk.CTkLabel(parent, text=f"  {label}", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
    # Changed colors to adaptive variables
    m = ctk.CTkOptionMenu(
        parent, values=values, width=400, height=45, 
        fg_color=G_BORDER, 
        button_color=G_BORDER, 
        text_color=G_TEXT, 
        corner_radius=8
    )
    m.pack(pady=5)
    return m