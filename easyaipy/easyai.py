from google import genai
from easyaipy.utils import prepare_image, process_openai_image
import json
import re
import time
from openai import OpenAI
from typing import Dict, Any, Optional, Tuple


def modify_prompt(base_prompt: str, schema: Dict[str, type]) -> str:
    """
    Appends schema instructions to the prompt.

    Args:
        base_prompt (str): The base text prompt.
        schema (dict): Dictionary mapping expected keys to their types.

    Returns:
        str: Modified prompt with schema instructions.
    """
    if not schema:
        return base_prompt

    schema_desc = ", ".join(f"'{k}': {v.__name__}" for k, v in schema.items())
    return (
        f"""
        {base_prompt}\n\n
        Respond in JSON format with this structure:\n
        {{{schema_desc}}}\n
        Ensure types match exactly and return only a JSON code block.  
        Always enclose the JSON elements in double quotes!
        """
    )


def extract_json(response_text: str) -> Dict[str, Any]:
    """
    Extracts JSON content from response text.

    Args:
        response_text (str): The response text containing JSON data.

    Returns:
        dict: Extracted JSON data.
    """
    try:
        json_text = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL) or \
                    re.search(r"(\{.*?\})", response_text, re.DOTALL)
        return json.loads(json_text.group(1)) if json_text else {}
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"JSON extraction failed: {e}")
        return {}


def validate_schema(output: Dict[str, Any], schema: Dict[str, type]) -> bool:
    """
    Validates the output against the expected schema.

    Args:
        output (dict): The extracted JSON output.
        schema (dict): Expected schema with key-type pairs.

    Returns:
        bool: True if output matches schema, else False.
    """
    return all(isinstance(output.get(key), expected_type) for key, expected_type in schema.items())


def call_openai(prompt: str, model: str, max_tokens: int, api_key: str, max_retries: int) -> Tuple[
    Optional[Any], Dict[str, Any]]:
    """
    Calls the OpenAI API with retries and schema validation.

    Args:
        prompt (str): The input prompt.
        model (str): OpenAI model to use.
        max_tokens (int): Maximum number of tokens in response.
        api_key (str): OpenAI API key.
        max_retries (int): Number of retries for the API call.

    Returns:
        tuple: OpenAI response object and extracted JSON data.
    """
    client = OpenAI(api_key=api_key)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            response_text = response.choices[0].message.content
            parsed_output = extract_json(response_text)
            response.choices[0].data_dict = dict(parsed_output)
            return response, parsed_output
        except Exception as e:
            print(f"OpenAI Retry {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(1)

    return response, {}


def call_gemini(prompt: list, model: str, api_key: str, max_retries: int) -> Dict[str, Any]:
    """
    Calls the Gemini API with retries and schema validation.

    Args:
        prompt (list): The input prompt formatted as a list.
        model (str): Gemini model to use.
        api_key (str): Gemini API key.
        max_retries (int): Number of retries for the API call.

    Returns:
        dict: Extracted JSON data.
    """
    client = genai.Client(api_key=api_key)

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            response_text = response.text.strip()
            return extract_json(response_text)
        except Exception as e:
            print(f"Gemini Retry {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(1)

    return {}


def gemini_easy_prompt(prompt: str, image: Optional[str] = None, model: str = "gemini-2.0-flash",
                       output_schema: Optional[Dict[str, type]] = None,
                       max_retries: int = 3, api_key: str = "") -> Dict[str, Any]:
    """
    Wrapper for the Gemini API with image support and schema validation.

    Args:
        prompt (str): The input prompt.
        image (str, optional): Image to be processed alongside text.
        model (str): Gemini model to use.
        output_schema (dict, optional): Expected schema for response.
        max_retries (int): Maximum retries for API call.
        api_key (str): API key for authentication.

    Returns:
        dict: Parsed response data.
    """
    prompt = modify_prompt(prompt, output_schema)
    prompt = [prompt]

    if image:
        prompt.append(prepare_image(image))

    response_data = call_gemini(prompt, model, api_key, max_retries)

    if output_schema and not validate_schema(response_data, output_schema):
        raise ValueError("Invalid output format")

    return response_data


def openai_easy_prompt(prompt: str, image: Optional[str] = None, model: str = "gpt-4o-mini",
                       output_schema: Optional[Dict[str, type]] = None,
                       max_retries: int = 3, api_key: str = "", max_tokens: int = 2000) -> Dict[str, Any]:
    """
    Wrapper for the OpenAI API with image support and schema validation.

    Args:
        prompt (str): The input prompt.
        image (str, optional): Image to be processed alongside text.
        model (str): OpenAI model to use.
        output_schema (dict, optional): Expected schema for response.
        max_retries (int): Maximum retries for API call.
        api_key (str): API key for authentication.
        max_tokens (int): Maximum number of tokens in response.

    Returns:
        dict: Parsed response data.
    """
    prompt = modify_prompt(prompt, output_schema)

    if image:
        prompt = process_openai_image(image, prompt)

    response_obj, response_data = call_openai(prompt, model, max_tokens, api_key, max_retries)

    if output_schema and not validate_schema(response_data, output_schema):
        raise ValueError("Invalid output format")

    return response_obj
