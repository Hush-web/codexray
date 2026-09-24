import os
from pathlib import Path
from openai import OpenAI

MODEL = os.getenv("CODEXRAY_MODEL", "openai/gpt-oss-120b")


def get_ai_summary(prompt: str) -> str:
    """Send a prompt to Groq and return the AI's response."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not set. Run: export GROQ_API_KEY='your_key'"

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def build_prompt(folder_path: str, files_list: list, max_files: int = 5) -> str:
    """
    Build a prompt for the AI from the top N files in the folder.
    Returns a string ready to send to get_ai_summary().
    """
    folder = Path(folder_path)

    top = sorted(files_list, key=lambda f: f["lines"], reverse=True)[:max_files]

    parts = []
    for entry in top:
        file_path = folder / entry["path"]
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            if len(content) > 4000:
                content = content[:4000] + "\n... (truncated)"

            parts.append(f"### {entry['path']}\n```\n{content}\n```")
        except Exception:
            continue

    context = "\n\n".join(parts)

    prompt = f"""You are analyzing a Python codebase.

Here are the {len(parts)} largest files:

{context}

In 3-5 sentences, summarize what this codebase does. Focus on:
- What problem it solves
- Its main components
- How they fit together

Be concise and concrete. No fluff.
"""
    return prompt