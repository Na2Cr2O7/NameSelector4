
import pyttsx3 as pyttsx4
import asyncio


def speak(text):
     engine=pyttsx4.init()
     engine.say(text)
     engine.runAndWait()

async def speakAsync(text):
     engine=pyttsx4.init()
     engine.say(text)
     asyncio.run(engine.runAndWait())
if __name__=="__main__":
     speak("Hello, I am Name Selector 4. How can I assist you?")
     input("Press any key to exit")