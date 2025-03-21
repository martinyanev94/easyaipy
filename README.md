# easyaipy

EasyAIPy allows extracting precise variables from AI API responses. It is designed to interact with 
OpenAI and Gemini developer APIs. It allows programmers to specify the amount and the datatypes of variables
they want to receive in their API response. 

## Installation

```bash
pip install easyaipy
```

## A Simple Example with OpenAI API

```python
from easyaipy import openai_easy_prompt

# Define or import your API key
api_key = "YOUR_API_KEY"

# Define the input prompt
prompt = "Generate a brief summary of the importance of AI in education."

# Specify an output schema (optional)
output_schema = {
    "summary": str,
    "word_count": int
}


response = openai_easy_prompt(
    prompt=prompt,
    model="gpt-4o-mini",
    output_schema=output_schema,
    max_retries=3,
    api_key=api_key
)

# Print the validated response
print("Response:", response.choices[0].data_dict)
```

## Expected Output
If the OpenAI API responds correctly and matches the schema, the output will look like this:


```json
{
    "summary": "AI in education enhances personalized learning, streamlines administrative tasks, and fosters innovation in teaching.",
    "word_count": 15
}
```
