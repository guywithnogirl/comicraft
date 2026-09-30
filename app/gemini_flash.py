import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def generate_outline(user_prompt: str) -> list:
    """
    Generates an exactly 5-panel comic layout based on the user's story idea
    using Gemini.

    Args:
        user_prompt (str): The user's comic idea.

    Returns:
        list: A list of exactly 5 dictionaries, one for each panel.
    """

    if client is None:
        return [{"error": "GEMINI_API_KEY is not configured."}]

    prompt = f"""
You are a professional AI comic planner.

Create a complete 5-panel comic based on the story idea below.

STORY:
"{user_prompt}"

IMPORTANT REQUIREMENTS:
- You MUST return EXACTLY 5 panels.
- The panels MUST be numbered 1, 2, 3, 4, and 5.
- Each panel must advance the story.
- Maintain character, setting, and visual continuity between panels.
- Each panel must have a unique scene.
- Each panel must contain an image prompt suitable for an AI image generator.

Each JSON object MUST contain:
- "panel": integer
- "title": string
- "scene_description": string
- "image_prompt": string

Respond ONLY with a valid JSON array.
Do NOT include markdown.
Do NOT include ```json.
Do NOT return fewer or more than 5 panels.

The required structure is:

[
    {{
        "panel": 1,
        "title": "Opening",
        "scene_description": "The story begins...",
        "image_prompt": "Detailed visual description..."
    }},
    {{
        "panel": 2,
        "title": "Development",
        "scene_description": "The story continues...",
        "image_prompt": "Detailed visual description..."
    }},
    {{
        "panel": 3,
        "title": "Conflict",
        "scene_description": "The main conflict appears...",
        "image_prompt": "Detailed visual description..."
    }},
    {{
        "panel": 4,
        "title": "Climax",
        "scene_description": "The situation reaches its peak...",
        "image_prompt": "Detailed visual description..."
    }},
    {{
        "panel": 5,
        "title": "Resolution",
        "scene_description": "The story concludes...",
        "image_prompt": "Detailed visual description..."
    }}
]
"""

    output_text = ""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Received empty response from Gemini.")

        output_text = response.text.strip()

        print("\n🔥 RAW GEMINI RESPONSE 🔥\n", output_text)

        # Remove markdown formatting if Gemini adds it despite the instruction.
        if output_text.startswith("```json"):
            output_text = output_text[len("```json"):].strip()

        if output_text.endswith("```"):
            output_text = output_text[:-3].strip()

        panel_data = json.loads(output_text)

        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        if len(panel_data) != 5:
            raise ValueError(
                f"Expected exactly 5 panels, but Gemini returned {len(panel_data)}."
            )

        for index, panel in enumerate(panel_data, start=1):
            if (
                not isinstance(panel, dict)
                or panel.get("panel") != index
                or not all(
                    key in panel
                    for key in (
                        "panel",
                        "title",
                        "scene_description",
                        "image_prompt",
                    )
                )
            ):
                raise ValueError(f"Invalid panel {index}: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("❌ Full Text Received:\n", output_text)
        return [{"error": f"JSON parsing failed: {str(e)}"}]

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return [{"error": f"Generation failed: {str(e)}"}]
