""" 
Google Vision API class to generate image descriptions using Google Vision API
"""

import base64
import os
from google import genai
from google.genai import types

from .base_api import BaseAPI
from .system_prompt import description_system_prompt


class GoogleVisionAPI(BaseAPI):
    """Google Vision API class to generate image descriptions using Google Vision API"""
    
    async def generate_description(self, image_path):

        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        files = [
            # Make the file available in local system working directory
            client.files.upload(file=image_path),
        ]
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(
                    text=description_system_prompt,
                ),
            ],
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")