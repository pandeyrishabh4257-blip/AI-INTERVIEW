"""Answer evaluation using LLM-compatible scoring with local heuristic fallback."""
from __future__ import annotations

from typing import Dict

from config import OPENAI_API_KEY


POSITIVE_MARKERS = ["impact", "result", "team", "scalable", "optimized", "improved", "delivered"]


def _heuristic_eval(answer: str, question: str) -> Dict[str, object]:
    answer_l = answer.lower()
    marker_hits = sum(1 for m in POSITIVE_MARKERS if m in answer_l)
    word_count = len(answer.split())
    score = min(10, max(3, (word_count // 20) + marker_hits + 2))
    strengths = [
        "Provides structured response" if word_count > 40 else "Concise response",
        "Includes business/technical impact" if marker_hits > 0 else "Directly addresses the question",
    ]
    weaknesses = [
        "Could provide more concrete metrics" if "%" not in answer and "increase" not in answer_l else "Minor details could be clearer"
    ]
    return {
        "question": question,
        "score": int(score),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": "Good direction. Add measurable outcomes and deeper technical detail for stronger answers.",
    }


def evaluate_answer(question: str, answer: str) -> Dict[str, object]:
    if not OPENAI_API_KEY:
        return _heuristic_eval(answer, question)

    try:
        from openai import OpenAI
        import json

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "Evaluate the candidate answer and respond as JSON with keys: score (0-10), "
            "strengths (array), weaknesses (array), feedback."
            f"\nQuestion: {question}\nAnswer: {answer}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        payload["question"] = question
        return payload
    except Exception:
        return _heuristic_eval(answer, question)
