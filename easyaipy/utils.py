import base64
import os

import PIL.Image
from google.genai import types
import requests
import validators


def process_openai_image(image: str, prompt: str) -> list:
    """
    Processes an image for OpenAI API usage.

    Parameters:
        image (str): URL or local file path of the image.
        prompt (str): Text prompt to be used with the image.

    Returns:
        list: Formatted input containing text and image data.
    """
    try:
        if image:
            if not validators.url(image):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"File not found: {image}")

                with open(image, "rb") as image_file:
                    image_bytes = image_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")

                extension = os.path.splitext(image)[-1].lstrip('.').lower()
                if not extension:
                    raise ValueError("Invalid file extension")

                image = f"data:image/{extension};base64,{base64_image}"

            prompt = [
                {"type": "text", "text": str(prompt)},
                {"type": "image_url", "image_url": {"url": image}},
            ]
            return prompt
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return prompt


def prepare_image(image_source: str):
    """
    Prepares an image from either a URL or a local file for use with the Gemini API.

    Parameters:
        image_source (str): URL or local file path of the image.

    Returns:
        types.Part: Gemini API compatible image part.

    Raises:
        ValueError: If the image cannot be retrieved or is invalid.
    """
    if validators.url(image_source):
        # Handle URL
        response = requests.get(image_source)
        if response.status_code == 200:
            mime_type = response.headers.get("Content-Type", "image/jpeg")
            return types.Part.from_bytes(data=response.content, mime_type=mime_type)
        else:
            raise ValueError("Failed to fetch image from URL")
    else:
        # Handle local file
        try:
            image = PIL.Image.open(image_source)
            return image
        except Exception as e:
            raise ValueError(f"Error processing local image: {e}")
