import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def generate_story(outline: list) -> list:
    """
    Generates exactly 5 structured comic story panels from the outline.
    """

    if client is None:
        raise ValueError("GEMINI_API_KEY is not configured.")

    formatted_outline = "\n\n".join(
        [
            f"""PANEL {i + 1}
Title: {item.get("title", "")}
Scene: {item.get("scene_description", "")}
Image Prompt: {item.get("image_prompt", "")}"""
            for i, item in enumerate(outline)
        ]
    )

    prompt = f"""
You are a professional comic book writer.

Create a complete 5-panel comic story from the following panel outline.

PANEL OUTLINE:
{formatted_outline}

STRICT REQUIREMENTS:
- Return EXACTLY 5 panels.
- Panels must be numbered 1 through 5.
- Each panel must correspond to the matching panel in the outline.
- Each panel must contain narration.
- Each panel should contain character dialogue where appropriate.
- Maintain character and story continuity.
- Keep the story engaging and concise.

Return ONLY valid JSON.
Do NOT use Markdown.
Do NOT use ```json.
Do NOT include any explanation outside the JSON.

Required format:

[
    {{
        "panel": 1,
        "story": "Narration and dialogue for panel 1."
    }},
    {{
        "panel": 2,
        "story": "Narration and dialogue for panel 2."
    }},
    {{
        "panel": 3,
        "story": "Narration and dialogue for panel 3."
    }},
    {{
        "panel": 4,
        "story": "Narration and dialogue for panel 4."
    }},
    {{
        "panel": 5,
        "story": "Narration and dialogue for panel 5."
    }}
]
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Gemini returned no text.")

        output_text = response.text.strip()

        print("\n🔥 RAW GEMINI STORY RESPONSE 🔥\n")
        print(output_text)

        # Remove Markdown fences if Gemini ignores the instruction.
        if output_text.startswith("```json"):
            output_text = output_text[len("```json"):].strip()

        if output_text.startswith("```"):
            output_text = output_text[3:].strip()

        if output_text.endswith("```"):
            output_text = output_text[:-3].strip()

        story_data = json.loads(output_text)

        if not isinstance(story_data, list):
            raise ValueError("Gemini story response is not a list.")

        if len(story_data) != 5:
            raise ValueError(
                f"Expected exactly 5 story panels, "
                f"but Gemini returned {len(story_data)}."
            )

        for index, panel in enumerate(story_data, start=1):
            if (
                not isinstance(panel, dict)
                or panel.get("panel") != index
                or not isinstance(panel.get("story"), str)
                or not panel["story"].strip()
            ):
                raise ValueError(
                    f"Invalid story panel {index}: {panel}"
                )

        return story_data

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        ) from e

    except Exception as e:
        raise ValueError(
            f"Error generating story: {e}"
        ) from e