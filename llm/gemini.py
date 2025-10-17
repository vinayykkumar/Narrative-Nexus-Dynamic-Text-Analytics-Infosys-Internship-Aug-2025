# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


GEMINI_API_KEY="AIzaSyDDef8kHKTmSb58aJwBawzoIDLEGoNnhHI"

def execute_gemini(prompt):
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.5-flash-lite"
    contents = [
        # types.Content( # system prompt
        #     role="system",
        #     parts=[
        #         types.Part.from_text(text=
        #         """Make Text Summarization like social media marketing"""
        #         ),
        #     ],
        # ),
        types.Content( # user prompt (same as chat input)
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    tools = [
        # this will attach google results to the llm output
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

    result = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return result.text

if __name__ == "__main__":

    bunch_of_prompts = [
        "How many a are there in apple ?",
        "How many p are there in apple ?",
        "How many l are there in apple ?",
    ]

    for the_prompt in bunch_of_prompts:
        out = execute_gemini(prompt=the_prompt)
        print(out)