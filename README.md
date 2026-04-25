# 🌸 Aika-chan: The RPG & Music Bot

Aika is a specialized Discord assistant designed as a "tsundere older sister" persona. She serves a dual purpose: acting as an intelligent RPG game master/assistant and a high-performance music player. 

Inspired by **Neo-Noir** aesthetics, Aika is sharp, challenging, and occasionally bossy, but becomes a supportive pillar for her "younger siblings" during difficult campaign moments.

---

## 🔪 Core Features

### 🧠 Intelligent RPG Assistance (Powered by Groq/Llama 3.1)
* **Dynamic Persona:** Aika isn't just a bot; she's a character. Expect casual language, slang, and a bit of attitude.
* **Contextual Knowledge:** She reads from a `projects.txt` file to keep track of your RPG world, NPCs, and campaign notes.
* **Smart Memory:** Remembers the last 10 messages in a conversation to maintain flow and context.
* **Safety Integrated:** Hard-coded refusal for illegal or harmful content.

### 🎵 High-Fidelity Music System
* **Seamless Streaming:** Utilizes `yt-dlp` for efficient YouTube searching and audio extraction.
* **Queue Management:** Supports server-specific song queues using asynchronous deques.
* **Playback Control:** Full suite of slash commands for `play`, `skip`, `pause`, `resume`, and `stop`.
* **Optimized Audio:** Configured with FFmpeg Opus for low-latency, high-quality 96k audio streams.

---

## 🚀 Tech Stack

- **Framework:** `discord.py` (Slash Commands / App Commands)
- **AI Engine:** Groq Cloud API (`llama-3.1-8b-instant`)
- **Audio Processing:** `yt-dlp` + FFmpeg
- **Environment:** Python 3.10+ with `python-dotenv`

---

## 🛠️ Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/LumeMello/Discord-BOT.git
    cd aika-bot
    ```

2.  **Install Dependencies:**
    ```bash
    pip install discord.py groq yt-dlp python-dotenv
    git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
    ```
    Extract the FFmpeg and copy the FFmpeg.exe in bin/FFmpeg directory

3.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    GROQ_KEY=your_groq_api_key
    ```

4.  **Hardware Requirements:**
    Ensure FFmpeg is installed and accessible. The code currently points to `bin/ffmpeg/ffmpeg.exe`. Update this path in the script if you are on Linux or have it in your system PATH.

5.  **RPG Data:**
    Populate `projects.txt` with your campaign notes. If the file is missing, Aika will default to her base persona.

---

## 📜 Commands

| Command | Description |
| :--- | :--- |
| `/greet` | Get a typical "Aika-style" welcome. |
| `/ask [query]` | Chat with Aika. She uses your RPG notes as context. |
| `/play [song]` | Search and play music in your current voice channel. |
| `/skip` | Skip the current track. |
| `/pause` | Pause the music. |
| `/resume` | Resume the party. |
| `/stop` | Clear the queue and disconnect Aika. |

---

## ⚙️ Configuration Notes

* **Guild Sync:** The bot is configured to sync commands specifically to the `GUILD_ID` defined in the source code for faster updates during development.
* **Memory Management:** Conversation history is stored in-memory and resets upon bot restart.
* **Voice Stability:** Uses auto-reconnect and stream delay buffers to ensure music doesn't cut out during network spikes.

---

> *"It's not like I made this README just for you, BAKA! Just make sure you read it carefully."* — **Aika**
