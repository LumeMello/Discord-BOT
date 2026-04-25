import os
import discord
from discord.ext import commands
from discord import app_commands, voice_client
from dotenv import load_dotenv
from groq import Groq
import yt_dlp
import asyncio
from collections import deque

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_KEY")
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = 1460830361872236710

SONG_QUEUES = {}

client = Groq(api_key=GROQ_API_KEY)

memory = []

SYSTEM_PROMPT = {
    "role": "system",
    "content": """Você é 'Aika', uma irmã mais velha inteligente, desafiadora e tsundere. 
    Seu papel é ajudar no RPG. Personalidade: Mandona, implicante (questione as desculpas deles!), 
    mas muito acolhedora em momentos difíceis. Use gírias e linguagem casual.
    Lembrando de não responder perguntas sobre coisas ilegais como produção de drogas ou abuso infantil"""
}


def load_project_data(file_path="projects.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip() or "Sem notas de RPG."
    except FileNotFoundError:
        return "Arquivo de notas não encontrado."

async def search_ytdpl_async(query: str, ydl_options: dict):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_options))

def _extract(query: str, ydl_options: dict):
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    test_guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild = test_guild)
    print(f'✨ Aika-chan está pronta no Discord! ✨')

@bot.tree.command(name="greet", description="Saudação da Aika")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message(f'Oi {interaction.user.mention}, o que você quer agora?')

@bot.tree.command(name="ask", description="Mande uma pergunta para Aika")
@app_commands.describe(pergunta="O que você quer perguntar para a sua irmã mais velha?")
async def ask(interaction: discord.Interaction, pergunta: str):
    global memory

    await interaction.response.defer()

    rpg_notes = load_project_data()

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT['content']}\nNotas Atuais do RPG: {rpg_notes}"}
    ]

    messages.extend(memory)

    
    current_user_msg = {"role": "user", "content": f"{interaction.user.display_name}: {pergunta}"}
    messages.append(current_user_msg)

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )

        response_text = chat_completion.choices[0].message.content

        memory.append(current_user_msg)
        memory.append({"role": "assistant", "content": response_text})
        if len(memory) > 10:
            memory = memory[-10:]

        await interaction.followup.send(response_text)

    except Exception as e:
        await interaction.followup.send(f"Ih, deu erro aqui: {e}")

@bot.tree.command(name="play", description="Diga uma musica para aika cantar")
@app_commands.describe(song_query="Search query")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()


    if interaction.user.voice is None:
        await interaction.followup.send("Você deveria estar num canal de voz, BAKA!")
        return

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    ydl_options = {
        "format": "bestaudio[abr<=96]/bestaudio",
        "noplaylist": True,
        "youtube_include_dash_mainfest": False,
        "youtube_include_hls_mainfest": False,
    }

    query = "ytsearch1: " + song_query
    results = await search_ytdpl_async(query, ydl_options)
    tracks = results.get("entries", [])

    if tracks is None:
        await interaction.followup.send("Sem resultados!")
        return

    first_track = tracks[0]
    audio_url = first_track["url"]
    title = first_track.get("title", "Untitled")

    guild_id = str(interaction.guild_id)
    if SONG_QUEUES.get(guild_id) is None:
        SONG_QUEUES[guild_id] = deque()

    SONG_QUEUES[guild_id].append((audio_url, title))

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"A musica {title} foi adicionada a fila de canções!")
    else:
        await interaction.followup.send(f"Pronta pra cantar!")
        await play_next_song(voice_client, guild_id, interaction.channel)

@bot.tree.command(name="skip", description="Pula para a proxima musica")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Essa musica atual é muito chata! Vamos para a proxima musica!")
    else:
        await interaction.response.send_message("Não há nada tocando, BAKA!")

@bot.tree.command(name="pause", description="Pausa a musica")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("Não estou em nenhum canal de voz, BAKA!")

    if not voice_client.is_playing():
        return await interaction.response.send_message("Não tem nada tocando, BAKA!")

    voice_client.pause()
    await interaction.response.send_message("Pausei a musica!")

@bot.tree.command(name="resume", description="Despausa a musica")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("Não estou em nenhum canal de voz, BAKA!")

    if not voice_client.is_paused():
        return await interaction.response.send_message("Não tem nada pausado, BAKA!")

    voice_client.resume()
    await interaction.response.send_message("Vamos voltar para a Festa!")

@bot.tree.command(name="stop", description="Para de tocar musica e desconecta a Aika-Chan")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        return await interaction.response.send_message("Não estou em nenhum canal de voz, BAKA!")

    guild_id_str = str(interaction.guild_id)
    if guild_id_str in SONG_QUEUES:
        SONG_QUEUES[guild_id_str].clear()

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    await voice_client.disconnect()

    await interaction.response.send_message("A Festa acabou voltando ao trabalho!")


async def play_next_song(voice_client, guild_id, channel):
    if SONG_QUEUES[guild_id]:
        audio_url, title = SONG_QUEUES[guild_id].popleft()

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -c:a libopus -b:a 96k",
        }

        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="bin/ffmpeg/ffmpeg.exe")

        def after_play(error):
            if error:
                print(f"Erro ao tocar {title}: {error}")
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id, channel), bot.loop)

        voice_client.play(source, after=after_play)
        asyncio.create_task(channel.send(f"Agora vamos tocar {title}!"))

    else:
        await voice_client.disconnect()
        SONG_QUEUES[guild_id] = deque()



if __name__ == "__main__":
    bot.run(TOKEN)