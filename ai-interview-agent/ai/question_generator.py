"""Question generation via LLM (OpenAI compatible) with deterministic fallback."""
from __future__ import annotations

from typing import Dict, List

from config import OPENAI_API_KEY


def _fallback_questions(skills: List[str]) -> Dict[str, List[str]]:
    primary = skills[0] if skills else "your core technical domain"
    hr = [
        "Tell me about yourself and what motivates you in your career.",
        "Describe a challenging professional situation and how you handled it.",
        "How do you prioritize tasks when working under tight deadlines?",
        "What kind of work environment helps you perform your best?",
        "Where do you see your career growth in the next 3 years?",
    ]
    technical = [
        f"Can you explain a project where you used {primary}?",
        "How do you ensure code quality in your development workflow?",
        "Describe your debugging approach for a production issue.",
        "How do you design scalable backend services?",
        "What trade-offs do you consider when selecting a tech stack?",
    ]
    follow_ups = [
        "Can you provide a concrete example?",
        "What did you learn from that experience?",
        "How would you improve the outcome if you did it again?",
    ]
    return {"hr_questions": hr, "technical_questions": technical, "follow_ups": follow_ups}


def generate_questions(resume_data: Dict[str, object]) -> Dict[str, List[str]]:
    """Create interview questions based on extracted skills.

    Uses an LLM when OPENAI_API_KEY is available, otherwise returns quality fallback questions.
    """
    skills = resume_data.get("skills", []) if isinstance(resume_data.get("skills"), list) else []

    if not OPENAI_API_KEY:
        return _fallback_questions(skills)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "Generate JSON with keys hr_questions (5), technical_questions (5), follow_ups (3) "
            f"for a candidate with skills: {', '.join(skills) or 'general software development'}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        import json

        return json.loads(response.choices[0].message.content or "{}")
    except Exception:
        return _fallback_questions(skills)
