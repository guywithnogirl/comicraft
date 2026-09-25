import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY=os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)



def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini 1.5 Pro.

    Args:
        outline (list): A list of strings representing each comic panel's idea.

    Returns:
        str: The generated comic story text or an error message.
    """

    # Format the panel outline as a numbered list for clarity
    formatted_outline = "\n".join(
        [f"{i+1}. {item}" for i, item in enumerate(outline)]
    )

    # Construct the prompt
    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
- Include narration and clearly marked character lines.
- Keep each panel self-contained but part of a cohesive story.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-pro",
            contents=prompt
        )
        if response.text is None:
            raise ValueError("Gemini returned no text")

        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"