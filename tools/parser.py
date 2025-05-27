from typing import List, NamedTuple, Optional
from enum import IntEnum
from bs4 import BeautifulSoup

from models.chart import DifficultyLabel
import re

# CSS selector for each record entry panel
RECORD_DIV_SELECTOR = "div.w_450.m_15.p_r.f_0"

# Regex patterns for detecting icons
_DIFF_PATTERN = re.compile(r"diff_(.*)\.png")
_MUSIC_PATTERN = re.compile(r"music_(.*)\.png")
_ICON_PATTERN = re.compile(r"music_icon_(.+?)\.png")

class RecordEntry(NamedTuple):
    title: str
    level_label: str
    difficulty: DifficultyLabel
    is_dx: bool
    achievement_rate: float
    dx_score: int
    rate_icon: str
    fc_icon: str
    fs_icon: str
    ds: int = 0


def parse_records_html(html: str) -> List[RecordEntry]:
    """Parse the HTML of a maimai DX NET page into a list of RecordEntry."""
    soup = BeautifulSoup(html, "html.parser")
    records: List[RecordEntry] = []
    for div in soup.select(RECORD_DIV_SELECTOR):
        entry = get_records_div(div)
        if entry is not None:
            records.append(entry)
    return records


def get_records_div(div) -> Optional[RecordEntry]:
    form = div.find("form")
    if not form or len(form.contents) != 23:
        return None

    src = form.contents[1].attrs["src"]
    chart_type = (_DIFF_PATTERN.search(src) or _MUSIC_PATTERN.search(src)).group(1)
    is_dx = chart_type != "standard"

    if "remaster" in src:
        difficulty = DifficultyLabel.remaster
    elif "master" in src:
        difficulty = DifficultyLabel.master
    elif "expert" in src:
        difficulty = DifficultyLabel.expert
    elif "advanced" in src:
        difficulty = DifficultyLabel.advanced
    else:
        difficulty = DifficultyLabel.basic

    # Title and level name
    title = form.contents[7].string or ""
    level_label = form.contents[5].string or ""

    # DX score
    score_txt = form.contents[11].contents[1].string or ""
    raw_score, raw_full = (s.strip().replace(",", "") for s in score_txt.split("/"))
    dx_score = int(raw_score)

    # Achievements
    achievement_text = form.contents[9].string or "0%"
    achievement_rate = float(achievement_text.rstrip("%"))

    # Helper to extract icon names
    def _extract_icon(src: str) -> str:
        m = _ICON_PATTERN.search(src)
        name = m.group(1) if m else ""
        return "" if name == "back" else name

    rate_icon = _extract_icon(form.contents[17].attrs["src"])
    fc_icon = _extract_icon(form.contents[15].attrs["src"])
    fs_icon = _extract_icon(form.contents[13].attrs["src"])

    return RecordEntry(
        title=title,
        level_label=level_label,
        difficulty=difficulty,
        is_dx=is_dx,
        achievement_rate=achievement_rate,
        dx_score=dx_score,
        rate_icon=rate_icon,
        fc_icon=fc_icon,
        fs_icon=fs_icon,
    )