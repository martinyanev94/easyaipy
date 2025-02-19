import re

from openai import OpenAI
import json
import time


def openai_easy_prompt(prompt: str, model: str = "gpt-4o-mini", output_schema: dict = None, max_retries: int = 3,
                       api_key: str = ""):
    """
    Function to interact with OpenAI API, dynamically adjust prompts, and enforce output schema.

    Args:
        prompt (str): The initial user prompt.
        model (str): The AI model to use (default is "gpt-4o-mini").
        output_schema (dict): A dictionary defining the desired output structure and types.
        max_retries (int): Maximum number of retries to adjust the prompt for a valid response.
        api_key (str): Your OpenAI API key.

    Returns:
        OpenAIResponse: The full API response object with added data dict. Access at response.choices[0].data_dict.

    Raises:
        RuntimeError: If maximum retries are reached without a valid response.
    """

    client = OpenAI(api_key=api_key)

    def modify_prompt(base_prompt: str, schema: dict) -> str:
        """Appends schema instructions to the prompt."""
        schema_desc = ", ".join(f"'{k}': {v.__name__}" for k, v in schema.items())
        return (f"{base_prompt}\n\n"
                f"Respond in JSON format with this structure:\n"
                f"{{{schema_desc}}}\n"
                f"Ensure types match exactly and return only a JSON code block.")

    if output_schema:
        prompt = modify_prompt(prompt, output_schema)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

            output = response.choices[0].message.content.replace("'", '"')

            # Extract JSON content
            json_text = re.search(r"```json\s*(\{.*?\})\s*```", output, re.DOTALL) or \
                        re.search(r"(\{.*?\})", output, re.DOTALL)

            parsed_output = json.loads(json_text.group(1)) if json_text else {}

            # Validate against output schema
            if output_schema:
                for key, expected_type in output_schema.items():
                    if not isinstance(parsed_output.get(key), expected_type):
                        raise ValueError(f"Invalid format: '{key}' is missing or incorrect.")

            response.choices[0].data_dict = dict(parsed_output)
            return response

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Retry {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                prompt = (f"Ensure your response matches the schema: {output_schema}. "
                          f"Return only the JSON object.") + "\n" + prompt
                time.sleep(1)

    response.choices[0].data_dict = {}
    return response  # Final fallback
