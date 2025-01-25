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
                              Example: {"key1": str, "key2": int}.
        max_retries (int): Maximum number of retries to adjust the prompt for a valid response.

    Returns:
        dict: A dictionary containing the validated output if successful.

    Raises:
        RuntimeError: If maximum retries are reached without a valid response.
    """

    client = OpenAI(api_key=api_key)

    # Helper function to modify the prompt
    def modify_prompt(base_prompt: str, schema: dict) -> str:
        schema_description = ", ".join([f"'{key}': {value_type.__name__}" for key, value_type in schema.items()])
        return (
            f"{base_prompt}\n\n"
            f"Please respond in JSON format with the following structure:\n"
            f"{{{schema_description}}}\n"
            f"Ensure the data types match the structure exactly."
        )

    # Adjust the initial prompt if a schema is provided
    if output_schema:
        prompt = modify_prompt(prompt, output_schema)
        print(prompt)

    for attempt in range(max_retries):
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            output = response.choices[0].message.content
            output = "\n".join(output.splitlines()[1:-1]) if len(output.splitlines()) > 2 else ""

            print(output)

            # Parse the response to a dictionary if schema validation is needed
            parsed_output = json.loads(output) if output_schema else output

            # Validate the output if a schema is provided
            if output_schema:
                for key, value_type in output_schema.items():
                    if key not in parsed_output or not isinstance(parsed_output[key], value_type):
                        raise ValueError(f"Invalid output: '{key}' is missing or not of type {value_type.__name__}.")

            # If validation succeeds, return the output
            return parsed_output

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                # Adjust the prompt further for clarification
                clarification = (
                    f"Your last response did not match the required format. "
                    f"Ensure your response is a JSON object strictly matching this schema: {output_schema}. "
                )
                prompt = clarification + prompt
                time.sleep(1)  # Wait briefly before retrying
            else:
                raise RuntimeError("Maximum retries reached. Failed to generate the required output.")
