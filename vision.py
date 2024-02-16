import base64
import json
import os
from io import BytesIO

import openai
from dotenv import load_dotenv
from PIL import Image
import asyncio

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
IMG_RES = 1080

# Function to encode the image
def encode_and_resize(image):
    W, H = image.size
    image = image.resize((IMG_RES, int(IMG_RES * H / W)))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded_image

async def get_actions(bot, screenshot, objective, answers=None, links=None):
    encoded_screenshot = encode_and_resize(screenshot)

    if answers is None:
        answers = []  # Initialize or use a provided list

    if links is None:
        links = []  # Initialize or use a provided list

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"You need to choose which action to take to help a user do this task: {objective}. Your options are navigate, type, click, and done. Navigate should take you to the specified URL. Type and click take strings where if you want to click on an object, return the string with the yellow character sequence you want to click on, and to type just a string with the message you want to type. For clicks, please only respond with the 1-2 letter sequence in the yellow box, and if there are multiple valid options choose the one you think a user would select. For typing, please return a click to click on the box along with a type with the message to write. When the page seems satisfactory, return done as a key with no value it doesn't have to be perfect it just has to have {objective} written somewhere on the page. Always scroll up and down before returning another json, just incase the objective is at the bottem. You must respond in JSON only with no other fluff or bad things will happen. The JSON keys must ONLY be one of navigate, type, or click. Do not return the JSON inside a code block.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_screenshot}",
                        },
                    },
                ],
            }
        ],
        max_tokens=200,
    )

    try:
        json_response = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        cleaned_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant to fix an invalid JSON response. You need to fix the invalid JSON response to be valid JSON. You must respond in JSON only with no other fluff or bad things will happen. Do not return the JSON inside a code block.",
                },
                {"role": "user", "content": f"The invalid JSON response is: {response.choices[0].message.content}"},
            ],
        )
        try:
            cleaned_json_response = json.loads(cleaned_response.choices[0].message.content)
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            return {}, answers
        return cleaned_json_response, answers

    # Handle the 'done' action to accumulate answers
    if "done" in json_response:
        current_page = await bot.get_current_page()
        links.append(current_page)  # Save the current page URL

    return json_response, answers, links

async def main():
    image = Image.open("image.png")
    actions = await get_actions(image, "upvote the pinterest post")

if __name__ == "__main__":
    asyncio.run(main())
