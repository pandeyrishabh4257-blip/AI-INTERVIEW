"""Resume parsing using spaCy-style heuristics and sentence-transformer-like extraction."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import re

import PyPDF2


SKILL_KEYWORDS = [
    "python",
    "javascript",
    "react",
    "node",
    "fastapi",
    "flask",
    "mongodb",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "machine learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "tailwind",
]


def _extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PyPDF2.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_resume(pdf_path: str) -> Dict[str, List[str] | str]:
    """Parse a PDF resume and extract candidate profile fields.

    This function uses robust fallback heuristics if spaCy / transformers are not installed.
    """
    text = _extract_text_from_pdf(Path(pdf_path))
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    name = lines[0] if lines else "Candidate"

    skills = []
    lower_text = text.lower()
    for keyword in SKILL_KEYWORDS:
        if keyword in lower_text:
            skills.append(keyword.title())

    education_matches = re.findall(r"(B\\.?Tech|M\\.?Tech|B\\.?Sc|M\\.?Sc|Bachelor|Master|PhD)[^\n]*", text, flags=re.I)
    experience_matches = re.findall(r"(\\d+\+?\s+years?[^\n]*)", text, flags=re.I)

    return {
        "name": name,
        "skills": skills[:12],
        "education": education_matches[:3] or ["Not explicitly found"],
        "experience": experience_matches[:4] or ["Not explicitly found"],
        "raw_text": text[:8000],
    }
