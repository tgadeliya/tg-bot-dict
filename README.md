# [WIP] Telegram Dictionary Bot

A Telegram bot that provides English word **meanings** and **translations** on request. [Marriam-Webster API](https://dictionaryapi.com/) is used as English Thesaurus. Bot works via public web hook

## ✨ Features

- 🔍 Get definitions for English words
- 📌 Simple interface via Telegram chat

### Planned Features (Coming Soon)

- Generate [Anki](https://apps.ankiweb.net/) flashcards directly from words
- Translate words to your native language
- Generate sentence examples with provided word
- Store words, meanings, and translations in a local database for review


## Getting Started

### 0. Basic requirements

To start with usage, you need:

- Telegram bot token
- Marriam-Webster API Token
- Public webhook and server to serve bot (I use cloudflare tunnels, apache and Raspberry Pi for this purpose)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/telegram-dictionary-bot.git
cd telegram-dictionary-bot
```

### 2. Create environment and install libraries using `uv`
```bash
un sync
```

### 3. Create .env file with Telegram token and Marriam-Webster tokens
### 4. Setup server (TODO: Add more description)
