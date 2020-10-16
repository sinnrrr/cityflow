from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    is_moving = os.getenv("TK_IS_MOVING") != "0"
    is_terminable = os.getenv("TK_IS_TERMINABLE") != "0"
    is_fullscreen = os.getenv("TK_IS_FULLSCREEN") != "0"

    pause = int(os.getenv("PAUSE"))

    covers = {
        0: (2, "#404040", "#808080"),
        1: (3, "#FF0000", "#FF4040"),
        2: (5, "#FF8000", "#FFB0B0"),
        3: (8, "#E0E000", "#FFFF00"),
        4: (12, "#70E020", "#90FF40"),
        5: (17, "#00E000", "#00FF00")
    }
