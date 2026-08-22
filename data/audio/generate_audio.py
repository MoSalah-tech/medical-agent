import asyncio
import os
from pathlib import Path
import edge_tts

async def main():
    text = "I have a headache and fever for two days."
    communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")

     

    await communicate.save("test_audio.mp3")
    print("Saved!---->  test_audio.mp3")

asyncio.run(main())