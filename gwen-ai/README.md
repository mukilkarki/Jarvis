# 🤖 GWEN AI - Futuristic Personal AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/OpenRouter-FREE-green" alt="OpenRouter Free">
  <img src="https://img.shields.io/badge/Firebase-Firestore-orange" alt="Firebase Firestore">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Active">
</p>

**Gwen AI** is a futuristic, Jarvis-style personal AI assistant that runs locally on your PC. It features voice interaction, long-term memory, PC automation, a Solo Leveling-inspired productivity system, emotional intelligence, and a beautiful terminal UI with Tanglish (Tamil+English) support.

---

## ✨ Features

### 🧠 AI Chat System
- Real-time AI conversation via OpenRouter API (free models)
- DeepSeek, Qwen, Mistral, Llama, Gemini support
- Smart contextual replies with streaming
- Tanglish (Tamil + English) understanding
- Continuous conversational memory
- Human-like personality with emotional awareness

### 🗣️ Voice Interaction
- **Wake word** support: "Hey Gwen" or "Gwen"
- Speech recognition via Google Web Speech API
- **Female AI voice** via edge-tts (Microsoft Jenny Neural)
- pyttsx3 fallback TTS engine
- Continuous listening mode
- Text-to-speech with emotional variation

### 🧠 Long-Term Memory
- Automatically remembers important information
- Memory types: short_term, long_term, emotional, habits, goals, reminders, preferences
- Relevance-based retrieval system
- Auto-detect important info from conversations
- Firebase Firestore sync with local fallback
- Memory editing and deletion

### 🎮 Solo Leveling Productivity System
- **Experience Points (XP)** for completing tasks
- **Level system** from 1-100
- **Rank progression**: E-Rank → SSS-Rank (Shadow Monarch)
- **Daily quests** with random selection
- **Streak tracking** with rewards
- **15 achievements** to unlock
- **Focus sessions** (Pomodoro-style)
- Motivational coaching

### ⚡ PC Automation
- Open apps (Chrome, VSCode, Spotify, etc.)
- Open websites and search Google
- Play music on YouTube
- Lock screen & shutdown PC
- Volume control (up/down/mute)
- Screenshot capture
- Cross-platform (Windows, macOS, Linux)

### ❤️ Emotional Intelligence
- Detects stress, sadness, burnout, excitement, motivation, anxiety, anger
- Text pattern analysis for emotion detection
- Interaction frequency monitoring
- Context-aware emotional responses
- Trend analysis and stability measurement
- Automatic encouragement when needed

### 🔔 Smart Notifications
- Motivational reminders
- Hydration reminders (every hour)
- Study session reminders
- Sleep time alerts
- Quest completion notifications
- Level-up celebrations

### 🖥️ Futuristic Terminal UI
- Animated startup with ASCII art
- Colored terminal output (16 colors)
- Loading effects
- AI typing animation
- Clean command interface

---

## 🏗️ Architecture

```
gwen-ai/
├── main.py                    # Main entry point
├── core/
│   ├── ai_engine.py           # OpenRouter AI integration
│   ├── voice_engine.py        # Speech I/O (edge-tts + pyttsx3)
│   ├── memory_engine.py       # Long-term memory system
│   ├── automation_engine.py   # PC automation
│   ├── emotion_engine.py      # Emotional intelligence
│   ├── productivity_engine.py # Solo Leveling system
│   ├── notification_engine.py # Smart notifications
│   ├── wakeword_engine.py     # "Hey Gwen" detection
│   └── command_engine.py      # Command processing
├── firebase/
│   ├── firebase_config.py     # Firebase configuration
│   └── firestore_service.py   # Firestore operations
├── prompts/
│   ├── personality_prompt.txt # AI personality
│   ├── emotion_prompt.txt     # Emotion guidelines
│   └── memory_prompt.txt      # Memory instructions
├── utils/
│   ├── helpers.py             # Utility functions
│   ├── parser.py              # Command parsing
│   ├── logger.py              # Colored logging
│   └── notification_helper.py # Desktop notifications
├── data/                      # Local storage
│   ├── local_memory.json
│   ├── quests.json
│   ├── settings.json
│   ├── stats.json
│   ├── emotion_state.json
│   └── conversation_logs.json
├── assets/
│   ├── sounds/
│   └── voices/
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Microphone (for voice features)
- Internet connection (for AI features)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/gwen-ai.git
cd gwen-ai
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your OpenRouter API key
```

### Get Your API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Run Gwen AI

```bash
python main.py
```

---

## 🎮 Commands

### 💬 Conversation
```
Just talk naturally! Gwen understands Tamil, English, and Tanglish.

Examples:
  "Vanakkam Gwen!"
  "Epdi irukeenga?"
  "Tell me about yourself"
  "I'm feeling stressed today"
```

### 🌐 Automation
| Command | Action |
|---------|--------|
| `open [app]` | Open app (chrome, vscode, spotify) |
| `open [website]` | Open website |
| `search [query]` | Google search |
| `play [song]` | Play music on YouTube |
| `youtube [search]` | Open YouTube |
| `screenshot` | Take screenshot |
| `lock screen` | Lock PC |
| `shutdown` | Shutdown computer |
| `volume up/down` | Adjust volume |
| `mute/unmute` | Toggle audio |

### 🎯 Productivity
| Command | Action |
|---------|--------|
| `my stats` / `my progress` | Show level & XP |
| `my quests` | View daily quests |
| `start focus` | Begin focus session |
| `stop focus` | End focus session |
| `motivate me` | Get motivated! |

### ⏰ Reminders
| Command | Action |
|---------|--------|
| `remind me to [task] in [time]` | Set reminder |
| `timer for [time]` | Set timer |

### 🎤 Voice Modes
| Command | Action |
|---------|--------|
| `/voice` | Switch to voice input |
| `/text` | Switch to text input |
| `Hey Gwen [command]` | Wake word activation |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **AI API** | OpenRouter (free models) |
| **Database** | Firebase Firestore + local JSON |
| **Speech Recognition** | Google Speech Recognition |
| **Text-to-Speech** | edge-tts + pyttsx3 |
| **Automation** | pyautogui, subprocess |
| **Terminal UI** | colorama, rich |
| **Notifications** | notify-send / platform-specific |

---

## ⚙️ Configuration

Edit `.env` file:

```env
# Required
OPENROUTER_API_KEY=your_key_here

# Optional
OPENROUTER_MODEL=deepseek    # deepseek, qwen, mistral, llama, gemini
VOICE_ENABLED=true
WAKE_WORD_ENABLED=true
NOTIFICATIONS_ENABLED=true
MOTIVATION_INTERVAL=120      # minutes
HYDRATION_INTERVAL=60        # minutes
```

---

## 🏆 Productivity System

### Rank Progression

| Rank | Level | Title |
|------|-------|-------|
| E-Rank | 1-5 | Beginner Hunter |
| D-Rank | 6-10 | Apprentice Hunter |
| C-Rank | 11-20 | Advanced Hunter |
| B-Rank | 21-35 | Elite Hunter |
| A-Rank | 36-50 | Master Hunter |
| S-Rank | 51-70 | Legendary Hunter |
| SS-Rank | 71-85 | Mythic Hunter |
| SSS-Rank | 86-100 | Shadow Monarch |

### Achievements (15 total)
Unlock achievements by completing quests, maintaining streaks, reaching levels, and doing focus sessions.

---

## 🔒 Security

- **Local-first**: All data stored locally by default
- **API keys**: Stored in `.env` (never committed)
- **Optional Firebase**: Cloud sync disabled by default
- **Memory control**: Clear or delete memories anytime

---

## 🔮 Future Features

- [ ] Offline AI with local models (Llama.cpp)
- [ ] Vision AI for screen analysis
- [ ] OCR text extraction
- [ ] Face recognition
- [ ] Voice authentication
- [ ] Mobile sync
- [ ] Overlay assistant mode
- [ ] Smartwatch integration
- [ ] Custom wake word training

---

## 📄 License

MIT License - feel free to use, modify, and share!

---

## 🙏 Acknowledgments

- OpenRouter for free AI model access
- Microsoft edge-tts for voice synthesis
- Firebase for cloud infrastructure
- Solo Leveling for productivity inspiration

---

<p align="center">
  Made with ❤️ by Gwen AI Team
</p>