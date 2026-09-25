import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea.

    Returns:
        list: A list of dictionaries, one for each panel.
    """

    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:

[
    {{
        "panel": 1,
        "title": "Title here",
        "scene_description": "Scene description here",
        "image_prompt": "Image prompt for Stable Diffusion"
    }}
]
"""

    output_text = ""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        output_text = response.text

        if output_text is None:
            raise ValueError("Received empty response from Gemini.")

        output_text = output_text.strip()

        print("\n🔥 RAW GEMINI RESPONSE 🔥\n", output_text)

        # Remove any markdown formatting if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "").replace("```", "").strip()

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if (
                not isinstance(panel, dict)
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
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("❌ Full Text Received:\n", output_text)
        return [{"error": f"JSON parsing failed: {str(e)}"}]

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return [{"error": f"Generation failed: {str(e)}"}]