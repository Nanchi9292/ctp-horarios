import os
from pathlib import Path

class Config:
    # Database
    DB_NAME = "horario.db"
    DB_PATH = str(Path(__file__).parent / DB_NAME)

    # Auth
    SECRET_KEY = os.getenv("CTP_SECRET_KEY", "default_secret_key")
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

    # App
    TIME_SLOTS = [
        "7:00 - 7:40", "7:40 - 8:20", "8:20 - 9:00",
        "9:20 - 10:00", "10:00 - 10:40", "10:40 - 11:20",
        "12:10 - 12:50", "12:50 - 13:30", "13:30 - 14:10",
        "14:30 - 15:10", "15:10 - 15:50", "15:50 - 16:30"
    ]

    DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    GROUPS = ["7-1", "7-4", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2"]
    SUBJECT_COLORS = {
        "Matemática": "#FFD700", "Español": "#FF6347", "Ciencias": "#7CFC00",
        "Inglés": "#1E90FF", "Sociales": "#9370DB", "Francés": "#FF69B4",
        "Religión": "#A52A2A", "Música": "#FF8C00", "Educación Física": "#008080",
        "TIC": "#4682B4", "Talleres": "#32CD32", "ALMUERZO": "#696969"
    }
