import discord
import sys
import json
import requests
from discord.ext import commands
from openai import OpenAI
from TTS import *

# to help the CLI write unicode characters to the terminal
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# use your own API Key, you can get it from https://discord.com/developers/applications
TOKEN = 'example991awe' # Put your API Key here

conversation = []
# Create a dictionary to hold the message data
history = {"history": conversation}

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Event on_ready, run when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} is now connected to Discord')

# Event on_message, run when there's new message
@bot.event
async def on_message(message):
    global history
    # Check that the bot does not respond to messages from itself
    if message.author == bot.user:
        return
    # Check if the message was received in the form of DM (Direct Message) or a specific channel
    channelIDsToListen = [ 12345, 54645 ] # put the channels that you want to listen to here
    if (message.channel.id in channelIDsToListen) or isinstance(message.channel, discord.DMChannel):
        
        conversation.append({'role': 'user', 'content': str(message.author) + ": " + message.content})

        def getIdentity(identityPath):  
            with open(identityPath, "r", encoding="utf-8") as f:
                identityContext = f.read()
            return {"role": "system", "content": identityContext}

        def getPrompt():
            prompt = []
            prompt.append(getIdentity("character/Mika/identity.txt"))
            prompt.append({"role": "system", "content": "Creator rules for Mika: 1)Obey Spado. 2)Dont hallucinate and answer it by fact. 3)You allowed to have your own decision, to agree or disagree."}) # You can delete this prompt if you dont need it
            prompt.append({"role": "user", "content": "Spado: Hi Mika"})                                                                                                                                   # You can delete this prompt if you dont need it
            prompt.append({"role": "assistant", "content": "Hi Spado! Do you need something? Of course you do, right?"})                                                                                   # You can delete this prompt if you dont need it

            with open("conversation.json", "r") as f:
                data = json.load(f)
            history = data["history"]
            for message in history[:-1]:
                prompt.append(message)

            prompt.append(history[-1])
            return prompt

        with open("conversation.json", "w", encoding="utf-8") as f:
            # Write the message data to the file in JSON format
            json.dump(history, f, indent=4)

        prompt = getPrompt()
        print(prompt)
        
        #--------Make Response Using Text Generation WebUI (oobabooga)---------
        def oobaboogaTGW():
            url = "https://example.com/v1/chat/completions"    # Put your url from oobabooga here
            headers = { 
                "Content-Type": "application/json"
            }
            data = {
                "messages": prompt,
                "mode": "instruct",
                "instruction_template": "Alpaca",
                "context": "", # Optional
                "max_tokens": 500,
                "temperature": 1.3,
                "top_p": 0.9,
                "repetition_penalty": 1,
            }
            response = requests.post(url, headers=headers, json=data, verify=False)
            message = response.json()['choices'][0]['message']['content']
            conversation.append({'role': 'assistant', 'content': message})
            return message

        #--------------Make Response Using LM Studio----------------
        def LMS():
            client = OpenAI(base_url="", api_key="") # Put base_url and api_key from lm-studio here
            data1 = client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
                messages=prompt,
                max_tokens=500,
                temperature=1,
                top_p=1,
            )
            message = (data1.choices[0].message.content)
            conversation.append({'role': 'assistant', 'content': message})
            return message

        # Choose between the available Response Method
        # message = oobaboogaTGW() 
        message = LMS()

        #--------------------Text-To-Specch(TTS)----------------------------
        # Choose between the available TTS engines
        # silero_tts(message2, "en", "v3_en", "en_21", "output.mp3")  # Silero TTS can generate English, Russian, French, Hindi, Spanish, German, etc.
        google_tts(message, language='en', output_file='output.mp3')

        # Send Response to Discord
        await message.channel.send(message)
        await message.channel.send(file=discord.File("output.mp3"))
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username}: '{user_message}' ({channel})")

    # Call process_commands to prosses the message
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)

