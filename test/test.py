import base64
import os
from datetime import datetime

from google import genai
from google.genai import types

start = datetime.now()

with open("./test2.png", "rb") as f:
  data = f.read()


def generate():
  client = genai.Client(
    api_key="AIz",
  )

  model = "gemini-2.0-flash"
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_bytes(
          mime_type="""image/jpeg""",
          data=data,
        ),
        types.Part.from_text(text="""帮我生成图片中文tag, 用逗号分割, 不要返回多余描述,尽可能详细"""),
      ],
    ),
  ]
  generate_content_config = types.GenerateContentConfig(
    response_mime_type="text/plain",
  )

  for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=generate_content_config,
  ):
    print(chunk.text, end="")


if __name__ == "__main__":
  generate()
  print(datetime.now() - start)
