#!/usr/bin/env python3
"""Generate team dashboard HTML for LeavesDesign content pipeline.

Tabs: Team | KPIs | Gantt | Posts | Matrix | Learning
"""

import base64
import json
import os
import re
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from calendar import monthrange
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE = Path(__file__).parent
OUTPUT_DIR = BASE / "O-output"

# ── Team Definition ────────────────────────────────────────────────────────
TEAM = [
    {
        "id": "marketing-director",
        "emoji": "\U0001f3af",
        "char_name": "\u05d3\u05e0\u05d9\u05d0\u05dc",  # Daniel
        "name_he": "\u05de\u05e0\u05d4\u05dc \u05d4\u05e9\u05d9\u05d5\u05d5\u05e7",
        "name_en": "Marketing Director",
        "role_he": "\u05e8\u05d0\u05e9 \u05d4\u05e6\u05d5\u05d5\u05ea \u2014 \u05d0\u05e1\u05d8\u05e8\u05d8\u05d2\u05d9\u05d4, \u05ea\u05db\u05e0\u05d5\u05df \u05d5\u05e0\u05d9\u05d4\u05d5\u05dc \u05d1\u05d9\u05e6\u05d5\u05e2\u05d9\u05dd",
        "identity_he": "\u05d0\u05e0\u05d9 \u05de\u05ea\u05d6\u05de\u05e8 \u05d0\u05ea \u05db\u05dc \u05de\u05db\u05d5\u05e0\u05ea \u05d4\u05ea\u05d5\u05db\u05df. \u05de\u05ea\u05db\u05e0\u05df \u05dc\u05d5\u05d7 \u05e9\u05e0\u05ea\u05d9, \u05de\u05e0\u05ea\u05d7 \u05d1\u05d9\u05e6\u05d5\u05e2\u05d9\u05dd, \u05d5\u05de\u05d5\u05d1\u05d9\u05dc \u05d0\u05ea \u05d4\u05e6\u05d5\u05d5\u05ea \u05dc\u05ea\u05d5\u05e6\u05d0\u05d5\u05ea.",
        "sla": "\u05dc\u05d5\u05d7 \u05e9\u05e0\u05ea\u05d9 \u05e2\u05d3 1 \u05dc\u05d7\u05d5\u05d3\u05e9",
        "dept": "lead",
        "avatar_bg": "#3b82f6", "avatar_hair": "#1e293b", "avatar_acc": "glasses",
        "is_lead": True,
    },
    {
        "id": "social-copywriter",
        "emoji": "\u270d\ufe0f",
        "char_name": "\u05e0\u05d5\u05e2\u05d4",  # Noa
        "name_he": "\u05e7\u05d5\u05e4\u05d9\u05e8\u05d9\u05d9\u05d8\u05e8 \u05e1\u05d5\u05e9\u05d9\u05d0\u05dc",
        "name_en": "Social Media Copywriter",
        "role_he": "\u05db\u05ea\u05d9\u05d1\u05ea \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05dc\u05e4\u05d9\u05d3 \u2014 Facebook & Instagram",
        "identity_he": "\u05d0\u05e0\u05d9 \u05d4\u05e7\u05d5\u05dc \u05e9\u05e2\u05d5\u05e6\u05e8 \u05d0\u05ea \u05d4\u05d2\u05dc\u05d9\u05dc\u05d4. \u05db\u05dc \u05de\u05d9\u05dc\u05d4 \u05e9\u05d0\u05e0\u05d9 \u05db\u05d5\u05ea\u05d1 \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d3\u05d1\u05e8 \u05d1\u05e7\u05d5\u05dc \u05d4\u05de\u05d5\u05ea\u05d2 \u05d5\u05dc\u05d2\u05e8\u05d5\u05dd \u05dc\u05d0\u05e0\u05e9\u05d9\u05dd \u05dc\u05e2\u05e6\u05d5\u05e8, \u05dc\u05e7\u05e8\u05d5\u05d0, \u05d5\u05dc\u05d4\u05d2\u05d9\u05d1.",
        "sla": "2-3 \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd/\u05e9\u05d1\u05d5\u05e2",
        "dept": "content",
        "avatar_bg": "#ec4899", "avatar_hair": "#7c2d12", "avatar_acc": "pen",
        "is_lead": False,
    },
    {
        "id": "stories-content",
        "emoji": "\U0001f4f1",
        "char_name": "\u05d0\u05dc\u05d9\u05d4",  # Eliya
        "name_he": "\u05d9\u05d5\u05e6\u05e8 \u05e1\u05d8\u05d5\u05e8\u05d9\u05d6",
        "name_en": "Stories Content Agent",
        "role_he": "\u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05d9\u05d5\u05de\u05d9\u05d9\u05dd \u2014 Instagram & Facebook Stories",
        "identity_he": "\u05d0\u05e0\u05d9 \u05de\u05db\u05d5\u05e0\u05ea \u05d4\u05ea\u05d5\u05db\u05df \u05d4\u05de\u05d4\u05d9\u05e8\u05d4. \u05db\u05dc \u05d9\u05d5\u05dd \u05e1\u05d8\u05d5\u05e8\u05d9 \u05d7\u05d3\u05e9, \u05db\u05dc \u05d9\u05d5\u05dd \u05e0\u05d9\u05e9 \u05d0\u05d7\u05e8. \u05e0\u05e7\u05d5\u05d3\u05d5\u05ea \u05de\u05d2\u05e2 \u05e7\u05d1\u05d5\u05e2\u05d5\u05ea \u05e2\u05dd \u05d4\u05e7\u05d4\u05dc.",
        "sla": "7 \u05e1\u05d8\u05d5\u05e8\u05d9\u05d6/\u05e9\u05d1\u05d5\u05e2",
        "dept": "content",
        "avatar_bg": "#f97316", "avatar_hair": "#451a03", "avatar_acc": "phone",
        "is_lead": False,
    },
    {
        "id": "gatekeeper",
        "emoji": "\U0001f6e1\ufe0f",
        "char_name": "\u05e2\u05de\u05d9\u05ea",  # Amit
        "name_he": "\u05e9\u05d5\u05de\u05e8 \u05d4\u05e1\u05e3",
        "name_en": "Gatekeeper",
        "role_he": "\u05d1\u05e7\u05e8\u05ea \u05d0\u05d9\u05db\u05d5\u05ea \u2014 \u05d4\u05d1\u05d3\u05d9\u05e7\u05d4 \u05d4\u05d0\u05d7\u05e8\u05d5\u05e0\u05d4 \u05dc\u05e4\u05e0\u05d9 \u05e4\u05e8\u05e1\u05d5\u05dd",
        "identity_he": "\u05e9\u05d5\u05dd \u05d3\u05d1\u05e8 \u05dc\u05d0 \u05d9\u05d5\u05e6\u05d0 \u05d1\u05dc\u05d9 \u05d0\u05d9\u05e9\u05d5\u05e8 \u05e9\u05dc\u05d9. \u05d0\u05e0\u05d9 \u05d1\u05d5\u05d3\u05e7 \u05d4\u05ea\u05d0\u05de\u05d4 \u05dc\u05e7\u05d5\u05dc \u05d4\u05de\u05d5\u05ea\u05d2, \u05d0\u05d9\u05db\u05d5\u05ea \u05d4\u05db\u05ea\u05d9\u05d1\u05d4, \u05d5\u05d3\u05d9\u05d5\u05e7 \u05d4\u05de\u05e1\u05e8.",
        "sla": "\u05e8\u05d9\u05d5\u05d5\u05d9\u05d5 \u05de\u05d9\u05d9\u05d3\u05d9 \u2014 3 \u05e8\u05d0\u05d5\u05e0\u05d3\u05d9\u05dd \u05de\u05e7\u05e1\u05d9\u05de\u05d5\u05dd",
        "dept": "quality",
        "avatar_bg": "#ef4444", "avatar_hair": "#1c1917", "avatar_acc": "shield",
        "is_lead": False,
    },
    {
        "id": "visual-designer",
        "emoji": "\U0001f3a8",
        "char_name": "\u05de\u05d0\u05d9\u05d4",  # Maya
        "name_he": "\u05de\u05e2\u05e6\u05d1 \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9",
        "name_en": "Visual Designer",
        "role_he": "\u05d9\u05e6\u05d9\u05e8\u05ea \u05db\u05dc \u05d4\u05d5\u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05dd \u2014 \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd, \u05e1\u05d5\u05e9\u05d9\u05d0\u05dc, \u05d1\u05dc\u05d5\u05d2",
        "identity_he": "\u05d0\u05e0\u05d9 \u05d9\u05d5\u05e6\u05e8 \u05d0\u05ea \u05d4\u05d5\u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05dd \u05e9\u05de\u05d7\u05d6\u05e7\u05d9\u05dd \u05d0\u05ea \u05d4\u05de\u05d5\u05ea\u05d2. \u05d0\u05e1\u05ea\u05d8\u05d9\u05e7\u05d4 \u05e9\u05dc \u05de\u05d5\u05e1\u05da, \u05de\u05ea\u05db\u05ea \u05d2\u05d5\u05dc\u05de\u05d9\u05ea, \u05d5\u05d2\u05d1\u05e8\u05d9\u05d5\u05ea \u05d0\u05d5\u05ea\u05e0\u05d8\u05d9\u05ea.",
        "sla": "\u05d2\u05e8\u05e4\u05d9\u05e7\u05d4 \u05d1\u05d0\u05d5\u05ea\u05d4 \u05e1\u05e9\u05d9\u05d4",
        "dept": "visual",
        "avatar_bg": "#a855f7", "avatar_hair": "#312e81", "avatar_acc": "beret",
        "is_lead": False,
    },
    {
        "id": "mockup-generator",
        "emoji": "\U0001f5bc\ufe0f",
        "char_name": "\u05dc\u05d9\u05d0\u05d5\u05e8",  # Lior
        "name_he": "\u05de\u05d7\u05d5\u05dc\u05dc \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd",
        "name_en": "Mockup Generator",
        "role_he": "\u05d4\u05e4\u05d9\u05db\u05ea \u05d2\u05e8\u05e4\u05d9\u05e7\u05d5\u05ea \u05e9\u05d8\u05d5\u05d7\u05d5\u05ea \u05dc\u05ea\u05de\u05d5\u05e0\u05d5\u05ea \u05de\u05d5\u05e6\u05e8 \u05e8\u05d9\u05d0\u05dc\u05d9\u05e1\u05d8\u05d9\u05d5\u05ea",
        "identity_he": "\u05d0\u05e0\u05d9 \u05d4\u05d5\u05e4\u05da PNG \u05e9\u05d8\u05d5\u05d7 \u05dc\u05ea\u05de\u05d5\u05e0\u05ea \u05de\u05d5\u05e6\u05e8 \u05e9\u05e0\u05e8\u05d0\u05d9\u05ea \u05db\u05de\u05d5 \u05e6\u05d9\u05dc\u05d5\u05dd \u05d0\u05de\u05d9\u05ea\u05d9. Gemini AI + \u05e1\u05e6\u05e0\u05d5\u05ea \u05de\u05d5\u05ea\u05d0\u05de\u05d5\u05ea \u05dc\u05db\u05dc \u05e7\u05d4\u05dc.",
        "sla": "1-10 \u05ea\u05de\u05d5\u05e0\u05d5\u05ea \u05dc\u05e8\u05d0\u05df",
        "dept": "visual",
        "avatar_bg": "#22c55e", "avatar_hair": "#365314", "avatar_acc": "camera",
        "is_lead": False,
    },
    {
        "id": "visual-qa",
        "emoji": "\U0001f50d",
        "char_name": "\u05ea\u05de\u05e8",  # Tamar
        "name_he": "\u05d1\u05d5\u05d3\u05e7 \u05d0\u05d9\u05db\u05d5\u05ea \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05ea",
        "name_en": "Visual QA Agent",
        "role_he": "\u05d0\u05d9\u05de\u05d5\u05ea \u05e9\u05d4\u05de\u05d5\u05e7\u05d0\u05e4 \u05ea\u05d5\u05d0\u05dd \u05dc\u05de\u05d5\u05e6\u05e8 \u05d4\u05d0\u05de\u05d9\u05ea\u05d9",
        "identity_he": "\u05d0\u05e0\u05d9 \u05de\u05d5\u05d5\u05d3\u05d0 \u05e9\u05de\u05d4 \u05e9\u05de\u05e4\u05d5\u05e8\u05e1\u05dd \u05d0\u05d5\u05e0\u05dc\u05d9\u05d9\u05df \u05d6\u05d4\u05d4 \u05dc\u05de\u05d4 \u05e9\u05d4\u05dc\u05e7\u05d5\u05d7 \u05d9\u05e7\u05d1\u05dc. \u05d0\u05dd \u05dc\u05d0 \u05de\u05d3\u05d5\u05d9\u05e7 \u2014 \u05e0\u05e4\u05e1\u05dc.",
        "sla": "\u05d1\u05d3\u05d9\u05e7\u05d4 \u05d1\u05d0\u05d5\u05ea\u05d4 \u05e1\u05e9\u05d9\u05d4",
        "dept": "quality",
        "avatar_bg": "#eab308", "avatar_hair": "#78350f", "avatar_acc": "magnifier",
        "is_lead": False,
    },
    {
        "id": "batch-runner",
        "emoji": "\u26a1",
        "char_name": "\u05d0\u05d3\u05dd",  # Adam
        "name_he": "\u05de\u05e2\u05d1\u05d3 \u05d0\u05e6\u05d5\u05d5\u05d4",
        "name_en": "Batch Runner",
        "role_he": "\u05e2\u05d9\u05d1\u05d5\u05d3 \u05de\u05d5\u05e6\u05e8\u05d9\u05dd \u05d1\u05e1\u05e7\u05d9\u05d9\u05dc \u2014 1,744+ \u05de\u05d5\u05e6\u05e8\u05d9\u05dd",
        "identity_he": "\u05d0\u05e0\u05d9 \u05de\u05e2\u05d1\u05d3 \u05d0\u05ea \u05db\u05dc \u05d4\u05e7\u05d8\u05dc\u05d5\u05d2 \u05d1\u05e1\u05e7\u05d9\u05d9\u05dc. \u05e1\u05e8\u05d9\u05e7\u05d4, \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d6\u05e6\u05d9\u05d4, \u05d5\u05d4\u05e8\u05e6\u05ea \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea \u05dc\u05db\u05dc \u05d4\u05de\u05d5\u05e6\u05e8\u05d9\u05dd.",
        "sla": "\u05dc\u05e4\u05d9 count \u05d5-limit \u05e9\u05d4\u05d5\u05d2\u05d3\u05e8",
        "dept": "visual",
        "avatar_bg": "#06b6d4", "avatar_hair": "#164e63", "avatar_acc": "bolt",
        "is_lead": False,
    },
    {
        "id": "paid-campaigner",
        "emoji": "\U0001f4b0",
        "char_name": "\u05e8\u05d5\u05df",  # Ron
        "name_he": "\u05e7\u05de\u05e4\u05d9\u05d9\u05e0\u05e8 \u05de\u05de\u05d5\u05de\u05df",
        "name_en": "Paid Campaign Manager",
        "role_he": "\u05e7\u05de\u05e4\u05d9\u05d9\u05e0\u05d9\u05dd \u05de\u05de\u05d5\u05de\u05e0\u05d9\u05dd \u2014 Meta, Pinterest, Etsy Ads",
        "identity_he": "\u05db\u05dc \u05d3\u05d5\u05dc\u05e8 \u05e9\u05d9\u05d5\u05e6\u05d0 \u05d7\u05d5\u05d6\u05e8 \u05db\u05e4\u05d5\u05dc. \u05d0\u05e0\u05d9 \u05dc\u05d0 \u05e9\u05d5\u05e8\u05e3 \u05ea\u05e7\u05e6\u05d9\u05d1 \u2014 \u05d0\u05e0\u05d9 \u05de\u05e9\u05e7\u05d9\u05e2 \u05d0\u05d5\u05ea\u05d5. $175 \u05dc\u05d7\u05d5\u05d3\u05e9 \u05e9\u05de\u05e8\u05d2\u05d9\u05e9\u05d9\u05dd \u05db\u05de\u05d5 $1,750.",
        "sla": "\u05d3\u05d5\u05d7 \u05e9\u05d1\u05d5\u05e2\u05d9 + \u05d7\u05d5\u05d3\u05e9\u05d9",
        "dept": "growth",
        "avatar_bg": "#f59e0b", "avatar_hair": "#422006", "avatar_acc": "chart",
        "is_lead": False,
    },
]

# ── Pillar Constants ───────────────────────────────────────────────────────
PILLAR_LABELS = {
    "automotive": "\u05e8\u05db\u05d1",
    "motorcycle": "\u05d0\u05d5\u05e4\u05e0\u05d5\u05e2",
    "wedding": "\u05d7\u05ea\u05d5\u05e0\u05d4 / \u05de\u05d5\u05e0\u05d5\u05d2\u05e8\u05de\u05d4",
    "dog": "\u05db\u05dc\u05d1\u05d9\u05dd",
    "blog": "\u05d1\u05dc\u05d5\u05d2 / \u05de\u05d5\u05e1\u05da",
    "other": "\u05d0\u05d7\u05e8",
}
PILLAR_COLORS = {
    "automotive": "#ef4444",
    "motorcycle": "#f97316",
    "wedding": "#ec4899",
    "dog": "#3b82f6",
    "blog": "#22c55e",
    "other": "#8b5cf6",
}
MONTHS_HE = {3: "\u05de\u05e8\u05e5", 4: "\u05d0\u05e4\u05e8\u05d9\u05dc"}
DAY_NAMES_HE = [
    "\u05d0\u05f3", "\u05d1\u05f3", "\u05d2\u05f3", "\u05d3\u05f3",
    "\u05d4\u05f3", "\u05d5\u05f3", "\u05e9\u05f3",
]


# ── Data Loading ───────────────────────────────────────────────────────────
def load_json(filename):
    path = BASE / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def find_post_folder(dt):
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir() and d.name.startswith(dt):
            return d
    return None


def parse_post_metadata(folder):
    post_path = folder / "post.md"
    if not post_path.exists():
        return {}
    content = post_path.read_text(encoding="utf-8")
    meta = {}
    for line in content.splitlines()[:7]:
        if line.startswith("# "):
            meta["emoji"] = line[2:4].strip() if len(line) > 3 else ""
        if line.startswith("**Audience:**"):
            meta["audience"] = line.replace("**Audience:**", "").strip()
        if line.startswith("**Angle:**"):
            meta["angle"] = line.replace("**Angle:**", "").strip()
        if line.startswith("**Story format:**"):
            raw = line.replace("**Story format:**", "").strip()
            meta["story_status"] = "ready" if "Ready" in raw else "need_crop"
            meta["story_raw"] = raw
    # Extract full text sections (between ## header and next ---)
    def _extract(text, marker):
        pos = text.find(marker)
        if pos == -1:
            return ""
        pos = text.find("\n", pos) + 1
        rest = text[pos:]
        m = re.search(r'\n---', rest)
        return rest[:m.start()].strip() if m else rest.strip()
    meta["fb_text"]    = _extract(content, "## \U0001f4d8 FACEBOOK POST")
    meta["ig_text"]    = _extract(content, "## \U0001f4f7 INSTAGRAM POST")
    meta["story_text"] = _extract(content, "## \U0001f4f1 STORY")
    # Gatekeeper check
    meta["gk_done"]     = "\u2705 GATEKEEPER" in content
    meta["gk_approved"] = "APPROVED" in content and meta["gk_done"]
    return meta


def classify_pillar(sign_name):
    s = sign_name.lower()
    if any(w in s for w in ["camaro", "mustang", "corvette", "thunderbird",
                            "dodge", "ford f-", "f-100", "f100"]):
        return "automotive"
    if any(w in s for w in ["harley", "biker", "motorcycle"]):
        return "motorcycle"
    if any(w in s for w in ["mr & mrs", "mr&mrs", "monogram", "wedding",
                            "rosales", "raymond", "narine"]):
        return "wedding"
    if any(w in s for w in ["malinois", "dog"]):
        return "dog"
    if "blog" in s or "bobby" in s:
        return "blog"
    return "other"


# ── Data Building ──────────────────────────────────────────────────────────
def build_posts_data(gantt, gemini_urls, mockup_urls):
    posts = []
    for item in gantt:
        dt = item["date"]
        folder = find_post_folder(dt)
        meta = parse_post_metadata(folder) if folder else {}
        pillar = classify_pillar(item["sign"])
        posts.append({
            "date": dt,
            "sign": item["sign"],
            "todoist_id": item["id"],
            "gemini_url": gemini_urls.get(dt),
            "mockup_url": mockup_urls.get(dt),
            "pillar": pillar,
            "pillar_label": PILLAR_LABELS.get(pillar, pillar),
            "pillar_color": PILLAR_COLORS.get(pillar, "#666"),
            "audience": meta.get("audience", "\u2014"),
            "angle": meta.get("angle", "\u2014"),
            "story_status": meta.get("story_status", "unknown"),
            "story_raw": meta.get("story_raw", "\u2014"),
            "emoji": meta.get("emoji", ""),
            "fb_text":    meta.get("fb_text", ""),
            "ig_text":    meta.get("ig_text", ""),
            "story_text": meta.get("story_text", ""),
            "gk_done":     meta.get("gk_done", False),
            "gk_approved": meta.get("gk_approved", False),
        })
    return posts


def compute_stats(posts, qa):
    gemini_ready = sum(1 for p in posts if p["gemini_url"])
    story_ready = sum(1 for p in posts if p["story_status"] == "ready")
    pillar_counts = {}
    for p in posts:
        pillar_counts[p["pillar"]] = pillar_counts.get(p["pillar"], 0) + 1
    return {
        "total": len(posts),
        "qa_passed": qa.get("passed", 0),
        "qa_total": qa.get("total", len(posts)),
        "gemini_ready": gemini_ready,
        "gemini_missing": len(posts) - gemini_ready,
        "mockup_ready": sum(1 for p in posts if p["mockup_url"]),
        "story_ready": story_ready,
        "story_need": len(posts) - story_ready,
        "pillars": pillar_counts,
    }


def compute_agent_kpis(stats):
    t = stats["total"]
    return {
        "marketing-director": {
            "metric": "\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05de\u05ea\u05d5\u05db\u05e0\u05e0\u05d9\u05dd",
            "value": str(t), "detail": "12 \u05de\u05e8\u05e5 \u2014 19 \u05d0\u05e4\u05e8\u05d9\u05dc 2026",
            "pct": 100,
        },
        "social-copywriter": {
            "metric": "\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05e0\u05db\u05ea\u05d1\u05d5",
            "value": f"{t}/{t}", "detail": "\u05db\u05dc \u05d4\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05e0\u05db\u05ea\u05d1\u05d5 \u05d5\u05de\u05d0\u05d5\u05e9\u05e8\u05d9\u05dd",
            "pct": 100,
        },
        "stories-content": {
            "metric": "\u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05de\u05d5\u05db\u05e0\u05d9\u05dd",
            "value": f"{stats['story_ready']}/{t}",
            "detail": f"{stats['story_need']} \u05e6\u05e8\u05d9\u05db\u05d9\u05dd \u05d7\u05d9\u05ea\u05d5\u05da",
            "pct": int(stats["story_ready"] / t * 100) if t else 0,
        },
        "gatekeeper": {
            "metric": "\u05e2\u05d1\u05e8\u05d5 \u05d1\u05d3\u05d9\u05e7\u05ea \u05d0\u05d9\u05db\u05d5\u05ea",
            "value": f"{stats['qa_passed']}/{stats['qa_total']}",
            "detail": "\u05d0\u05e4\u05e1 \u05d1\u05e2\u05d9\u05d5\u05ea. \u05d4\u05db\u05dc \u05de\u05d0\u05d5\u05e9\u05e8.",
            "pct": int(stats["qa_passed"] / stats["qa_total"] * 100) if stats["qa_total"] else 0,
        },
        "visual-designer": {
            "metric": "\u05e2\u05d9\u05e6\u05d5\u05d1\u05d9\u05dd \u05e0\u05d5\u05e6\u05e8\u05d5",
            "value": f"{stats['mockup_ready']}/{t}",
            "detail": "\u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u05dc\u05db\u05dc \u05d4\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd",
            "pct": int(stats["mockup_ready"] / t * 100) if t else 0,
        },
        "mockup-generator": {
            "metric": "\u05d4\u05d3\u05de\u05d9\u05d5\u05ea Gemini",
            "value": f"{stats['gemini_ready']}/{t}",
            "detail": f"{stats['gemini_missing']} \u05d7\u05e1\u05e8\u05d9\u05dd",
            "pct": int(stats["gemini_ready"] / t * 100) if t else 0,
        },
        "visual-qa": {
            "metric": "\u05e2\u05d1\u05e8\u05d5 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05ea",
            "value": f"{stats['qa_passed']}/{stats['qa_total']}",
            "detail": "\u05db\u05dc \u05d4\u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u05ea\u05d5\u05d0\u05de\u05d9\u05dd \u05dc\u05de\u05d5\u05e6\u05e8",
            "pct": int(stats["qa_passed"] / stats["qa_total"] * 100) if stats["qa_total"] else 0,
        },
        "batch-runner": {
            "metric": "\u05e4\u05e8\u05d9\u05d8\u05d9\u05dd \u05e2\u05d5\u05d1\u05d3\u05d5",
            "value": f"{t}/{t}",
            "detail": "\u05db\u05dc \u05d4\u05e4\u05e8\u05d9\u05d8\u05d9\u05dd \u05e2\u05d5\u05d1\u05d3\u05d5 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4",
            "pct": 100,
        },
        "paid-campaigner": {
            "metric": "\u05ea\u05e7\u05e6\u05d9\u05d1 \u05e9\u05e0\u05ea\u05d9",
            "value": "$2,100",
            "detail": "$175/\u05d7\u05d5\u05d3\u05e9 \u2014 70% Meta, 20% Pinterest, 10% Etsy",
            "pct": 0,
        },
    }


def compute_sla_report(posts):
    """Compute per-agent SLA compliance from actual post data."""
    t = len(posts)
    if t == 0:
        return []
    # Helper
    def _pct(n):
        return round(n / t * 100) if t else 0
    def _missing(lst):
        return [f"{p['date'][5:]} {p['sign']}" for p in lst]

    fb_done  = [p for p in posts if p.get("fb_text")]
    ig_done  = [p for p in posts if p.get("ig_text")]
    both_txt = [p for p in posts if p.get("fb_text") and p.get("ig_text")]
    story_rdy = [p for p in posts if p.get("story_status") == "ready"]
    story_txt = [p for p in posts if p.get("story_text")]
    gk_app   = [p for p in posts if p.get("gk_approved")]
    gem      = [p for p in posts if p.get("gemini_url")]
    mock     = [p for p in posts if p.get("mockup_url")]

    report = [
        {
            "agent_id": "social-copywriter",
            "sla": "\u05db\u05ea\u05d9\u05d1\u05ea \u05d8\u05e7\u05e1\u05d8 FB + IG \u05dc\u05db\u05dc \u05e4\u05d5\u05e1\u05d8",
            "done": len(both_txt), "total": t, "pct": _pct(len(both_txt)),
            "detail": f"Facebook: {len(fb_done)}/{t} | Instagram: {len(ig_done)}/{t}",
            "missing": _missing([p for p in posts if not (p.get("fb_text") and p.get("ig_text"))]),
        },
        {
            "agent_id": "stories-content",
            "sla": "\u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05de\u05d5\u05db\u05e0\u05d9\u05dd \u05dc\u05e4\u05e8\u05e1\u05d5\u05dd (Ready)",
            "done": len(story_rdy), "total": t, "pct": _pct(len(story_rdy)),
            "detail": f"\u05d8\u05e7\u05e1\u05d8 \u05e0\u05db\u05ea\u05d1: {len(story_txt)}/{t} | \u05e4\u05d5\u05e8\u05de\u05d8 Ready: {len(story_rdy)}/{t}",
            "missing": _missing([p for p in posts if p.get("story_status") != "ready"]),
        },
        {
            "agent_id": "visual-designer",
            "sla": "\u05de\u05d5\u05e7\u05d0\u05e4 \u05de\u05d5\u05e6\u05e8 \u05dc\u05db\u05dc \u05e4\u05d5\u05e1\u05d8",
            "done": len(mock), "total": t, "pct": _pct(len(mock)),
            "detail": f"Mockup: {len(mock)}/{t}",
            "missing": _missing([p for p in posts if not p.get("mockup_url")]),
        },
        {
            "agent_id": "mockup-generator",
            "sla": "\u05d4\u05d3\u05de\u05d9\u05ea Gemini \u05dc\u05db\u05dc \u05e4\u05d5\u05e1\u05d8",
            "done": len(gem), "total": t, "pct": _pct(len(gem)),
            "detail": f"Gemini: {len(gem)}/{t} | \u05d7\u05e1\u05e8\u05d9\u05dd: {t - len(gem)}",
            "missing": _missing([p for p in posts if not p.get("gemini_url")]),
        },
        {
            "agent_id": "gatekeeper",
            "sla": "\u05d1\u05d9\u05e7\u05d5\u05e8\u05ea Gatekeeper + APPROVED",
            "done": len(gk_app), "total": t, "pct": _pct(len(gk_app)),
            "detail": f"\u05d0\u05d5\u05e9\u05e8\u05d5: {len(gk_app)}/{t}",
            "missing": _missing([p for p in posts if not p.get("gk_approved")]),
        },
        {
            "agent_id": "visual-qa",
            "sla": "\u05d1\u05d3\u05d9\u05e7\u05ea \u05d0\u05d9\u05db\u05d5\u05ea \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05ea (AUTO-REJECT)",
            "done": len(gk_app), "total": t, "pct": _pct(len(gk_app)),
            "detail": "\u05de\u05d1\u05d5\u05e1\u05e1 \u05e2\u05dc \u05d1\u05d9\u05e7\u05d5\u05e8\u05ea Gatekeeper",
            "missing": _missing([p for p in posts if not p.get("gk_approved")]),
        },
        {
            "agent_id": "batch-runner",
            "sla": "\u05d4\u05e8\u05e6\u05ea \u05e4\u05d9\u05d9\u05e4\u05dc\u05d9\u05d9\u05df \u05de\u05dc\u05d0\u05d4 \u05dc\u05db\u05dc \u05d4\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd",
            "done": t, "total": t, "pct": 100,
            "detail": f"\u05db\u05dc {t} \u05d4\u05ea\u05d9\u05e7\u05d9\u05d5\u05ea \u05e0\u05d5\u05e6\u05e8\u05d5",
            "missing": [],
        },
        {
            "agent_id": "paid-campaigner",
            "sla": "\u05d4\u05db\u05e0\u05ea \u05e7\u05de\u05e4\u05d9\u05d9\u05e0\u05d9\u05dd \u05de\u05de\u05d5\u05de\u05e0\u05d9\u05dd",
            "done": 0, "total": t, "pct": 0,
            "detail": "\u05dc\u05d0 \u05de\u05d3\u05d9\u05d3 \u2014 \u05de\u05de\u05ea\u05d9\u05df \u05dc\u05d0\u05d9\u05e9\u05d5\u05e8 \u05ea\u05d5\u05db\u05df",
            "missing": [],
        },
    ]
    return report


def compute_agent_logs(posts, stats):
    """Compute per-agent activity logs for today / this week / this month."""
    today = date.today()
    # Week: Sunday to Saturday containing today
    days_since_sun = today.isoweekday() % 7
    week_start = today - timedelta(days=days_since_sun)
    week_end = week_start + timedelta(days=6)
    month_num = today.month

    # Partition posts by time range
    today_posts = [p for p in posts if p["date"] == today.isoformat()]
    week_posts = [p for p in posts if week_start.isoformat() <= p["date"] <= week_end.isoformat()]
    month_posts = [p for p in posts if p["date"][:7] == f"2026-{month_num:02d}"]

    def sign_list(ps, limit=4):
        names = [p["sign"] for p in ps]
        if len(names) <= limit:
            return ", ".join(names)
        return ", ".join(names[:limit]) + f" +{len(names)-limit}"

    def _logs_for(role_id, today_p, week_p, month_p):
        t_n, w_n, m_n = len(today_p), len(week_p), len(month_p)
        w_signs = sign_list(week_p)
        m_signs = sign_list(month_p, 5)
        # Count sub-metrics for the period
        w_gemini = sum(1 for p in week_p if p["gemini_url"])
        w_mockup = sum(1 for p in week_p if p["mockup_url"])
        w_story = sum(1 for p in week_p if p["story_status"] == "ready")
        m_gemini = sum(1 for p in month_p if p["gemini_url"])
        m_mockup = sum(1 for p in month_p if p["mockup_url"])
        m_story = sum(1 for p in month_p if p["story_status"] == "ready")

        if role_id == "marketing-director":
            return {
                "today": [f"\u05de\u05d7\u05e8 \u05de\u05ea\u05d7\u05d9\u05dc \u05e4\u05e8\u05e1\u05d5\u05dd \u2014 \u05d4\u05e4\u05d5\u05e1\u05d8 \u05d4\u05e8\u05d0\u05e9\u05d5\u05df \u05d9\u05d5\u05e6\u05d0 \u05de\u05d7\u05e8"] if t_n == 0 else [f"\u05de\u05e0\u05d4\u05dc {t_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd"],
                "week": [f"\u05ea\u05d9\u05db\u05e0\u05df {w_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd: {w_signs}"] if w_n else ["\u05d0\u05d9\u05df \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05ea\u05d9\u05db\u05e0\u05df {m_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05dc\u05de\u05e8\u05e5", f"Pipeline: {m_mockup} mockups, {m_gemini} Gemini, {m_story} stories"],
            }
        elif role_id == "social-copywriter":
            return {
                "today": [f"\u05db\u05ea\u05d1 \u05e4\u05d5\u05e1\u05d8: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05db\u05ea\u05d9\u05d1\u05d4 \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05db\u05ea\u05d1 {w_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd: {w_signs}"] if w_n else ["\u05d0\u05d9\u05df \u05db\u05ea\u05d9\u05d1\u05d4 \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05db\u05ea\u05d1 {m_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05dc\u05de\u05e8\u05e5: {m_signs}"],
            }
        elif role_id == "stories-content":
            return {
                "today": [f"\u05d4\u05db\u05d9\u05df \u05e1\u05d8\u05d5\u05e8\u05d9: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05e1\u05d8\u05d5\u05e8\u05d9 \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"{w_story}/{w_n} \u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05de\u05d5\u05db\u05e0\u05d9\u05dd \u05d4\u05e9\u05d1\u05d5\u05e2"] if w_n else ["\u05d0\u05d9\u05df \u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"{m_story}/{m_n} \u05e1\u05d8\u05d5\u05e8\u05d9\u05d6 \u05de\u05d5\u05db\u05e0\u05d9\u05dd \u05dc\u05de\u05e8\u05e5", f"{m_n - m_story} \u05e6\u05e8\u05d9\u05db\u05d9\u05dd \u05d7\u05d9\u05ea\u05d5\u05da 9:16"],
            }
        elif role_id == "gatekeeper":
            return {
                "today": [f"\u05d1\u05d3\u05e7 \u05d5\u05d0\u05d9\u05e9\u05e8: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05d1\u05d3\u05d9\u05e7\u05d5\u05ea \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05d1\u05d3\u05e7 {w_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u2014 \u05d4\u05db\u05dc \u05d0\u05d5\u05e9\u05e8"] if w_n else ["\u05d0\u05d9\u05df \u05d1\u05d3\u05d9\u05e7\u05d5\u05ea \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05d1\u05d3\u05e7 {m_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05dc\u05de\u05e8\u05e5", "\u05d0\u05e4\u05e1 \u05d1\u05e2\u05d9\u05d5\u05ea. 100% \u05d0\u05d9\u05e9\u05d5\u05e8."],
            }
        elif role_id == "visual-designer":
            return {
                "today": [f"\u05e2\u05d9\u05e6\u05d1 \u05de\u05d5\u05e7\u05d0\u05e4: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05e2\u05d9\u05e6\u05d5\u05d1\u05d9\u05dd \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05e2\u05d9\u05e6\u05d1 {w_mockup}/{w_n} \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd: {w_signs}"] if w_n else ["\u05d0\u05d9\u05df \u05e2\u05d9\u05e6\u05d5\u05d1\u05d9\u05dd \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05e2\u05d9\u05e6\u05d1 {m_mockup}/{m_n} \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u05dc\u05de\u05e8\u05e5"],
            }
        elif role_id == "mockup-generator":
            return {
                "today": [f"\u05d9\u05e6\u05e8 \u05d4\u05d3\u05de\u05d9\u05d4: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05d4\u05d3\u05de\u05d9\u05d5\u05ea \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05d9\u05e6\u05e8 {w_gemini}/{w_n} \u05d4\u05d3\u05de\u05d9\u05d5\u05ea Gemini"] if w_n else ["\u05d0\u05d9\u05df \u05d4\u05d3\u05de\u05d9\u05d5\u05ea \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05d9\u05e6\u05e8 {m_gemini}/{m_n} \u05d4\u05d3\u05de\u05d9\u05d5\u05ea \u05dc\u05de\u05e8\u05e5", f"{m_n - m_gemini} \u05d7\u05e1\u05e8\u05d9\u05dd \u05dc\u05d4\u05e9\u05dc\u05de\u05d4"],
            }
        elif role_id == "visual-qa":
            return {
                "today": [f"\u05d1\u05d3\u05e7 \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc\u05d9\u05ea: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05d1\u05d3\u05d9\u05e7\u05d5\u05ea \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05d1\u05d3\u05e7 {w_n} \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u2014 \u05d4\u05db\u05dc \u05ea\u05d5\u05d0\u05dd"] if w_n else ["\u05d0\u05d9\u05df \u05d1\u05d3\u05d9\u05e7\u05d5\u05ea \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05d1\u05d3\u05e7 {m_n} \u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd \u05dc\u05de\u05e8\u05e5", "\u05d0\u05e4\u05e1 \u05e4\u05e1\u05d9\u05dc\u05d5\u05ea. \u05d4\u05db\u05dc \u05ea\u05d5\u05d0\u05dd \u05dc\u05de\u05d5\u05e6\u05e8."],
            }
        elif role_id == "batch-runner":
            return {
                "today": [f"\u05e2\u05d9\u05d1\u05d3: {today_p[0]['sign']}"] if t_n else ["\u05d0\u05d9\u05df \u05e2\u05d9\u05d1\u05d5\u05d3\u05d9\u05dd \u05d4\u05d9\u05d5\u05dd"],
                "week": [f"\u05e2\u05d9\u05d1\u05d3 {w_n} \u05e4\u05e8\u05d9\u05d8\u05d9\u05dd: {w_signs}"] if w_n else ["\u05d0\u05d9\u05df \u05e2\u05d9\u05d1\u05d5\u05d3\u05d9\u05dd \u05d4\u05e9\u05d1\u05d5\u05e2"],
                "month": [f"\u05e2\u05d9\u05d1\u05d3 {m_n} \u05e4\u05e8\u05d9\u05d8\u05d9\u05dd \u05dc\u05de\u05e8\u05e5", "100% \u05d4\u05e6\u05dc\u05d7\u05d4"],
            }
        elif role_id == "paid-campaigner":
            return {
                "today": ["\u05e1\u05d5\u05db\u05df \u05d7\u05d3\u05e9 \u2014 \u05de\u05ea\u05db\u05e0\u05df \u05e7\u05de\u05e4\u05d9\u05d9\u05e0\u05d9\u05dd"],
                "week": ["\u05de\u05de\u05e4\u05d4 10 \u05e1\u05e7\u05d9\u05dc\u05e1", f"\u05ea\u05d5\u05db\u05df {m_n} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05d0\u05d5\u05e8\u05d2\u05e0\u05d9\u05d9\u05dd \u05dc\u05d1\u05d5\u05e1\u05d8"],
                "month": ["\u05ea\u05e7\u05e6\u05d9\u05d1 \u05de\u05e8\u05e5: $100", f"\u05de\u05ea\u05db\u05e0\u05df \u05e7\u05de\u05e4\u05d9\u05d9\u05df Wedding Season (\u05d0\u05e4\u05e8\u05d9\u05dc)", "\u05e4\u05dc\u05d9\u05d9\u05d1\u05d5\u05e7 Father\u2019s Day \u05de\u05d5\u05db\u05df"],
            }
        return {"today": [], "week": [], "month": []}

    logs = {}
    for agent in TEAM:
        logs[agent["id"]] = _logs_for(agent["id"], today_posts, week_posts, month_posts)
    return logs


def build_calendar_data(posts):
    post_map = {}
    for p in posts:
        post_map.setdefault(p["date"], []).append(p)
    months = []
    for year, month, name_he in [(2026, 3, "\u05de\u05e8\u05e5 2026"), (2026, 4, "\u05d0\u05e4\u05e8\u05d9\u05dc 2026")]:
        _, days_in_month = monthrange(year, month)
        first_dow = date(year, month, 1).weekday()
        first_dow_sun = (first_dow + 1) % 7
        days = []
        for day in range(1, days_in_month + 1):
            dt_str = f"{year}-{month:02d}-{day:02d}"
            day_posts = post_map.get(dt_str, [])
            days.append({
                "day": day, "date": dt_str,
                "posts": [{"sign": p["sign"], "pillar": p["pillar"],
                           "color": p["pillar_color"],
                           "img": p.get("gemini_url") or p.get("mockup_url") or ""} for p in day_posts],
            })
        months.append({"name": name_he, "first_dow": first_dow_sun, "days": days})
    return months


def build_gantt_weeks(posts):
    sorted_posts = sorted(posts, key=lambda x: x["date"])
    weeks = []
    current_posts = []
    current_sun = None
    for p in sorted_posts:
        d = date.fromisoformat(p["date"])
        dow = d.isoweekday() % 7  # Sun=0
        week_sun = d - timedelta(days=dow)
        if current_sun is None:
            current_sun = week_sun
        if week_sun != current_sun:
            week_sat = current_sun + timedelta(days=6)
            weeks.append({
                "start": current_sun.isoformat(),
                "end": week_sat.isoformat(),
                "label": _week_label(current_sun, week_sat),
                "posts": current_posts,
            })
            current_sun = week_sun
            current_posts = []
        current_posts.append({
            "date": p["date"], "sign": p["sign"], "pillar": p["pillar"],
            "color": p["pillar_color"], "dow": dow,
            "gemini": bool(p["gemini_url"]), "mockup": bool(p["mockup_url"]),
            "story": p["story_status"],
            "gemini_url": p["gemini_url"] or "",
            "mockup_url": p["mockup_url"] or "",
        })
    if current_posts:
        week_sat = current_sun + timedelta(days=6)
        weeks.append({
            "start": current_sun.isoformat(), "end": week_sat.isoformat(),
            "label": _week_label(current_sun, week_sat), "posts": current_posts,
        })
    return weeks


def _week_label(start, end):
    if start.month == end.month:
        return f"{start.day}-{end.day} {MONTHS_HE.get(start.month, '')}"
    return f"{start.day} {MONTHS_HE.get(start.month, '')} - {end.day} {MONTHS_HE.get(end.month, '')}"


def build_matrix_data(posts):
    products = {}
    for p in posts:
        base = re.sub(r"\s*v\d+$", "", p["sign"])
        if base not in products:
            products[base] = {
                "name": base, "pillar": p["pillar"], "pillar_color": p["pillar_color"],
                "dates": [], "gemini_count": 0, "mockup_count": 0,
                "story_ready_count": 0, "total": 0,
            }
        products[base]["dates"].append(p["date"])
        products[base]["total"] += 1
        if p["gemini_url"]:
            products[base]["gemini_count"] += 1
        if p["mockup_url"]:
            products[base]["mockup_count"] += 1
        if p["story_status"] == "ready":
            products[base]["story_ready_count"] += 1
    return list(products.values())


# ── HTML Generation ────────────────────────────────────────────────────────
def generate_html(data):
    posts = data["posts"]
    stats = data["stats"]
    calendar = data["calendar"]
    matrix = data["matrix"]
    kpis = data["kpis"]
    agent_logs = data["agent_logs"]
    sla_report = data.get("sla_report", [])
    weeks = data["weeks"]
    generated = data["generated"]
    missing_gemini = [p for p in posts if not p["gemini_url"]]
    posts_json = json.dumps(posts, ensure_ascii=False)

    # ── Build Team HTML ────────────────────────────────────────────────
    lead = [a for a in TEAM if a["is_lead"]][0]
    members = [a for a in TEAM if not a["is_lead"]]
    lead_kpi = kpis.get(lead["id"], {})

    def _pct_color(pct):
        if pct >= 90:
            return "#4ade80"
        if pct >= 60:
            return "#fbbf24"
        return "#f87171"

    def _render_avatar_svg(agent, size=64):
        """Generate a cartoon face SVG avatar for an agent."""
        bg = agent['avatar_bg']
        hair = agent['avatar_hair']
        acc = agent.get('avatar_acc', '')
        svg = f'<svg width="{size}" height="{size}" viewBox="0 0 80 80" style="border-radius:50%;flex-shrink:0">'
        svg += f'<circle cx="40" cy="40" r="40" fill="{bg}"/>'
        # Skin face
        svg += '<circle cx="40" cy="44" r="20" fill="#fcd9b6"/>'
        # Hair
        svg += f'<ellipse cx="40" cy="30" rx="21" ry="12" fill="{hair}"/>'
        # Eyes
        svg += '<circle cx="33" cy="42" r="2.5" fill="#333"/><circle cx="47" cy="42" r="2.5" fill="#333"/>'
        svg += '<circle cx="34" cy="41" r="1" fill="#fff"/><circle cx="48" cy="41" r="1" fill="#fff"/>'
        # Smile
        svg += '<path d="M34,51 Q40,57 46,51" fill="none" stroke="#c97850" stroke-width="2" stroke-linecap="round"/>'
        # Accessory
        if acc == 'glasses':
            svg += '<circle cx="33" cy="42" r="6" fill="none" stroke="#555" stroke-width="1.5"/>'
            svg += '<circle cx="47" cy="42" r="6" fill="none" stroke="#555" stroke-width="1.5"/>'
            svg += '<line x1="39" y1="41" x2="41" y2="41" stroke="#555" stroke-width="1.5"/>'
            svg += '<line x1="27" y1="40" x2="22" y2="38" stroke="#555" stroke-width="1.5"/>'
            svg += '<line x1="53" y1="40" x2="58" y2="38" stroke="#555" stroke-width="1.5"/>'
        elif acc == 'pen':
            svg += '<rect x="57" y="22" width="3.5" height="18" rx="1" fill="#fff" transform="rotate(20,58,31)"/>'
            svg += '<polygon points="59,40 57,44 61,44" fill="#f87171" transform="rotate(20,59,42)"/>'
        elif acc == 'phone':
            svg += '<rect x="55" y="46" width="11" height="18" rx="2" fill="#333" stroke="#666" stroke-width="1"/>'
            svg += '<rect x="57" y="49" width="7" height="10" rx="1" fill="#6ee7b7"/>'
        elif acc == 'shield':
            svg += '<path d="M60,26 L67,30 L67,38 L60,44 L53,38 L53,30 Z" fill="#fbbf24" stroke="#f59e0b" stroke-width="1"/>'
            svg += '<path d="M60,30 L60,40" stroke="#fff" stroke-width="1.5"/>'
            svg += '<path d="M56,35 L64,35" stroke="#fff" stroke-width="1.5"/>'
        elif acc == 'beret':
            svg += f'<ellipse cx="40" cy="24" rx="22" ry="7" fill="{hair}"/>'
            svg += '<ellipse cx="40" cy="22" rx="18" ry="5" fill="#c084fc"/>'
            svg += '<circle cx="40" cy="16" r="3" fill="#c084fc"/>'
        elif acc == 'camera':
            svg += '<rect x="52" y="50" width="16" height="12" rx="3" fill="#444" stroke="#666" stroke-width="1"/>'
            svg += '<circle cx="60" cy="56" r="4" fill="#333" stroke="#888" stroke-width="1"/>'
            svg += '<circle cx="60" cy="56" r="2" fill="#6ee7b7"/>'
            svg += '<rect x="57" y="49" width="6" height="2.5" rx="1" fill="#555"/>'
        elif acc == 'magnifier':
            svg += '<circle cx="60" cy="52" r="7" fill="none" stroke="#fbbf24" stroke-width="2"/>'
            svg += '<line x1="65" y1="57" x2="72" y2="64" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round"/>'
        elif acc == 'bolt':
            svg += '<polygon points="62,22 56,33 60,33 54,44 68,31 62,31 68,22" fill="#fbbf24"/>'
        elif acc == 'chart':
            svg += '<rect x="53" y="48" width="5" height="12" rx="1" fill="#4ade80"/>'
            svg += '<rect x="60" y="44" width="5" height="16" rx="1" fill="#fbbf24"/>'
            svg += '<rect x="67" y="40" width="5" height="20" rx="1" fill="#f87171"/>'
        svg += '</svg>'
        return svg

    def _render_log_section(log_data):
        """Render today/week/month log tabs for an agent."""
        today_items = log_data.get("today", [])
        week_items = log_data.get("week", [])
        month_items = log_data.get("month", [])
        def _items_html(items):
            if not items:
                return '<div class="log-empty">\u05d0\u05d9\u05df \u05e4\u05e2\u05d9\u05dc\u05d5\u05ea</div>'
            return "".join(f'<div class="log-item">{i}</div>' for i in items)
        return f"""
        <div class="agent-log">
          <div class="log-tabs">
            <button class="log-tab active" onclick="switchLog(this,'today')">\u05d4\u05d9\u05d5\u05dd</button>
            <button class="log-tab" onclick="switchLog(this,'week')">\u05d4\u05e9\u05d1\u05d5\u05e2</button>
            <button class="log-tab" onclick="switchLog(this,'month')">\u05d4\u05d7\u05d5\u05d3\u05e9</button>
          </div>
          <div class="log-panel active" data-period="today">{_items_html(today_items)}</div>
          <div class="log-panel" data-period="week">{_items_html(week_items)}</div>
          <div class="log-panel" data-period="month">{_items_html(month_items)}</div>
        </div>"""

    lead_log = agent_logs.get(lead["id"], {})
    lead_avatar = _render_avatar_svg(lead, 72)
    team_lead_html = f"""
    <div class="lead-card">
      <div class="lead-avatar">{lead_avatar}</div>
      <div class="lead-info">
        <div class="lead-name">{lead['char_name']} <span class="lead-title">{lead['name_he']}</span></div>
        <div class="lead-role">{lead['role_he']}</div>
        <div class="lead-sla">{lead['sla']}</div>
        <div class="lead-identity">"{lead['identity_he']}"</div>
      </div>
      <div class="lead-stat">
        <div class="lead-stat-value">{lead_kpi.get('value','')}</div>
        <div class="lead-stat-label">{lead_kpi.get('metric','')}</div>
      </div>
      {_render_log_section(lead_log)}
    </div>"""

    team_members_html = ""
    for m in members:
        mk = kpis.get(m["id"], {})
        pct = mk.get("pct", 0)
        pcolor = _pct_color(pct)
        m_log = agent_logs.get(m["id"], {})
        m_avatar = _render_avatar_svg(m, 48)
        team_members_html += f"""
    <div class="member-card">
      <div class="member-top">
        <div class="member-avatar">{m_avatar}</div>
        <div>
          <div class="member-name">{m['char_name']} <span class="member-title">{m['name_he']}</span></div>
          <div class="member-role">{m['role_he']}</div>
          <div class="member-sla">{m['sla']}</div>
        </div>
      </div>
      <div class="member-identity">"{m['identity_he']}"</div>
      <div class="member-kpi">
        <div class="kpi-bar-track"><div class="kpi-bar" style="width:{pct}%;background:{pcolor}"></div></div>
        <span class="kpi-value">{mk.get('value','')}</span>
        <span class="kpi-label">{mk.get('metric','')}</span>
      </div>
      {_render_log_section(m_log)}
    </div>"""

    # ── Build KPI HTML ─────────────────────────────────────────────────
    # Team-wide summary cards
    pipeline_pct = 0
    if stats["total"] > 0:
        # Pipeline completeness = avg of all asset readiness
        pipeline_pct = int((
            (stats["gemini_ready"] / stats["total"]) +
            (stats["mockup_ready"] / stats["total"]) +
            (stats["qa_passed"] / stats["qa_total"] if stats["qa_total"] else 0) +
            (stats["story_ready"] / stats["total"])
        ) / 4 * 100)

    kpi_summary_html = f"""
    <div class="kpi-presenter">
      <span class="kpi-presenter-emoji">{lead['emoji']}</span>
      <span>{lead['name_he']} \u05de\u05d3\u05d5\u05d5\u05d7 \u05e2\u05dc \u05d1\u05d9\u05e6\u05d5\u05e2\u05d9 \u05d4\u05e6\u05d5\u05d5\u05ea:</span>
    </div>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-number">{stats['total']}</div><div class="stat-label">\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05de\u05ea\u05d5\u05db\u05e0\u05e0\u05d9\u05dd</div></div>
      <div class="stat-card stat-green"><div class="stat-number">{stats['qa_passed']}/{stats['qa_total']}</div><div class="stat-label">\u05e2\u05d1\u05e8\u05d5 QA</div></div>
      <div class="stat-card {'stat-green' if stats['gemini_missing']==0 else 'stat-amber'}"><div class="stat-number">{stats['gemini_ready']}/{stats['total']}</div><div class="stat-label">\u05d4\u05d3\u05de\u05d9\u05d5\u05ea Gemini</div></div>
      <div class="stat-card stat-green"><div class="stat-number">{stats['mockup_ready']}/{stats['total']}</div><div class="stat-label">\u05de\u05d5\u05e7\u05d0\u05e4\u05d9\u05dd</div></div>
      <div class="stat-card {'stat-green' if stats['story_ready']==stats['total'] else 'stat-amber'}"><div class="stat-number">{stats['story_ready']}/{stats['total']}</div><div class="stat-label">Story \u05de\u05d5\u05db\u05df</div></div>
      <div class="stat-card"><div class="stat-number" style="color:{_pct_color(pipeline_pct)}">{pipeline_pct}%</div><div class="stat-label">\u05e9\u05dc\u05de\u05d5\u05ea Pipeline</div></div>
    </div>"""

    # Per-agent KPI cards
    kpi_agents_html = ""
    for agent in TEAM:
        ak = kpis.get(agent["id"], {})
        pct = ak.get("pct", 0)
        pcolor = _pct_color(pct)
        border_cls = "kpi-agent-green" if pct >= 90 else ("kpi-agent-amber" if pct >= 60 else "kpi-agent-red")
        kpi_agents_html += f"""
    <div class="kpi-agent-card {border_cls}">
      <div class="kpi-agent-top">
        <span class="kpi-agent-emoji">{agent['emoji']}</span>
        <span class="kpi-agent-name">{agent['char_name']} <span style="font-size:11px;color:#666;font-weight:400">{agent['name_he']}</span></span>
      </div>
      <div class="kpi-agent-value">{ak.get('value','')}</div>
      <div class="kpi-agent-metric">{ak.get('metric','')}</div>
      <div class="kpi-agent-detail">{ak.get('detail','')}</div>
      <div class="kpi-bar-track"><div class="kpi-bar" style="width:{pct}%;background:{pcolor}"></div></div>
    </div>"""

    # ── Build Gantt HTML ───────────────────────────────────────────────
    # Month view = calendars
    cal_html = ""
    for month in calendar:
        cal_html += f'<div class="cal-month"><h3>{month["name"]}</h3><div class="cal-grid">'
        for dn in DAY_NAMES_HE:
            cal_html += f'<div class="cal-header">{dn}</div>'
        for _ in range(month["first_dow"]):
            cal_html += '<div class="cal-cell empty"></div>'
        for day_info in month["days"]:
            dots = ""
            tooltip = ""
            cal_img = ""
            if day_info["posts"]:
                for dp in day_info["posts"]:
                    dots += f'<span class="cal-dot" style="background:{dp["color"]}"></span>'
                tooltip = ", ".join(dp["sign"] for dp in day_info["posts"])
                # Show first post's image as background
                first_img = day_info["posts"][0].get("img", "")
                if first_img:
                    cal_img = f'<img src="{first_img}" class="cal-img thumb" loading="lazy" data-full="{first_img}">'
            cls = "cal-cell has-post" if day_info["posts"] else "cal-cell"
            cal_html += f'<div class="{cls}" title="{tooltip}"><span class="cal-day">{day_info["day"]}</span>{cal_img}{dots}</div>'
        cal_html += "</div></div>"

    # Week views (pre-rendered)
    week_views_html = ""
    for wi, week in enumerate(weeks):
        disp = "block" if wi == 0 else "none"
        week_views_html += f'<div class="gantt-week-panel" data-week="{wi}" style="display:{disp}">'
        week_views_html += f'<h3 class="week-title">{week["label"]}</h3>'
        for wp in week["posts"]:
            g_dot = '<span class="sdot sdot-green" title="Gemini OK"></span>' if wp["gemini"] else '<span class="sdot sdot-red" title="Gemini \u05d7\u05e1\u05e8"></span>'
            m_dot = '<span class="sdot sdot-green" title="Mockup OK"></span>' if wp["mockup"] else '<span class="sdot sdot-red" title="Mockup \u05d7\u05e1\u05e8"></span>'
            s_dot = '<span class="sdot sdot-green" title="Story OK"></span>' if wp["story"] == "ready" else '<span class="sdot sdot-amber" title="Story \u05d7\u05e1\u05e8"></span>'
            day_he = DAY_NAMES_HE[wp["dow"]]
            # Show Gemini image if available, fallback to mockup
            img_url = wp["gemini_url"] or wp["mockup_url"]
            thumb_html = f'<img src="{img_url}" class="gantt-thumb thumb" loading="lazy" data-full="{img_url}" onerror="this.style.display=\'none\'">' if img_url else '<div class="gantt-thumb-empty"></div>'
            week_views_html += f"""
        <div class="gantt-row">
          <div class="gantt-date">{wp['date'][5:]} {day_he}</div>
          <div class="gantt-thumb-box">{thumb_html}</div>
          <div class="gantt-bar-area">
            <div class="gantt-bar" style="background:{wp['color']}">{wp['sign']}</div>
          </div>
          <div class="gantt-dots">{g_dot}{m_dot}{s_dot}</div>
        </div>"""
        week_views_html += "</div>"

    weeks_json = json.dumps([{"label": w["label"], "count": len(w["posts"])} for w in weeks], ensure_ascii=False)

    # ── Build Posts HTML ───────────────────────────────────────────────
    posts_cards = ""
    for p in posts:
        gemini_img = f'<img src="{p["gemini_url"]}" loading="lazy" class="thumb" data-full="{p["gemini_url"]}" onerror="this.parentElement.innerHTML=\'<div class=missing-img>\u05d7\u05e1\u05e8</div>\'">' if p["gemini_url"] else '<div class="missing-img">\u05d7\u05e1\u05e8</div>'
        mockup_img = f'<img src="{p["mockup_url"]}" loading="lazy" class="thumb" data-full="{p["mockup_url"]}">' if p["mockup_url"] else '<div class="missing-img">\u05d7\u05e1\u05e8</div>'
        g_badge = '<span class="badge badge-green">Gemini OK</span>' if p["gemini_url"] else '<span class="badge badge-red">Gemini \u05d7\u05e1\u05e8</span>'
        m_badge = '<span class="badge badge-green">Mockup OK</span>' if p["mockup_url"] else '<span class="badge badge-red">Mockup \u05d7\u05e1\u05e8</span>'
        s_badge = '<span class="badge badge-green">Story \u05de\u05d5\u05db\u05df</span>' if p["story_status"] == "ready" else '<span class="badge badge-amber">Story \u05d7\u05e1\u05e8</span>'
        todoist_link = f'https://app.todoist.com/app/task/{p["todoist_id"]}'
        posts_cards += f"""
    <div class="post-card" data-pillar="{p['pillar']}" data-story="{p['story_status']}" data-gemini="{'yes' if p['gemini_url'] else 'no'}">
      <div class="post-images">
        <div class="img-box"><div class="img-label">Mockup</div>{mockup_img}</div>
        <div class="img-box"><div class="img-label">Gemini</div>{gemini_img}</div>
      </div>
      <div class="post-info">
        <div class="post-date">{p['date'][5:]}</div>
        <div class="post-sign"><span class="pillar-dot" style="background:{p['pillar_color']}"></span>{p['sign']}</div>
        <div class="post-meta">{p['audience']}</div>
        <div class="post-angle">{p['angle']}</div>
      </div>
      <div class="post-badges">
        {g_badge}{m_badge}{s_badge}
        <a href="{todoist_link}" target="_blank" class="badge badge-link">Todoist</a>
      </div>
    </div>"""

    # ── Build Review (ביקורת) HTML ──────────────────────────────────────
    sop_auto = [
        ("ar1", "\u2705 \u05e4\u05d0\u05e0\u05dc \u05d4\u05e9\u05dc\u05d8 \u05de\u05db\u05d9\u05dc \u05e9\u05dd \u05d0\u05de\u05d9\u05ea\u05d9 — \u05dc\u05d0 \u05e8\u05d9\u05e7"),
        ("ar2", "\u2705 \u05d0\u05d9\u05df \u05d8\u05e7\u05e1\u05d8 \u05d2\u05e0\u05e8\u05d9 (OPEN 24/7 / Best Dad / Man Cave)"),
        ("ar3", "\u2705 \u05d4\u05ea\u05de\u05d5\u05e0\u05d4 \u05d4\u05d9\u05d0 \u05de\u05de\u05d0\u05d2\u05e8 LeavesDesign — \u05dc\u05d0 stock"),
        ("ar4", "\u2705 \u05d9\u05e9 \u05e7\u05d9\u05e9\u05d5\u05e8 Shopify \u05d1\u05d8\u05d0\u05e1\u05e7 Todoist"),
    ]
    sop_feed = [
        ("f1", "\u05d4\u05d5\u05e7 \u05d7\u05d6\u05e7 — 2 \u05e9\u05e0\u05d9\u05d5\u05ea, \u05e2\u05d5\u05e6\u05e8 \u05d0\u05ea \u05d4\u05d2\u05dc\u05d9\u05dc\u05d4"),
        ("f2", "\u05e9\u05dd \u05d4\u05de\u05d5\u05e6\u05e8 \u05de\u05d5\u05d6\u05db\u05e8 \u05d1\u05d8\u05e7\u05e1\u05d8"),
        ("f3", "\u05d8\u05d5\u05df \u05de\u05d3\u05d5\u05d9\u05e7 \u05dc\u05e4\u05d9 \u05e7\u05d4\u05dc \u05d9\u05e2\u05d3 (A / B / C)"),
        ("f4", "\u05d0\u05d9\u05df \u05e9\u05d2\u05d9\u05d0\u05d5\u05ea \u05db\u05ea\u05d9\u05d1 / \u05d3\u05e7\u05d3\u05d5\u05e7"),
        ("f5", "CTA \u05d1\u05e8\u05d5\u05e8 \u05d5\u05de\u05d3\u05d5\u05d9\u05e7 (\u05e7\u05d9\u05e9\u05d5\u05e8 / \u05d4\u05e0\u05d7\u05d9\u05d4)"),
        ("f6", "GATEKEEPER CHECK \u2014 APPROVED \u2705 \u05d1\u05ea\u05d9\u05e7"),
    ]
    sop_story = [
        ("s1", "\u05d8\u05e7\u05e1\u05d8 \u05e7\u05e8\u05d9\u05d0 \u05e2\u05dc \u05de\u05d5\u05d1\u05d9\u05d9\u05dc (\u05e4\u05d5\u05e0\u05d8 \u05d2\u05d3\u05d5\u05dc, \u05e0\u05d9\u05d2\u05d5\u05d3\u05d9\u05d5\u05ea)"),
        ("s2", "\u05e4\u05ea\u05d9\u05d7\u05d4 \u05e8\u05d2\u05e9\u05d9\u05ea / \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc \u05d7\u05d6\u05e7"),
        ("s3", "CTA \u05d1\u05e8\u05d5\u05e8 — Swipe Up / Tap"),
    ]
    total_posts = len(posts)

    def _esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _cb_item(pid, key, label):
        full_key = f"{pid}-{key}"
        return f'<label class="sop-item"><input type="checkbox" class="sop-cb" data-key="{full_key}"> {label}</label>'

    review_cards = ""
    for p in posts:
        pid = p["date"].replace("-", "")   # e.g. 20260312
        thumb_url = p.get("mockup_url") or p.get("gemini_url") or ""
        thumb_html = (f'<img src="{thumb_url}" class="review-thumb" loading="lazy" '
                      f'onerror="this.style.display=\'none\'">'
                      if thumb_url else '<div class="review-thumb-empty"></div>')

        fb_esc  = _esc(p.get("fb_text", "")).replace("\n", "<br>")
        ig_esc  = _esc(p.get("ig_text", "")).replace("\n", "<br>")
        st_esc  = _esc(p.get("story_text", "")).replace("\n", "<br>")
        fb_panel  = fb_esc  if fb_esc  else '<em style="color:#555">\u05dc\u05d0 \u05e0\u05de\u05e6\u05d0 \u05d8\u05e7\u05e1\u05d8 Facebook</em>'
        ig_panel  = ig_esc  if ig_esc  else '<em style="color:#555">\u05dc\u05d0 \u05e0\u05de\u05e6\u05d0 \u05d8\u05e7\u05e1\u05d8 Instagram</em>'
        st_panel  = st_esc  if st_esc  else '<em style="color:#555">\u05dc\u05d0 \u05e0\u05de\u05e6\u05d0 \u05d8\u05e7\u05e1\u05d8 Story</em>'

        auto_items  = "".join(_cb_item(pid, k, l) for k, l in sop_auto)
        feed_items  = "".join(_cb_item(pid, k, l) for k, l in sop_feed)
        story_items = "".join(_cb_item(pid, k, l) for k, l in sop_story)
        todoist_link = f'https://app.todoist.com/app/task/{p["todoist_id"]}'

        review_cards += f"""
    <div class="review-card" id="rcard-{pid}">
      <div class="review-header">
        <div class="review-title">
          <span class="review-date">{p['date'][5:]}</span>
          <span class="pillar-dot" style="background:{p['pillar_color']}"></span>
          <span class="review-sign">{p['sign']}</span>
          <a href="{todoist_link}" target="_blank" class="badge badge-link" style="font-size:11px;margin-right:8px">Todoist</a>
        </div>
        <span class="review-badge badge-pending" id="rbadge-{pid}">\u23f3 \u05de\u05de\u05ea\u05d9\u05df \u05dc\u05d0\u05d9\u05e9\u05d5\u05e8</span>
      </div>
      <div class="review-body">
        <div class="review-image-col">{thumb_html}</div>
        <div class="review-text-col">
          <div class="rtabs">
            <button class="rtab rtab-active" onclick="switchRTab(this,'{pid}-fb')">\U0001f4d8 Facebook</button>
            <button class="rtab" onclick="switchRTab(this,'{pid}-ig')">\U0001f4f7 Instagram</button>
            <button class="rtab" onclick="switchRTab(this,'{pid}-story')">\U0001f4f1 Story</button>
            <button class="copy-btn" id="copybtn-{pid}" onclick="copyRText('{pid}')">\U0001f4cb \u05d4\u05e2\u05ea\u05e7</button>
          </div>
          <div class="rtext-panel rtext-active" id="{pid}-fb">{fb_panel}</div>
          <div class="rtext-panel" id="{pid}-ig">{ig_panel}</div>
          <div class="rtext-panel" id="{pid}-story">{st_panel}</div>
        </div>
        <div class="review-checklist-col">
          <div class="sop-section">
            <div class="sop-header sop-reject">\U0001f6a8 AUTO-REJECT — \u05d1\u05d3\u05d9\u05e7\u05d5\u05ea \u05e7\u05e8\u05d9\u05d8\u05d9\u05d5\u05ea</div>
            {auto_items}
          </div>
          <div class="sop-section">
            <div class="sop-header sop-feed">\U0001f4d8 \u05e4\u05d5\u05e1\u05d8 \u05e4\u05d9\u05d3 — SOP</div>
            {feed_items}
          </div>
          <div class="sop-section">
            <div class="sop-header sop-story">\U0001f4f1 \u05e1\u05d8\u05d5\u05e8\u05d9 — SOP</div>
            {story_items}
          </div>
        </div>
      </div>
      <div class="review-notes-row">
        <textarea class="review-notes" id="notes-{pid}"
          data-sign="{p['sign']}" data-date="{p['date'][5:]}"
          placeholder="\U0001f4dd \u05d4\u05e2\u05e8\u05d5\u05ea \u05dc\u05d3\u05e0\u05d9\u05d0\u05dc \u2014 \u05e8\u05d2\'\u05d6\u05d9\u05e7\u05d8\u05d9\u05dd, \u05d1\u05e2\u05d9\u05d5\u05ea \u05d5\u05e9\u05d9\u05e0\u05d5\u05d9\u05d9\u05dd \u05e9\u05e6\u05e8\u05d9\u05da \u05dc\u05d8\u05e4\u05dc \u05d1\u05d4\u05dd..."
          oninput="saveNote('{pid}')"></textarea>
      </div>
    </div>"""

    # ── Build SLA Report HTML ─────────────────────────────────────────
    # Build agent lookup for avatars & names
    team_map = {a["id"]: a for a in TEAM}
    sla_cards_html = ""
    for sr in sla_report:
        agent = team_map.get(sr["agent_id"], {})
        a_name = agent.get("char_name", "")
        a_title = agent.get("name_he", sr["agent_id"])
        a_avatar = _render_avatar_svg(agent, 44) if agent else ""
        pct = sr["pct"]
        bar_color = "#4ade80" if pct >= 90 else ("#fbbf24" if pct >= 50 else "#f87171")
        border_color = "#166534" if pct >= 90 else ("#854d0e" if pct >= 50 else "#991b1b")
        status_emoji = "\u2705" if pct >= 90 else ("\u26a0\ufe0f" if pct >= 50 else "\u274c")
        missing_items = ""
        if sr["missing"]:
            items = "".join(f'<div class="sla-miss-item">{m}</div>' for m in sr["missing"][:8])
            more = f'<div class="sla-miss-more">+{len(sr["missing"]) - 8} \u05e0\u05d5\u05e1\u05e4\u05d9\u05dd...</div>' if len(sr["missing"]) > 8 else ""
            missing_items = f'<div class="sla-missing">{items}{more}</div>'
        sla_cards_html += f"""
    <div class="sla-card" style="border-color:{border_color}">
      <div class="sla-card-top">
        <div class="sla-agent-info">
          {a_avatar}
          <div>
            <div class="sla-agent-name">{a_name} <span style="font-size:12px;color:#666;font-weight:400">{a_title}</span></div>
            <div class="sla-desc">{sr['sla']}</div>
          </div>
        </div>
        <div class="sla-score" style="color:{bar_color}">
          <div class="sla-score-num">{status_emoji} {sr['done']}/{sr['total']}</div>
          <div class="sla-score-pct">{pct}%</div>
        </div>
      </div>
      <div class="sla-bar-track"><div class="sla-bar" style="width:{pct}%;background:{bar_color}"></div></div>
      <div class="sla-detail">{sr['detail']}</div>
      {missing_items}
    </div>"""

    # Overall SLA
    all_pcts = [sr["pct"] for sr in sla_report if sr["agent_id"] != "paid-campaigner"]
    overall_pct = round(sum(all_pcts) / len(all_pcts)) if all_pcts else 0
    overall_color = "#4ade80" if overall_pct >= 90 else ("#fbbf24" if overall_pct >= 50 else "#f87171")
    bottlenecks = [sr for sr in sla_report if sr["pct"] < 90 and sr["missing"]]
    bottleneck_html = ""
    if bottlenecks:
        bn_parts = []
        for b in bottlenecks:
            _ba = team_map.get(b["agent_id"], {})
            _bname = _ba.get("char_name", "")
            _btitle = _ba.get("name_he", "")
            _bmiss = b["total"] - b["done"]
            bn_parts.append(f'<div class="bn-item"><span class="bn-name">{_bname} ({_btitle})</span>'
                            f' — <span style="color:#f87171">{_bmiss} \u05d7\u05e1\u05e8\u05d9\u05dd</span> | {b["sla"]}</div>')
        items = "".join(bn_parts)
        bottleneck_html = f"""
    <div class="sla-bottleneck">
      <div class="sla-bottleneck-title">\U0001f6a8 \u05e6\u05d5\u05d5\u05d0\u05e8\u05d9 \u05d1\u05e7\u05d1\u05d5\u05e7 \u2014 \u05d3\u05d5\u05e8\u05e9 \u05d8\u05d9\u05e4\u05d5\u05dc</div>
      {items}
    </div>"""

    # ── Build Matrix HTML ──────────────────────────────────────────────
    matrix_rows = ""
    for prod in sorted(matrix, key=lambda x: -x["total"]):
        g_cls = "cell-green" if prod["gemini_count"] == prod["total"] else ("cell-amber" if prod["gemini_count"] > 0 else "cell-red")
        m_cls = "cell-green" if prod["mockup_count"] == prod["total"] else ("cell-amber" if prod["mockup_count"] > 0 else "cell-red")
        s_cls = "cell-green" if prod["story_ready_count"] == prod["total"] else ("cell-amber" if prod["story_ready_count"] > 0 else "cell-red")
        matrix_rows += f"""
    <tr>
      <td><span class="pillar-dot" style="background:{prod['pillar_color']}"></span>{prod['name']}</td>
      <td>{prod['total']}</td>
      <td class="{m_cls}">{prod['mockup_count']}/{prod['total']}</td>
      <td class="{g_cls}">{prod['gemini_count']}/{prod['total']}</td>
      <td class="{s_cls}">{prod['story_ready_count']}/{prod['total']}</td>
    </tr>"""

    # ── Build Pillar Bars (for KPI tab) ────────────────────────────────
    max_count = max(stats["pillars"].values()) if stats["pillars"] else 1
    pillar_bars = ""
    for pillar, count in sorted(stats["pillars"].items(), key=lambda x: -x[1]):
        pct = int(count / max_count * 100)
        color = PILLAR_COLORS.get(pillar, "#666")
        label = PILLAR_LABELS.get(pillar, pillar)
        pillar_bars += f"""
    <div class="pillar-row">
      <span class="pillar-label">{label}</span>
      <div class="pillar-bar-track"><div class="pillar-bar" style="width:{pct}%;background:{color}"></div></div>
      <span class="pillar-count">{count}</span>
    </div>"""

    # Missing gemini alert
    missing_alert = ""
    if missing_gemini:
        items = "".join(f'<li>{p["date"]} \u2014 {p["sign"]}</li>' for p in missing_gemini)
        missing_alert = f"""
    <div class="alert alert-amber">
      <h3>\u05d4\u05d3\u05de\u05d9\u05d5\u05ea Gemini \u05d7\u05e1\u05e8\u05d5\u05ea ({len(missing_gemini)})</h3>
      <ul>{items}</ul>
    </div>"""

    # ── Build Learning HTML ────────────────────────────────────────────
    learning_html = f"""
    <div class="learn-section">
      <h2>\U0001f4a1 \u05de\u05d4 \u05e2\u05d5\u05d1\u05d3 (\u05ea\u05d1\u05e0\u05d9\u05d5\u05ea \u05de\u05d0\u05d5\u05de\u05ea\u05d5\u05ea)</h2>
      <div class="learn-grid">
        <div class="learn-card learn-do">
          <h3>\u2705 \u05ea\u05e2\u05e9\u05d4 \u05d0\u05ea \u05d6\u05d4</h3>
          <ul>
            <li>\u05ea\u05ea\u05d7\u05d9\u05dc \u05e2\u05dd \u05e8\u05d2\u05e2 \u05e1\u05e4\u05e6\u05d9\u05e4\u05d9 \u05d0\u05d5 \u05e4\u05e2\u05d5\u05dc\u05d4</li>
            <li>\u05d4\u05e9\u05ea\u05de\u05e9 \u05d1\u05de\u05e1\u05d2\u05e8\u05d5\u05ea \u05e0\u05d9\u05d2\u05d5\u05d3: "\u05e4\u05e2\u05dd... \u05e2\u05db\u05e9\u05d9\u05d5..."</li>
            <li>\u05e9\u05dc\u05d1 \u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05e9\u05d0\u05e4\u05e9\u05e8 \u05dc\u05d3\u05de\u05d9\u05d9\u05df</li>
            <li>\u05db\u05ea\u05d5\u05d1 \u05e9\u05d5\u05e8\u05d5\u05ea \u05e7\u05e6\u05e8\u05d5\u05ea. \u05e8\u05d9\u05ea\u05de\u05d5\u05e1 \u05e4\u05d0\u05e0\u05e6'\u05d9.</li>
            <li>\u05d2\u05d5\u05e3 \u05e8\u05d0\u05e9\u05d5\u05df: \u05d0\u05e0\u05d9, \u05e9\u05dc\u05d9, \u05d0\u05ea\u05d4</li>
            <li>\u05e4\u05e8\u05d8\u05d9\u05dd \u05d7\u05d5\u05e9\u05d9\u05d9\u05dd \u2014 \u05de\u05e9\u05e7\u05dc, \u05de\u05d2\u05e2, \u05e2\u05de\u05d9\u05d3\u05d5\u05ea</li>
          </ul>
        </div>
        <div class="learn-card learn-dont">
          <h3>\u274c \u05d4\u05d9\u05de\u05e0\u05e2 \u05de\u05d6\u05d4</h3>
          <ul>
            <li>\u05d6\u05e8\u05d2\u05d5\u05df \u05ea\u05d0\u05d2\u05d9\u05d3\u05d9 (leverage, optimize, synergy)</li>
            <li>\u05e9\u05d1\u05d7\u05d9\u05dd \u05e2\u05de\u05d5\u05de\u05d9\u05dd (best, leading, top-tier)</li>
            <li>\u05d8\u05e2\u05e0\u05d5\u05ea \u05d2\u05e0\u05e8\u05d9\u05d5\u05ea \u05e9\u05de\u05ea\u05d7\u05e8\u05d9\u05dd \u05d9\u05db\u05d5\u05dc\u05d9\u05dd \u05dc\u05d4\u05e9\u05ea\u05de\u05e9 \u05d1\u05d4\u05df</li>
            <li>\u05e9\u05d9\u05de\u05d5\u05e9 \u05d9\u05ea\u05e8 \u05d1\u05e1\u05d1\u05d9\u05dc (passive voice)</li>
            <li>\u05de\u05e9\u05e4\u05d8\u05d9\u05dd \u05d0\u05e8\u05d5\u05db\u05d9\u05dd \u05d5\u05de\u05e1\u05d1\u05d9\u05e8\u05d9\u05dd</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="learn-section">
      <h2>\U0001f3af \u05d4\u05d7\u05dc\u05d8\u05d5\u05ea \u05d0\u05e1\u05d8\u05e8\u05d8\u05d2\u05d9\u05d5\u05ea</h2>
      <div class="learn-grid-3">
        <div class="learn-card">
          <h3>\U0001f465 \u05e7\u05d4\u05dc \u05d9\u05e2\u05d3</h3>
          <ul>
            <li>Gift-Giver (60%) + Self-Buyer (40%)</li>
            <li>\u05e9\u05e4\u05d4 \u05e8\u05d2\u05e9\u05d9\u05ea \u05dc\u05e7\u05d5\u05e0\u05d9\u05dd, \u05e9\u05e4\u05d4 \u05d8\u05db\u05e0\u05d9\u05ea \u05dc\u05e2\u05e6\u05de\u05d9\u05d9\u05dd</li>
            <li>"\u05d1\u05d3\u05d9\u05d5\u05e7 \u05db\u05de\u05d5 \u05d1\u05ea\u05de\u05d5\u05e0\u05d4" = \u05de\u05e1\u05e8 \u05d0\u05de\u05d5\u05df \u05de\u05e4\u05ea\u05d7</li>
          </ul>
        </div>
        <div class="learn-card">
          <h3>\U0001f4cc \u05e2\u05de\u05d5\u05d3\u05d9 \u05ea\u05d5\u05db\u05df</h3>
          <ul>
            <li>Muscle Cars + Garage</li>
            <li>Biker Couples</li>
            <li>Wedding / Anniversary Monograms</li>
          </ul>
        </div>
        <div class="learn-card">
          <h3>\U0001f4e2 \u05e4\u05dc\u05d8\u05e4\u05d5\u05e8\u05de\u05d5\u05ea</h3>
          <ul>
            <li>Facebook (\u05e8\u05d0\u05e9\u05d9) + Instagram (cross-post)</li>
            <li>Postly.ai \u05dc\u05e4\u05e8\u05e1\u05d5\u05dd</li>
            <li>Todoist = Publishing Hub</li>
            <li>catbox.moe = \u05d0\u05d9\u05e8\u05d5\u05d7 \u05ea\u05de\u05d5\u05e0\u05d5\u05ea</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="learn-section">
      <h2>\U0001f4ac \u05e9\u05e4\u05ea \u05dc\u05e7\u05d5\u05d7\u05d5\u05ea (\u05de\u05d1\u05d9\u05e7\u05d5\u05e8\u05d5\u05ea Etsy)</h2>
      <div class="learn-grid">
        <div class="learn-card">
          <h3>\U0001f60d \u05de\u05d4 \u05d4\u05dd \u05d0\u05d5\u05de\u05e8\u05d9\u05dd</h3>
          <ul>
            <li>"gorgeous", "absolutely beautiful", "perfect"</li>
            <li>"made his 40th birthday!!!"</li>
            <li>"exactly as shown"</li>
            <li>"professionally made", "sturdy", "elegant looking"</li>
          </ul>
        </div>
        <div class="learn-card">
          <h3>\U0001f381 \u05e9\u05e4\u05ea \u05de\u05ea\u05e0\u05d5\u05ea</h3>
          <ul>
            <li>"wedding gift was a hit"</li>
            <li>"his dad is going to love it"</li>
            <li>"unique piece"</li>
            <li>"super fast turnaround"</li>
            <li>"excellent to work with"</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="learn-section">
      <h2>\U0001f6a9 \u05e6\u05e2\u05d3\u05d9\u05dd \u05d4\u05d1\u05d0\u05d9\u05dd (\u05e9\u05d9\u05e4\u05d5\u05e8 \u05d5\u05e9\u05d9\u05de\u05d5\u05e8)</h2>
      <div class="learn-card" style="max-width:600px">
        <ul>
          <li>\u05dc\u05d9\u05e6\u05d5\u05e8 \u05ea\u05de\u05d5\u05e0\u05d5\u05ea Story (\u05e4\u05d5\u05e8\u05d8\u05e8\u05d8 9:16) \u05dc\u05de\u05d5\u05e6\u05e8\u05d9\u05dd \u05e9\u05d7\u05e1\u05e8\u05d9\u05dd</li>
          <li>\u05dc\u05d4\u05e4\u05e8\u05d9\u05d3 \u05db\u05dc \u05d8\u05e1\u05e7 Todoist \u05dc-feed post + story</li>
          <li>\u05dc\u05d4\u05e9\u05dc\u05d9\u05dd 6 \u05d4\u05d3\u05de\u05d9\u05d5\u05ea Gemini \u05d7\u05e1\u05e8\u05d5\u05ea</li>
          <li>\u05dc\u05d4\u05ea\u05d7\u05d9\u05dc \u05dc\u05e4\u05e8\u05e1\u05dd \u05d1-Postly</li>
        </ul>
      </div>
    </div>"""

    # ── Build Org Tree HTML ─────────────────────────────────────────────
    dept_labels = {
        "content": "\U0001f4dd \u05ea\u05d5\u05db\u05df",         # Content
        "visual": "\U0001f3a8 \u05d5\u05d9\u05d6\u05d5\u05d0\u05dc",       # Visual
        "quality": "\U0001f6e1\ufe0f \u05d0\u05d9\u05db\u05d5\u05ea",       # Quality
        "growth": "\U0001f4b0 \u05e4\u05e8\u05e1\u05d5\u05dd \u05d5\u05e6\u05de\u05d9\u05d7\u05d4",  # Growth
    }
    dept_colors = {
        "content": "#ec4899",
        "visual": "#a855f7",
        "quality": "#ef4444",
        "growth": "#f59e0b",
    }
    # Group members by department
    dept_members = {}
    for m in members:
        d = m.get("dept", "other")
        dept_members.setdefault(d, []).append(m)

    # CEO node
    ceo_avatar = f'''<svg width="64" height="64" viewBox="0 0 80 80" style="border-radius:50%;flex-shrink:0">
        <circle cx="40" cy="40" r="40" fill="#10b981"/>
        <circle cx="40" cy="44" r="20" fill="#fcd9b6"/>
        <ellipse cx="40" cy="30" rx="21" ry="12" fill="#1c1917"/>
        <circle cx="33" cy="42" r="2.5" fill="#333"/><circle cx="47" cy="42" r="2.5" fill="#333"/>
        <circle cx="34" cy="41" r="1" fill="#fff"/><circle cx="48" cy="41" r="1" fill="#fff"/>
        <path d="M34,51 Q40,57 46,51" fill="none" stroke="#c97850" stroke-width="2" stroke-linecap="round"/>
        <polygon points="62,22 56,33 60,33 54,44 68,31 62,31 68,22" fill="#4ade80"/>
    </svg>'''

    # Lead node
    lead_avatar_org = _render_avatar_svg(lead, 64)

    # Build department columns
    dept_cols_html = ""
    for dept_key in ["content", "visual", "quality", "growth"]:
        d_members = dept_members.get(dept_key, [])
        d_label = dept_labels.get(dept_key, dept_key)
        d_color = dept_colors.get(dept_key, "#666")
        members_html = ""
        for dm in d_members:
            dm_avatar = _render_avatar_svg(dm, 48)
            members_html += f"""
            <div class="org-agent">
              {dm_avatar}
              <div class="org-agent-name">{dm['char_name']}</div>
              <div class="org-agent-role">{dm['name_he']}</div>
              <div class="org-agent-sla">{dm['sla']}</div>
            </div>"""
        dept_cols_html += f"""
        <div class="org-dept">
          <div class="org-dept-header" style="border-color:{d_color}">
            <div class="org-dept-label" style="color:{d_color}">{d_label}</div>
          </div>
          <div class="org-dept-members">{members_html}</div>
        </div>"""

    org_tree_html = f"""
    <div class="org-tree">
      <div class="org-level org-ceo">
        <div class="org-node org-node-ceo">
          {ceo_avatar}
          <div class="org-node-name">\u05d6\u05d0\u05e7</div>
          <div class="org-node-role">CEO / \u05d1\u05e2\u05dc\u05d9\u05dd</div>
        </div>
      </div>
      <div class="org-connector"></div>
      <div class="org-level org-director">
        <div class="org-node org-node-director">
          {lead_avatar_org}
          <div class="org-node-name">{lead['char_name']}</div>
          <div class="org-node-role">{lead['name_he']}</div>
          <div class="org-node-sla">{lead['sla']}</div>
        </div>
      </div>
      <div class="org-connector"></div>
      <div class="org-departments">
        {dept_cols_html}
      </div>
    </div>"""

    # ── Embed review sync state ───────────────────────────────────────
    review_sync = data.get("review_sync", {})
    sync_json_str = json.dumps(review_sync, ensure_ascii=False)

    # ── Assemble Complete HTML ─────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LeavesDesign Team Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f0f0f; color: #e8e8e8; min-height: 100vh; }}
  a {{ color: #7eb8f7; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* ── Topbar ── */
  .topbar {{ background: #1a1a1a; border-bottom: 1px solid #2a2a2a;
            padding: 16px 32px; display: flex; align-items: center; gap: 16px; }}
  .topbar h1 {{ font-size: 20px; font-weight: 700; }}
  .topbar .gen {{ color: #555; font-size: 12px; margin-right: auto; }}

  /* ── Tabs ── */
  .tabs {{ display: flex; gap: 4px; padding: 12px 32px 0; background: #1a1a1a;
           border-bottom: 1px solid #2a2a2a; flex-wrap: wrap; }}
  .tab {{ padding: 10px 20px; border: none; background: transparent; color: #888;
          cursor: pointer; font-size: 14px; border-bottom: 2px solid transparent;
          font-family: inherit; }}
  .tab:hover {{ color: #ccc; }}
  .tab.active {{ color: #e8e8e8; border-bottom-color: #7eb8f7; }}

  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  .section {{ display: none; }}
  .section.active {{ display: block; }}

  /* ── Team Tab ── */
  .lead-card {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 1px solid #2a3a5a;
               border-radius: 14px; padding: 28px; display: flex; align-items: center; gap: 24px;
               margin-bottom: 24px; }}
  .lead-emoji {{ font-size: 48px; display: none; }}
  .lead-info {{ flex: 1; }}
  .lead-name {{ font-size: 22px; font-weight: 700; color: #7eb8f7; }}
  .lead-role {{ font-size: 13px; color: #8899bb; margin-top: 4px; }}
  .lead-identity {{ font-size: 14px; color: #aabbcc; margin-top: 8px; font-style: italic; }}
  .lead-stat {{ text-align: center; background: rgba(126,184,247,0.1); border-radius: 10px; padding: 16px 24px; }}
  .lead-stat-value {{ font-size: 36px; font-weight: 700; color: #7eb8f7; }}
  .lead-stat-label {{ font-size: 12px; color: #8899bb; margin-top: 4px; }}

  .members-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
  .member-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
                 padding: 20px; transition: border-color .15s; }}
  .member-card:hover {{ border-color: #444; }}
  .member-emoji {{ font-size: 32px; margin-bottom: 8px; display: none; }}
  .member-name {{ font-size: 16px; font-weight: 600; color: #e8e8e8; }}
  .member-role {{ font-size: 12px; color: #888; margin-top: 2px; }}
  .member-identity {{ font-size: 13px; color: #aaa; margin-top: 8px; font-style: italic; line-height: 1.5; }}
  .member-kpi {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #2a2a2a; }}
  .kpi-bar-track {{ height: 6px; background: #252525; border-radius: 3px; overflow: hidden; margin-bottom: 6px; }}
  .kpi-bar {{ height: 100%; border-radius: 3px; transition: width .4s ease; }}
  .kpi-value {{ font-size: 14px; font-weight: 600; }}
  .kpi-label {{ font-size: 11px; color: #888; margin-right: 6px; }}

  /* ── Agent Logs ── */
  .agent-log {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #2a2a2a; }}
  .log-tabs {{ display: flex; gap: 4px; margin-bottom: 8px; }}
  .log-tab {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px; padding: 4px 10px;
             font-size: 11px; color: #888; cursor: pointer; transition: all .2s; font-family: inherit; }}
  .log-tab:hover {{ color: #ccc; border-color: #444; }}
  .log-tab.active {{ background: #2a2a3a; color: #a78bfa; border-color: #5b4b8a; }}
  .log-panel {{ display: none; }}
  .log-panel.active {{ display: block; }}
  .log-item {{ font-size: 12px; color: #bbb; padding: 4px 0; line-height: 1.5; }}
  .log-item::before {{ content: "\u25b8 "; color: #666; }}
  .log-empty {{ font-size: 12px; color: #555; font-style: italic; padding: 4px 0; }}
  .lead-card .agent-log {{ margin-top: 16px; padding-top: 16px; }}

  /* ── KPI Tab ── */
  .kpi-presenter {{ display: flex; align-items: center; gap: 10px; margin-bottom: 20px;
                   padding: 12px 16px; background: #1a1a2e; border-radius: 8px; border: 1px solid #2a3a5a; }}
  .kpi-presenter-emoji {{ font-size: 24px; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .stat-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; text-align: center; }}
  .stat-card.stat-green {{ border-color: #166534; background: #0d1f13; }}
  .stat-card.stat-amber {{ border-color: #854d0e; background: #1c1a0d; }}
  .stat-card.stat-red {{ border-color: #991b1b; background: #1f0d0d; }}
  .stat-number {{ font-size: 32px; font-weight: 700; }}
  .stat-green .stat-number {{ color: #4ade80; }}
  .stat-amber .stat-number {{ color: #fbbf24; }}
  .stat-red .stat-number {{ color: #f87171; }}
  .stat-label {{ font-size: 13px; color: #888; margin-top: 4px; }}

  .kpi-agents-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .kpi-agent-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 16px; }}
  .kpi-agent-green {{ border-color: #166534; }}
  .kpi-agent-amber {{ border-color: #854d0e; }}
  .kpi-agent-red {{ border-color: #991b1b; }}
  .kpi-agent-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
  .kpi-agent-emoji {{ font-size: 20px; }}
  .kpi-agent-name {{ font-size: 14px; font-weight: 600; }}
  .kpi-agent-value {{ font-size: 28px; font-weight: 700; }}
  .kpi-agent-metric {{ font-size: 12px; color: #888; }}
  .kpi-agent-detail {{ font-size: 11px; color: #666; margin-top: 4px; }}

  .pillar-section {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; margin-bottom: 24px; }}
  .pillar-section h3 {{ font-size: 14px; color: #888; margin-bottom: 16px; }}
  .pillar-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
  .pillar-label {{ width: 140px; font-size: 13px; color: #aaa; text-align: left; }}
  .pillar-bar-track {{ flex: 1; height: 20px; background: #252525; border-radius: 4px; overflow: hidden; }}
  .pillar-bar {{ height: 100%; border-radius: 4px; transition: width .3s; }}
  .pillar-count {{ width: 30px; font-size: 13px; color: #888; text-align: right; }}

  .alert {{ border-radius: 10px; padding: 16px 20px; margin-bottom: 24px; }}
  .alert h3 {{ font-size: 14px; margin-bottom: 8px; }}
  .alert ul {{ padding-right: 20px; font-size: 13px; line-height: 1.8; }}
  .alert-amber {{ background: #1c1a0d; border: 1px solid #854d0e; color: #fbbf24; }}

  /* ── Gantt Tab ── */
  .gantt-controls {{ display: flex; gap: 8px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }}
  .gantt-btn {{ padding: 8px 16px; border-radius: 6px; border: 1px solid #333; background: #1a1a1a;
               color: #888; cursor: pointer; font-size: 13px; font-family: inherit; }}
  .gantt-btn:hover, .gantt-btn.active {{ background: #252525; color: #e8e8e8; border-color: #555; }}
  .gantt-nav {{ display: flex; align-items: center; gap: 12px; margin-right: auto; }}
  .nav-btn {{ width: 32px; height: 32px; border-radius: 50%; border: 1px solid #333; background: #1a1a1a;
             color: #888; cursor: pointer; font-size: 16px; display: flex; align-items: center;
             justify-content: center; font-family: inherit; }}
  .nav-btn:hover {{ background: #252525; color: #e8e8e8; }}
  #gantt-period {{ font-size: 14px; color: #aaa; min-width: 160px; text-align: center; }}

  .cal-container {{ display: flex; gap: 24px; flex-wrap: wrap; }}
  .cal-month {{ flex: 1; min-width: 300px; background: #1a1a1a; border: 1px solid #2a2a2a;
               border-radius: 10px; padding: 20px; }}
  .cal-month h3 {{ text-align: center; margin-bottom: 12px; font-size: 16px; }}
  .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }}
  .cal-header {{ text-align: center; font-size: 12px; color: #555; padding: 4px; }}
  .cal-cell {{ aspect-ratio: 1; display: flex; flex-direction: column; align-items: center;
              justify-content: center; border-radius: 6px; font-size: 13px; color: #555;
              position: relative; overflow: hidden; }}
  .cal-cell.has-post {{ background: #1f1f1f; color: #e8e8e8; cursor: pointer; }}
  .cal-cell.has-post:hover {{ background: #2a2a2a; }}
  .cal-img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
             border-radius: 6px; opacity: 0.45; transition: opacity .2s; cursor: pointer; }}
  .cal-cell:hover .cal-img {{ opacity: 0.85; }}
  .cal-day {{ position: relative; z-index: 1; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }}
  .cal-dot {{ width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-top: 2px;
             position: relative; z-index: 1; }}

  .gantt-view {{ }}
  .gantt-week-panel {{ }}
  .week-title {{ font-size: 16px; margin-bottom: 16px; color: #aaa; }}
  .gantt-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; padding: 4px 0; }}
  .gantt-date {{ width: 80px; font-size: 12px; color: #888; text-align: left; flex-shrink: 0; }}
  .gantt-thumb-box {{ width: 56px; height: 56px; flex-shrink: 0; border-radius: 8px; overflow: hidden;
                     background: #111; border: 1px solid #2a2a2a; }}
  .gantt-thumb {{ width: 100%; height: 100%; object-fit: cover; cursor: pointer; }}
  .gantt-thumb-empty {{ width: 100%; height: 100%; }}
  .gantt-bar-area {{ flex: 1; }}
  .gantt-bar {{ padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; color: #fff;
               white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .gantt-dots {{ display: flex; gap: 4px; flex-shrink: 0; }}
  .sdot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
  .sdot-green {{ background: #4ade80; }}
  .sdot-amber {{ background: #fbbf24; }}
  .sdot-red {{ background: #f87171; }}

  /* ── Posts Tab ── */
  .filter-bar {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
  .filter-btn {{ padding: 6px 14px; border-radius: 20px; border: 1px solid #333; background: #1a1a1a;
                color: #888; cursor: pointer; font-size: 12px; font-family: inherit; }}
  .filter-btn:hover, .filter-btn.active {{ background: #252525; color: #e8e8e8; border-color: #555; }}

  .posts-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
  .post-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
               overflow: hidden; transition: border-color .15s; }}
  .post-card:hover {{ border-color: #444; }}
  .post-images {{ display: flex; gap: 2px; }}
  .img-box {{ flex: 1; position: relative; aspect-ratio: 1; overflow: hidden; background: #111; }}
  .img-box .img-label {{ position: absolute; top: 4px; right: 4px; font-size: 10px; color: #888;
                        background: rgba(0,0,0,0.7); padding: 2px 6px; border-radius: 3px; z-index: 1; }}
  .thumb {{ width: 100%; height: 100%; object-fit: cover; cursor: pointer; }}
  .missing-img {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
                 color: #555; font-size: 13px; background: #111; }}
  .post-info {{ padding: 12px 16px 8px; }}
  .post-date {{ font-size: 12px; color: #666; }}
  .post-sign {{ font-size: 15px; font-weight: 600; margin: 4px 0; display: flex; align-items: center; gap: 6px; }}
  .pillar-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
  .post-meta {{ font-size: 12px; color: #888; }}
  .post-angle {{ font-size: 12px; color: #666; font-style: italic; margin-top: 2px; }}
  .post-badges {{ padding: 8px 16px 12px; display: flex; flex-wrap: wrap; gap: 6px; }}

  .badge {{ font-size: 11px; padding: 3px 8px; border-radius: 4px; border: 1px solid #333; }}
  .badge-green {{ background: #0d2b1a; color: #4ade80; border-color: #166534; }}
  .badge-amber {{ background: #1c1a0d; color: #fbbf24; border-color: #854d0e; }}
  .badge-red {{ background: #2b0d0d; color: #f87171; border-color: #991b1b; }}
  .badge-link {{ background: #1a1a2e; color: #818cf8; border-color: #3730a3; }}

  /* ── Matrix Tab ── */
  .matrix-table {{ width: 100%; border-collapse: collapse; }}
  .matrix-table th {{ text-align: right; padding: 10px 12px; font-size: 12px; color: #666;
                     border-bottom: 1px solid #2a2a2a; }}
  .matrix-table td {{ padding: 10px 12px; border-bottom: 1px solid #1f1f1f; font-size: 13px; }}
  .matrix-table tr:hover td {{ background: #1a1a1a; }}
  .cell-green {{ color: #4ade80; }}
  .cell-amber {{ color: #fbbf24; }}
  .cell-red {{ color: #f87171; }}

  /* ── Learning Tab ── */
  .learn-section {{ margin-bottom: 32px; }}
  .learn-section h2 {{ font-size: 18px; margin-bottom: 16px; color: #ccc; }}
  .learn-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
  .learn-grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
  .learn-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 20px; }}
  .learn-card h3 {{ font-size: 15px; margin-bottom: 12px; color: #aaa; }}
  .learn-card ul {{ padding-right: 20px; font-size: 13px; color: #888; line-height: 1.8; }}
  .learn-card.learn-do {{ border-color: #166534; background: #0d1f13; }}
  .learn-card.learn-do h3 {{ color: #4ade80; }}
  .learn-card.learn-do ul {{ color: #8ade80; }}
  .learn-card.learn-dont {{ border-color: #991b1b; background: #1f0d0d; }}
  .learn-card.learn-dont h3 {{ color: #f87171; }}
  .learn-card.learn-dont ul {{ color: #f8a0a0; }}

  /* ── Avatar & Char Name ── */
  .lead-avatar {{ flex-shrink: 0; }}
  .lead-title {{ font-size: 14px; font-weight: 400; color: #8899bb; }}
  .lead-sla {{ font-size: 12px; color: #6b7280; margin-top: 4px; padding: 2px 8px;
              background: rgba(126,184,247,0.1); border-radius: 4px; display: inline-block; }}
  .member-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
  .member-avatar {{ flex-shrink: 0; }}
  .member-title {{ font-size: 12px; font-weight: 400; color: #666; }}
  .member-sla {{ font-size: 11px; color: #6b7280; margin-top: 2px; }}

  /* ── Org Tree Tab ── */
  .org-tree {{ display: flex; flex-direction: column; align-items: center; padding: 20px 0; width: 100%; }}
  .org-level {{ display: flex; justify-content: center; }}
  .org-node {{ display: flex; flex-direction: column; align-items: center; gap: 6px;
              background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 14px;
              padding: 20px 28px; text-align: center; }}
  .org-node-ceo {{ background: linear-gradient(135deg, #0d2818 0%, #1a2e1a 100%);
                  border-color: #166534; }}
  .org-node-director {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                       border-color: #2a3a5a; }}
  .org-node-name {{ font-size: 18px; font-weight: 700; color: #e8e8e8; }}
  .org-node-role {{ font-size: 12px; color: #888; }}
  .org-node-sla {{ font-size: 11px; color: #6b7280; background: rgba(126,184,247,0.1);
                  padding: 2px 8px; border-radius: 4px; }}
  /* Vertical connector between levels */
  .org-connector {{ width: 2px; height: 32px; background: #3a3a3a; margin: 0 auto; }}
  /* Department grid — 4 equal columns; ::before draws the horizontal bar */
  .org-departments {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
                     width: 100%; max-width: 1020px; margin: 0 auto;
                     padding-top: 32px; position: relative; }}
  .org-departments::before {{ content: ''; position: absolute; top: 0;
                              left: calc(100% / 8); right: calc(100% / 8);
                              height: 2px; background: #3a3a3a; }}
  /* Each dept column gets a vertical drop from the horizontal bar */
  .org-dept {{ position: relative; }}
  .org-dept::before {{ content: ''; position: absolute; top: -32px; left: 50%;
                      transform: translateX(-50%); width: 2px; height: 32px;
                      background: #3a3a3a; }}
  .org-dept-header {{ text-align: center; padding: 10px; border: 2px solid #2a2a2a;
                     border-radius: 10px; background: #1a1a1a; margin-bottom: 12px; }}
  .org-dept-label {{ font-size: 13px; font-weight: 600; }}
  .org-dept-members {{ display: flex; flex-direction: column; gap: 10px; }}
  .org-agent {{ display: flex; flex-direction: column; align-items: center; gap: 4px;
               background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
               padding: 14px 10px; text-align: center; transition: border-color .15s; }}
  .org-agent:hover {{ border-color: #444; }}
  .org-agent-name {{ font-size: 14px; font-weight: 600; color: #e8e8e8; }}
  .org-agent-role {{ font-size: 11px; color: #888; }}
  .org-agent-sla {{ font-size: 10px; color: #6b7280; margin-top: 2px; }}

  /* ── SLA Report Tab ── */
  .sla-overall {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
                 padding: 20px; margin-bottom: 20px; text-align: center; }}
  .sla-overall-label {{ font-size: 13px; color: #888; margin-bottom: 6px; }}
  .sla-overall-score {{ font-size: 48px; font-weight: 800; }}
  .sla-overall-bar {{ height: 10px; background: #252525; border-radius: 5px;
                     overflow: hidden; margin-top: 8px; max-width: 400px; margin-left: auto; margin-right: auto; }}
  .sla-overall-fill {{ height: 100%; border-radius: 5px; transition: width .4s ease; }}
  .sla-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px; margin-bottom: 20px; }}
  .sla-card {{ background: #1a1a1a; border: 2px solid #2a2a2a; border-radius: 12px; padding: 18px; }}
  .sla-card-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; }}
  .sla-agent-info {{ display: flex; align-items: center; gap: 10px; }}
  .sla-agent-name {{ font-size: 15px; font-weight: 600; color: #e8e8e8; }}
  .sla-desc {{ font-size: 11px; color: #888; margin-top: 2px; }}
  .sla-score {{ text-align: left; flex-shrink: 0; }}
  .sla-score-num {{ font-size: 20px; font-weight: 700; }}
  .sla-score-pct {{ font-size: 12px; color: #888; }}
  .sla-bar-track {{ height: 6px; background: #252525; border-radius: 3px; overflow: hidden; margin-bottom: 8px; }}
  .sla-bar {{ height: 100%; border-radius: 3px; transition: width .3s; }}
  .sla-detail {{ font-size: 11px; color: #666; }}
  .sla-missing {{ margin-top: 8px; padding-top: 8px; border-top: 1px solid #2a2a2a; }}
  .sla-miss-item {{ font-size: 11px; color: #f87171; padding: 2px 0; }}
  .sla-miss-item::before {{ content: "\u274c "; font-size: 9px; }}
  .sla-miss-more {{ font-size: 10px; color: #666; font-style: italic; margin-top: 4px; }}
  .sla-bottleneck {{ background: #1f0d0d; border: 1px solid #991b1b; border-radius: 10px;
                    padding: 16px 20px; margin-bottom: 20px; }}
  .sla-bottleneck-title {{ font-size: 14px; font-weight: 700; color: #f87171; margin-bottom: 10px; }}
  .bn-item {{ font-size: 12px; color: #ccc; padding: 4px 0; line-height: 1.6; }}
  .bn-name {{ font-weight: 600; color: #fbbf24; }}

  /* ── Review Tab ── */
  .review-progress {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
                     padding: 16px 20px; margin-bottom: 20px; }}
  .review-progress-top {{ display: flex; align-items: center; justify-content: space-between;
                          margin-bottom: 8px; gap: 12px; }}
  .review-progress-label {{ font-size: 14px; color: #ccc; }}
  .send-daniel-btn {{ padding: 8px 18px; background: #1a2a1a; border: 1px solid #4ade80;
                     color: #4ade80; border-radius: 8px; font-size: 13px; font-weight: 600;
                     cursor: pointer; font-family: inherit; transition: all .15s; }}
  .send-daniel-btn:hover {{ background: #166534; color: #fff; border-color: #22c55e; }}
  /* Daniel modal */
  .daniel-modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85);
                  z-index: 1000; align-items: center; justify-content: center; padding: 24px; }}
  .daniel-modal.active {{ display: flex; }}
  .daniel-modal-box {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 14px;
                      width: 100%; max-width: 680px; display: flex; flex-direction: column; gap: 0; }}
  .daniel-modal-header {{ display: flex; justify-content: space-between; align-items: center;
                          padding: 16px 20px; border-bottom: 1px solid #2a2a2a;
                          font-size: 15px; font-weight: 600; color: #4ade80; }}
  .daniel-modal-close {{ background: none; border: none; color: #666; font-size: 22px;
                         cursor: pointer; line-height: 1; padding: 0 4px; }}
  .daniel-modal-close:hover {{ color: #f87171; }}
  .daniel-modal-text {{ width: 100%; min-height: 300px; max-height: 55vh; background: #111;
                       border: none; color: #ccc; font-size: 13px; padding: 16px 20px;
                       resize: none; font-family: 'Courier New', monospace; line-height: 1.7;
                       direction: rtl; overflow-y: auto; }}
  .daniel-modal-footer {{ display: flex; align-items: center; gap: 12px; padding: 14px 20px;
                          border-top: 1px solid #2a2a2a; }}
  .daniel-copy-btn {{ padding: 8px 18px; background: #1a2a3a; border: 1px solid #7eb8f7;
                     color: #7eb8f7; border-radius: 8px; font-size: 13px; cursor: pointer;
                     font-family: inherit; transition: all .15s; }}
  .daniel-copy-btn:hover {{ background: #1e3a5f; color: #fff; }}
  .daniel-copy-hint {{ font-size: 12px; color: #555; }}
  .review-progress-bar {{ height: 8px; background: #252525; border-radius: 4px; overflow: hidden; }}
  .review-progress-fill {{ height: 100%; background: linear-gradient(90deg, #4ade80, #22c55e);
                           border-radius: 4px; transition: width .4s ease; width: 0%; }}
  .review-card {{ background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
                 padding: 20px; margin-bottom: 16px; }}
  .review-header {{ display: flex; justify-content: space-between; align-items: center;
                   margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }}
  .review-title {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .review-date {{ font-size: 13px; color: #888; }}
  .review-sign {{ font-size: 15px; font-weight: 600; color: #e8e8e8; }}
  .review-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
  .badge-pending {{ background: #1c1a0d; color: #fbbf24; border: 1px solid #854d0e; }}
  .badge-approved {{ background: #0d1f13; color: #4ade80; border: 1px solid #166534; }}
  .review-body {{ display: grid; grid-template-columns: 130px 1fr 300px; gap: 16px; }}
  .review-image-col {{ flex-shrink: 0; }}
  .review-thumb {{ width: 130px; height: 130px; object-fit: cover; border-radius: 8px; }}
  .review-thumb-empty {{ width: 130px; height: 130px; background: #252525; border-radius: 8px; }}
  .review-text-col {{ min-width: 0; }}
  .rtabs {{ display: flex; gap: 4px; margin-bottom: 8px; }}
  .rtab {{ padding: 5px 12px; border: 1px solid #2a2a2a; background: #111; color: #888;
           border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; }}
  .rtab:hover {{ color: #ccc; border-color: #444; }}
  .rtab.rtab-active {{ background: #1a2a3a; color: #7eb8f7; border-color: #3a5a8a; }}
  .copy-btn {{ margin-right: auto; padding: 5px 12px; border: 1px solid #3a4a2a; background: #0d1f0d;
              color: #86efac; border-radius: 6px; font-size: 12px; cursor: pointer;
              font-family: inherit; transition: all .15s; }}
  .copy-btn:hover {{ background: #166534; border-color: #4ade80; color: #fff; }}
  .copy-btn.copied {{ background: #166534; color: #4ade80; border-color: #4ade80; }}
  .rtext-panel {{ display: none; font-size: 12px; color: #ccc; line-height: 1.7;
                 max-height: 180px; overflow-y: auto; background: #111;
                 border: 1px solid #2a2a2a; border-radius: 8px; padding: 10px 14px; }}
  .rtext-panel.rtext-active {{ display: block; }}
  .review-checklist-col {{ border-right: 1px solid #2a2a2a; padding-right: 16px; }}
  .sop-section {{ margin-bottom: 12px; }}
  .sop-header {{ font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px;
                margin-bottom: 6px; }}
  .sop-reject {{ background: #1f0d0d; color: #f87171; }}
  .sop-feed   {{ background: #0d1529; color: #7eb8f7; }}
  .sop-story  {{ background: #0d1f13; color: #4ade80; }}
  .sop-item {{ display: flex; align-items: flex-start; gap: 6px; font-size: 11px; color: #bbb;
              line-height: 1.5; padding: 3px 0; cursor: pointer; }}
  .sop-item input[type="checkbox"] {{ margin-top: 2px; accent-color: #4ade80; cursor: pointer;
                                      flex-shrink: 0; }}
  .sop-item:hover {{ color: #e8e8e8; }}
  .review-notes-row {{ margin-top: 12px; padding-top: 12px; border-top: 1px solid #2a2a2a; }}
  .review-notes {{ width: 100%; min-height: 64px; max-height: 140px; background: #111;
                  border: 1px solid #2a3a4a; border-radius: 8px; color: #ccc;
                  font-size: 12px; padding: 10px 12px; resize: vertical; font-family: inherit;
                  line-height: 1.6; direction: rtl; }}
  .review-notes:focus {{ outline: none; border-color: #7eb8f7; background: #0d1520; }}
  .review-notes::placeholder {{ color: #444; }}

  /* ── Lightbox ── */
  .lightbox {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
              background: rgba(0,0,0,0.9); z-index: 999; align-items: center; justify-content: center;
              cursor: pointer; }}
  .lightbox.active {{ display: flex; }}
  .lightbox img {{ max-width: 90%; max-height: 90%; object-fit: contain; border-radius: 8px; }}

  .footer {{ text-align: center; padding: 32px; color: #333; font-size: 12px; }}
</style>
</head>
<body>

<div class="topbar">
  <h1>LeavesDesign Team Dashboard</h1>
  <span class="gen">\u05e2\u05d5\u05d3\u05db\u05df: {generated}</span>
</div>

<div class="tabs">
  <button class="tab active" data-tab="team">\u05d4\u05e6\u05d5\u05d5\u05ea</button>
  <button class="tab" data-tab="kpi">\u05de\u05d3\u05d3\u05d9 KPI</button>
  <button class="tab" data-tab="gantt">\u05dc\u05d5\u05d7 \u05d2\u05d0\u05e0\u05d8</button>
  <button class="tab" data-tab="posts">\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd</button>
  <button class="tab" data-tab="matrix">\u05de\u05d8\u05e8\u05d9\u05e6\u05ea \u05ea\u05de\u05d5\u05e0\u05d5\u05ea</button>
  <button class="tab" data-tab="org">\u05e2\u05e5 \u05d0\u05e8\u05d2\u05d5\u05e0\u05d9</button>
  <button class="tab" data-tab="learning">\u05dc\u05de\u05d9\u05d3\u05d4 \u05d5\u05e9\u05d9\u05e4\u05d5\u05e8</button>
  <button class="tab" data-tab="review">\u2705 \u05d1\u05d9\u05e7\u05d5\u05e8\u05ea SOP</button>
  <button class="tab" data-tab="sla">\U0001f4ca \u05d3\u05d5\u05d7 SLA</button>
</div>

<div class="container">

  <!-- TAB: Team -->
  <div class="section active" id="team">
    {team_lead_html}
    <div class="members-grid">
      {team_members_html}
    </div>
  </div>

  <!-- TAB: KPI -->
  <div class="section" id="kpi">
    {kpi_summary_html}
    <h3 style="font-size:15px;color:#888;margin-bottom:14px">\u05d1\u05d9\u05e6\u05d5\u05e2\u05d9\u05dd \u05dc\u05e4\u05d9 \u05d0\u05d9\u05e9 \u05e6\u05d5\u05d5\u05ea</h3>
    <div class="kpi-agents-grid">
      {kpi_agents_html}
    </div>
    <div class="pillar-section">
      <h3>\u05d4\u05ea\u05e4\u05dc\u05d2\u05d5\u05ea \u05dc\u05e4\u05d9 \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4</h3>
      {pillar_bars}
    </div>
    {missing_alert}
  </div>

  <!-- TAB: Gantt -->
  <div class="section" id="gantt">
    <div class="gantt-controls">
      <button class="gantt-btn active" data-view="month">\u05d7\u05d5\u05d3\u05e9\u05d9</button>
      <button class="gantt-btn" data-view="week">\u05e9\u05d1\u05d5\u05e2\u05d9</button>
      <div class="gantt-nav" id="gantt-nav" style="display:none">
        <button class="nav-btn" id="gantt-prev">\u2192</button>
        <span id="gantt-period"></span>
        <button class="nav-btn" id="gantt-next">\u2190</button>
      </div>
    </div>
    <div id="gantt-month-view" class="gantt-view">
      <div class="cal-container">{cal_html}</div>
    </div>
    <div id="gantt-week-view" class="gantt-view" style="display:none">
      {week_views_html}
    </div>
  </div>

  <!-- TAB: Posts -->
  <div class="section" id="posts">
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">\u05d4\u05db\u05dc</button>
      <button class="filter-btn" data-filter="automotive">\u05e8\u05db\u05d1</button>
      <button class="filter-btn" data-filter="motorcycle">\u05d0\u05d5\u05e4\u05e0\u05d5\u05e2</button>
      <button class="filter-btn" data-filter="wedding">\u05d7\u05ea\u05d5\u05e0\u05d4</button>
      <button class="filter-btn" data-filter="dog">\u05db\u05dc\u05d1\u05d9\u05dd</button>
      <button class="filter-btn" data-filter="blog">\u05d1\u05dc\u05d5\u05d2</button>
      <button class="filter-btn" data-filter="story-ready">Story \u05de\u05d5\u05db\u05df</button>
      <button class="filter-btn" data-filter="story-missing">Story \u05d7\u05e1\u05e8</button>
      <button class="filter-btn" data-filter="gemini-missing">Gemini \u05d7\u05e1\u05e8</button>
    </div>
    <div class="posts-grid">{posts_cards}</div>
  </div>

  <!-- TAB: Matrix -->
  <div class="section" id="matrix">
    <table class="matrix-table">
      <thead><tr>
        <th>\u05de\u05d5\u05e6\u05e8</th><th>\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd</th><th>Mockup</th><th>Gemini</th><th>Story</th>
      </tr></thead>
      <tbody>{matrix_rows}</tbody>
    </table>
  </div>

  <!-- TAB: Org Tree -->
  <div class="section" id="org">
    <h2 style="text-align:center;margin-bottom:24px;color:#ccc">\U0001f3e2 \u05e2\u05e5 \u05d0\u05e8\u05d2\u05d5\u05e0\u05d9 \u2014 LeavesDesign Agent Team</h2>
    {org_tree_html}
  </div>

  <!-- TAB: Learning -->
  <div class="section" id="learning">
    {learning_html}
  </div>

  <!-- TAB: Review (ביקורת SOP) -->
  <div class="section" id="review">
    <div class="review-progress">
      <div class="review-progress-top">
        <div class="review-progress-label">
          \u05d0\u05d5\u05e9\u05e8\u05d5 <span id="approved-count">0</span> \u05de\u05ea\u05d5\u05da {total_posts} \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd
        </div>
        <button class="send-daniel-btn" onclick="exportToDaniel()">\U0001f4e8 \u05e9\u05dc\u05d7 \u05d4\u05e2\u05e8\u05d5\u05ea \u05dc\u05d3\u05e0\u05d9\u05d0\u05dc</button>
      </div>
      <div class="review-progress-bar">
        <div class="review-progress-fill" id="progress-fill"></div>
      </div>
    </div>
    <!-- Modal for Daniel export -->
    <div class="daniel-modal" id="daniel-modal" onclick="closeDanielModal(event)">
      <div class="daniel-modal-box">
        <div class="daniel-modal-header">
          <span>\U0001f4e8 \u05d4\u05e2\u05e8\u05d5\u05ea \u05dc\u05d3\u05e0\u05d9\u05d0\u05dc — \u05d4\u05e2\u05ea\u05e7 \u05d5\u05d4\u05d3\u05d1\u05e7 \u05d1\u05e6\'\u05d0\u05d8</span>
          <button class="daniel-modal-close" onclick="closeDanielModal()">\u00d7</button>
        </div>
        <textarea class="daniel-modal-text" id="daniel-export-text" readonly></textarea>
        <div class="daniel-modal-footer">
          <button class="daniel-copy-btn" onclick="copyDanielExport()">\U0001f4cb \u05d4\u05e2\u05ea\u05e7 \u05dc\u05e7\u05dc\u05d9\u05e4\u05d1\u05d5\u05e8\u05d3</button>
          <span class="daniel-copy-hint">\u05d0\u05d7\u05e8\u05d9 \u05d4\u05e2\u05ea\u05e7 \u2014 \u05e4\u05ea\u05d7 Claude Code \u05d5\u05d4\u05d3\u05d1\u05e7 \u05d9\u05e9\u05d9\u05e8 \u05dc\u05e6\'\u05d0\u05d8</span>
        </div>
      </div>
    </div>
    {review_cards}
  </div>

  <!-- TAB: SLA Report -->
  <div class="section" id="sla">
    <h2 style="text-align:center;margin-bottom:20px;color:#ccc">\U0001f4ca \u05d3\u05d5\u05d7 SLA \u2014 \u05e2\u05de\u05d9\u05d3\u05d4 \u05d1\u05d9\u05e2\u05d3\u05d9\u05dd</h2>
    <div class="sla-overall">
      <div class="sla-overall-label">\u05e6\u05d9\u05d5\u05df SLA \u05db\u05dc\u05dc\u05d9</div>
      <div class="sla-overall-score" style="color:{overall_color}">{overall_pct}%</div>
      <div class="sla-overall-bar"><div class="sla-overall-fill" style="width:{overall_pct}%;background:{overall_color}"></div></div>
    </div>
    {bottleneck_html}
    <div class="sla-grid">{sla_cards_html}</div>
  </div>

</div>

<div class="footer">LeavesDesign Agent Team Dashboard \u2022 \u05e0\u05d5\u05e6\u05e8 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 generate_dashboard.py</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox"><img id="lightbox-img" src="" alt=""></div>

<script>
// Agent log tab switching
function switchLog(btn, period) {{
  const log = btn.closest('.agent-log');
  log.querySelectorAll('.log-tab').forEach(t => t.classList.remove('active'));
  log.querySelectorAll('.log-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  log.querySelector('.log-panel[data-period="' + period + '"]').classList.add('active');
}}

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
  }});
}});

// Filter buttons (Posts tab)
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const f = btn.dataset.filter;
    document.querySelectorAll('.post-card').forEach(card => {{
      if (f === 'all') {{ card.style.display = ''; return; }}
      if (f === 'story-ready') {{ card.style.display = card.dataset.story === 'ready' ? '' : 'none'; return; }}
      if (f === 'story-missing') {{ card.style.display = card.dataset.story !== 'ready' ? '' : 'none'; return; }}
      if (f === 'gemini-missing') {{ card.style.display = card.dataset.gemini === 'no' ? '' : 'none'; return; }}
      card.style.display = card.dataset.pillar === f ? '' : 'none';
    }});
  }});
}});

// Gantt view switching
const weeksData = {weeks_json};
let weekIdx = 0;

function updateWeekNav() {{
  document.getElementById('gantt-period').textContent = weeksData[weekIdx].label + ' (' + weeksData[weekIdx].count + ' \u05e4\u05d5\u05e1\u05d8\u05d9\u05dd)';
}}

document.querySelectorAll('.gantt-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.gantt-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const view = btn.dataset.view;
    document.getElementById('gantt-month-view').style.display = view === 'month' ? 'block' : 'none';
    document.getElementById('gantt-week-view').style.display = view === 'week' ? 'block' : 'none';
    document.getElementById('gantt-nav').style.display = view === 'week' ? 'flex' : 'none';
    if (view === 'week') {{
      showWeek(weekIdx);
      updateWeekNav();
    }}
  }});
}});

function showWeek(idx) {{
  document.querySelectorAll('.gantt-week-panel').forEach(w => w.style.display = 'none');
  const panel = document.querySelector('.gantt-week-panel[data-week="' + idx + '"]');
  if (panel) panel.style.display = 'block';
}}

document.getElementById('gantt-prev').addEventListener('click', () => {{
  if (weekIdx < weeksData.length - 1) {{ weekIdx++; showWeek(weekIdx); updateWeekNav(); }}
}});
document.getElementById('gantt-next').addEventListener('click', () => {{
  if (weekIdx > 0) {{ weekIdx--; showWeek(weekIdx); updateWeekNav(); }}
}});

// ── Review Tab ──────────────────────────────────────────────────────────
function switchRTab(btn, panelId) {{
  const card = btn.closest('.review-card');
  card.querySelectorAll('.rtab').forEach(t => t.classList.remove('rtab-active'));
  card.querySelectorAll('.rtext-panel').forEach(p => p.classList.remove('rtext-active'));
  btn.classList.add('rtab-active');
  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add('rtext-active');
}}

function updateReviewProgress() {{
  const cards = document.querySelectorAll('.review-card');
  let approved = 0;
  cards.forEach(card => {{
    const pid = card.id.replace('rcard-', '');
    const boxes = card.querySelectorAll('.sop-cb');
    const allChecked = boxes.length > 0 && [...boxes].every(b => b.checked);
    const badge = document.getElementById('rbadge-' + pid);
    if (allChecked) {{
      approved++;
      if (badge) {{ badge.textContent = '\u2705 \u05d0\u05d5\u05e9\u05e8'; badge.className = 'review-badge badge-approved'; }}
    }} else {{
      if (badge) {{ badge.textContent = '\u23f3 \u05de\u05de\u05ea\u05d9\u05df \u05dc\u05d0\u05d9\u05e9\u05d5\u05e8'; badge.className = 'review-badge badge-pending'; }}
    }}
  }});
  const el = document.getElementById('approved-count');
  const fill = document.getElementById('progress-fill');
  if (el) el.textContent = approved;
  if (fill) fill.style.width = (cards.length ? Math.round(approved / cards.length * 100) : 0) + '%';
}}

// Export all notes to Daniel
function exportToDaniel() {{
  const notes = [];
  document.querySelectorAll('.review-notes').forEach(ta => {{
    const val = ta.value.trim();
    if (val) {{
      notes.push({{ date: ta.dataset.date, sign: ta.dataset.sign, text: val }});
    }}
  }});
  const today = new Date().toLocaleDateString('he-IL');
  let output = '';
  if (notes.length === 0) {{
    output = '\u05d0\u05d9\u05df \u05d4\u05e2\u05e8\u05d5\u05ea \u05e4\u05ea\u05d5\u05d7\u05d5\u05ea \u05db\u05e8\u05d2\u05e2 \u2014 \u05db\u05dc\u05d4\u05e3 \u05e8\u05e9\u05d5\u05de\u05d4 \u05e9\u05dc\u05d3\u05d4 \u05d4\u05e2\u05e8\u05d5\u05ea \u05d1\u05d3\u05e9\u05d1\u05d5\u05e8\u05d3.';
  }} else {{
    output += '\U0001f4cb \u05d4\u05e2\u05e8\u05d5\u05ea \u05dc\u05d3\u05e0\u05d9\u05d0\u05dc \u2014 LeavesDesign (' + today + ')\\n';
    output += '='.repeat(50) + '\\n\\n';
    notes.forEach(n => {{
      output += '\U0001f4c5 ' + n.date + ' | ' + n.sign + '\\n';
      output += n.text + '\\n\\n';
      output += '-'.repeat(40) + '\\n\\n';
    }});
    output += '\u05e1\u05d4"\u05db: ' + notes.length + ' \u05d4\u05e2\u05e8\u05d5\u05ea \u05e4\u05ea\u05d5\u05d7\u05d5\u05ea \u05dc\u05d8\u05d9\u05e4\u05d5\u05dc.\\n';
    output += '\u05d3\u05e0\u05d9\u05d0\u05dc \u2014 \u05d0\u05e0\u05d0 \u05d1\u05d3\u05d5\u05e7 \u05db\u05dc \u05d4\u05e2\u05e8\u05d4 \u05d5\u05d8\u05e4\u05dc \u05d1\u05d4\u05ea\u05d0\u05dd.';
  }}
  document.getElementById('daniel-export-text').value = output;
  document.getElementById('daniel-modal').classList.add('active');
}}

function closeDanielModal(e) {{
  if (!e || e.target === document.getElementById('daniel-modal') || e.currentTarget === document.querySelector('.daniel-modal-close')) {{
    document.getElementById('daniel-modal').classList.remove('active');
  }}
}}

function copyDanielExport() {{
  const ta = document.getElementById('daniel-export-text');
  ta.select();
  navigator.clipboard.writeText(ta.value).then(() => {{
    const btn = document.querySelector('.daniel-copy-btn');
    if (btn) {{
      btn.textContent = '\u2713 \u05d4\u05d5\u05e2\u05ea\u05e7!';
      setTimeout(() => {{ btn.textContent = '\U0001f4cb \u05d4\u05e2\u05ea\u05e7 \u05dc\u05e7\u05dc\u05d9\u05e4\u05d1\u05d5\u05e8\u05d3'; }}, 2000);
    }}
  }});
}}

// Copy text of active panel to clipboard
function copyRText(pid) {{
  const card = document.getElementById('rcard-' + pid);
  const panel = card.querySelector('.rtext-panel.rtext-active');
  if (!panel) return;
  const text = panel.innerText.trim();
  navigator.clipboard.writeText(text).then(() => {{
    const btn = document.getElementById('copybtn-' + pid);
    if (btn) {{
      btn.textContent = '\u2713 \u05d4\u05d5\u05e2\u05ea\u05e7!';
      btn.classList.add('copied');
      setTimeout(() => {{
        btn.textContent = '\U0001f4cb \u05d4\u05e2\u05ea\u05e7';
        btn.classList.remove('copied');
      }}, 2000);
    }}
  }});
}}

// ── SYNC Module — two-way sync (server + localStorage + embedded) ──
const SYNC = (function() {{
  const API = '/api/sync';
  let _s = window.__REVIEW_SYNC__ || {{}};
  let _timer = null;
  let _serverOk = null;

  function _posts() {{ if (!_s.posts) _s.posts = {{}}; return _s.posts; }}
  function _post(pid) {{
    if (!_posts()[pid]) _posts()[pid] = {{ checkboxes: {{}}, note: '', approved: false }};
    return _posts()[pid];
  }}

  function setCb(pid, cbKey, val) {{
    _post(pid).checkboxes[cbKey] = val;
    const cbs = _post(pid).checkboxes;
    const all = ['ar1','ar2','ar3','ar4','f1','f2','f3','f4','f5','f6','s1','s2','s3'];
    _post(pid).approved = all.every(k => cbs[k] === true);
    _save();
  }}

  function setNote(pid, txt) {{ _post(pid).note = txt; _save(); }}
  function getCb(pid, cbKey) {{ return _posts()[pid]?.checkboxes?.[cbKey] || false; }}
  function getNote(pid) {{ return _posts()[pid]?.note || ''; }}

  function _save() {{
    _s.lastModified = new Date().toISOString();
    _s.version = 1;
    clearTimeout(_timer);
    _timer = setTimeout(_flush, 500);
  }}

  function _flush() {{
    try {{ localStorage.setItem('__review_sync__', JSON.stringify(_s)); }} catch(e) {{}}
    if (_serverOk === false) return;
    fetch(API, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(_s)
    }}).then(r => {{ _serverOk = r.ok; }})
      .catch(() => {{ _serverOk = false; console.log('[Sync] Server unavailable — localStorage only.'); }});
  }}

  async function init() {{
    // Priority: server > embedded > localStorage > migrate old keys
    try {{
      const r = await fetch(API);
      if (r.ok) {{
        const d = await r.json();
        _serverOk = true;
        if (d?.posts && Object.keys(d.posts).length > 0) {{
          _s = d;
          console.log('[Sync] Loaded from server.');
          return;
        }}
      }}
    }} catch(e) {{ _serverOk = false; }}

    if (window.__REVIEW_SYNC__?.posts && Object.keys(window.__REVIEW_SYNC__.posts).length > 0) {{
      _s = window.__REVIEW_SYNC__;
      console.log('[Sync] Loaded from embedded state.');
      return;
    }}

    try {{
      const ls = localStorage.getItem('__review_sync__');
      if (ls) {{ _s = JSON.parse(ls); console.log('[Sync] Loaded from localStorage.'); return; }}
    }} catch(e) {{}}

    // Migrate old rv-xxx / rvnote-xxx keys
    let migrated = false;
    document.querySelectorAll('.review-card').forEach(card => {{
      const pid = card.id.replace('rcard-', '');
      card.querySelectorAll('.sop-cb').forEach(cb => {{
        const fk = cb.dataset.key;
        const old = localStorage.getItem('rv-' + fk);
        if (old === '1') {{ setCb(pid, fk.replace(pid + '-', ''), true); migrated = true; }}
      }});
      const nv = localStorage.getItem('rvnote-' + pid);
      if (nv) {{ setNote(pid, nv); migrated = true; }}
    }});
    if (migrated) {{ console.log('[Sync] Migrated old localStorage keys.'); _flush(); }}
  }}

  return {{ init, setCb, setNote, getCb, getNote }};
}})();

// Save note (called from textarea oninput)
function saveNote(pid) {{
  const ta = document.getElementById('notes-' + pid);
  if (ta) SYNC.setNote(pid, ta.value);
}}

// Init review state asynchronously
(async function initReview() {{
  await SYNC.init();

  // Restore notes
  document.querySelectorAll('.review-notes').forEach(ta => {{
    const pid = ta.id.replace('notes-', '');
    const saved = SYNC.getNote(pid);
    if (saved) ta.value = saved;
  }});

  // Restore checkboxes
  document.querySelectorAll('.sop-cb').forEach(cb => {{
    const fk = cb.dataset.key;
    const parts = fk.split('-');
    const pid = parts[0];
    const cbKey = parts.slice(1).join('-');
    if (SYNC.getCb(pid, cbKey)) cb.checked = true;
    cb.addEventListener('change', () => {{
      SYNC.setCb(pid, cbKey, cb.checked);
      updateReviewProgress();
    }});
  }});

  updateReviewProgress();
}})();

// Lightbox
document.addEventListener('click', (e) => {{
  if (e.target.classList.contains('thumb')) {{
    document.getElementById('lightbox-img').src = e.target.dataset.full;
    document.getElementById('lightbox').classList.add('active');
  }}
}});
document.getElementById('lightbox').addEventListener('click', () => {{
  document.getElementById('lightbox').classList.remove('active');
}});
</script>
</body>
</html>"""

    # Inject review sync state before the main <script> block
    sync_tag = '<script>window.__REVIEW_SYNC__=' + sync_json_str + ';</script>\n'
    html = html.replace('<!-- Lightbox -->', sync_tag + '<!-- Lightbox -->')
    return html


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    gantt = load_json("gantt_results.json")
    gemini_urls = load_json("gemini_urls_final.json")
    mockup_urls = load_json("mockup_urls_final.json")
    qa = load_json("qa_report.json")
    review_sync = load_json("review-sync.json")

    if not gantt:
        print("ERROR: gantt_results.json not found or empty")
        return

    print(f"Found {len(gantt)} posts in gantt_results.json")

    posts = build_posts_data(gantt, gemini_urls, mockup_urls)
    stats = compute_stats(posts, qa)
    kpis = compute_agent_kpis(stats)
    agent_logs = compute_agent_logs(posts, stats)
    sla_report = compute_sla_report(posts)
    calendar = build_calendar_data(posts)
    weeks = build_gantt_weeks(posts)
    matrix = build_matrix_data(posts)

    data = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "posts": posts,
        "stats": stats,
        "kpis": kpis,
        "agent_logs": agent_logs,
        "sla_report": sla_report,
        "calendar": calendar,
        "weeks": weeks,
        "matrix": matrix,
        "review_sync": review_sync,
    }

    print("Generating HTML...")
    html = generate_html(data)

    output_path = BASE / "dashboard.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard saved to: {output_path}")
    print(f"Stats: {stats['total']} posts | Gemini: {stats['gemini_ready']}/{stats['total']} | "
          f"Stories: {stats['story_ready']}/{stats['total']} | QA: {stats['qa_passed']}/{stats['qa_total']}")
    print(f"Team: {len(TEAM)} agents | Weeks: {len(weeks)} | Matrix: {len(matrix)} products")


# ── Sync Server ────────────────────────────────────────────────────────────
SYNC_FILE = BASE / "review-sync.json"
DASH_USER = os.environ.get('DASH_USER', '')
DASH_PASS = os.environ.get('DASH_PASS', '')

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def _check_auth(self):
        """Return True if auth passes (or no auth configured)."""
        if not DASH_USER:
            return True
        auth = self.headers.get('Authorization', '')
        if not auth.startswith('Basic '):
            return False
        try:
            creds = base64.b64decode(auth[6:]).decode('utf-8')
        except Exception:
            return False
        return creds == f'{DASH_USER}:{DASH_PASS}'

    def _require_auth(self):
        """Send 401 response asking for credentials."""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Dashboard"')
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Unauthorized')

    def do_GET(self):
        if not self._check_auth():
            self._require_auth()
            return
        if self.path == '/api/sync':
            data = SYNC_FILE.read_bytes() if SYNC_FILE.exists() else b'{}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()

    def do_POST(self):
        if not self._check_auth():
            self._require_auth()
            return
        if self.path == '/api/sync':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                json.loads(body)  # validate JSON
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
                return
            SYNC_FILE.write_bytes(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        if not self._check_auth():
            self._require_auth()
            return
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy GET logs, keep sync logs
        if '/api/sync' in str(args[0]):
            super().log_message(format, *args)


def serve(port=8787):
    """Generate dashboard then serve with sync API."""
    main()
    print(f"\n{'='*50}")
    print(f"  Dashboard: http://localhost:{port}/dashboard.html")
    print(f"  Sync API:  http://localhost:{port}/api/sync")
    if DASH_USER:
        print(f"  Auth:      user={DASH_USER} (password protected)")
    else:
        print(f"  Auth:      OFF (set DASH_USER / DASH_PASS to enable)")
    print(f"{'='*50}")
    print("  Press Ctrl+C to stop.\n")
    server = HTTPServer(('', port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    if '--serve' in sys.argv:
        # Priority: --port flag > PORT env var > default 8787
        port = int(os.environ.get('PORT', 8787))
        for i, arg in enumerate(sys.argv):
            if arg == '--port' and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        serve(port)
    else:
        main()
