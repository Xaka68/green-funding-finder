CATEGORY_COLORS = {
    "Kommunal": "#4caf50",
    "Bundesland": "#2196f3",
    "Bund": "#ff9800",
    "EU": "#9c27b0",
    "Sonstige": "#607d8b"
}

def get_category_color(ebene: str):
    return CATEGORY_COLORS.get(ebene, CATEGORY_COLORS["Sonstige"])
