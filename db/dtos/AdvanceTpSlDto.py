import datetime
import json
from dataclasses import dataclass, asdict

from config import logger


@dataclass
class AdvanceTpSlDto:
    quantity : int = 0
    tp: float = 0
    sl: float = 0

    percentage_tp: float = 0
    percentage_sl: float = 0

    dollar_tp: float = 0
    dollar_sl: float = 0

    trail: float = 0
    trail_stop: float = 0
    trail_trigger: float = 0
    trail_freq: float = 0
    breakeven: float = 0

    def __str__(self):
            return json.dumps(asdict(self))

