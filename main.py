import argparse
import time
import asyncio

from whisper_mic import WhisperMic

import vision
from vimbot import Vimbot

async def main(voice_mode):
    print("Initializing the Vimbot driver...")
    driver = Vimbot()
    await driver.initialize()

    if voice_mode:
        print("Voice mode enabled. Listening for your command...")
        mic = WhisperMic()
        try:
            objectives = mic.listen().split(',')
        except Exception as e:
            print(f"Error in capturing voice input: {e}")
            return  # Exit if voice input fails
        print(f"Objectives received: {objectives}")
    else:
        objectives = input("Please enter your objectives, separated by commas: ").split(',')

    answers = []  # Initialize an empty list for answers
    links = []  # Initialize an empty list for links

    for objective in objectives:
        print("Navigating to Google...")
        await driver.navigate("https://www.google.com")

        while True:
            time.sleep(1)
            print("Capturing the screen...")
            screenshot = await driver.capture()

            print(f"Getting actions for the given objective: {objective}...")
            action, answers, links = await vision.get_actions(driver, screenshot, objective.strip(), answers, links)
            print(f"JSON Response: {action}")
            if await driver.perform_action(action):  # returns True if done
                break
            if "done" in action:
                current_page = await driver.get_current_page()
                links.append(current_page)  # Save the current page URL
                break

    # Print accumulated answers and links
    # print("Accumulated Answers:")
    # for answer in answers:
    #     print(answer)

    print("Accumulated Links:")
    for link in links:
        print(link)

    await driver.close()


def main_entry():
    parser = argparse.ArgumentParser(description="Run the Vimbot with optional voice input.")
    parser.add_argument(
        "--voice",
        help="Enable voice input mode",
        action="store_true",
    )
    args = parser.parse_args()
    asyncio.run(main(args.voice))


if __name__ == "__main__":
    try:
        main_entry()
    except KeyboardInterrupt:
        print("Exiting...")
