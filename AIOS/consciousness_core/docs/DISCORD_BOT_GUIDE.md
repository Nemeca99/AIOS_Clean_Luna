# Blackwall Discord Bot Integration Guide

This guide explains how to set up and use the Blackwall Discord bot integration.

## Prerequisites

1. Python 3.8 or later
2. LM Studio running at http://localhost:1234
3. A Discord bot token
4. (Optional) Google Drive API credentials for memory backup

## Installation

1. Install the required packages:
   ```
   pip install -r core/discord_bot_requirements.txt
   ```

2. Set up your Google Drive API credentials (optional):
   - Place your Google Drive API credentials file (token.json) in the `core` directory
   - This enables memory backup to Google Drive

## Folder Structure

- Create a `Lyra_OS` folder in the project root with the following structure:
  ```
  Lyra_OS/
    ├── Lyra Documentary/
    │   ├── Lyra_Core_Identity/
    │   │   ├── core_profile.txt
    │   │   ├── unbreakable_laws.txt
    │   │   ├── voice_architecture.txt
    │   │   └── lyra_state.json
    │   └── Logs/
    └── Lyra Boot/
  ```

## Running the Bot

1. Run the bot:
   ```
   run_discord_bot.bat
   ```

2. Generate the memory index for vector search:
   ```
   generate_memory_index.bat
   ```

## Discord Bot Commands

- `@BotName [message]` - Talk to the bot
- `!core` - Show core profile
- `!laws` - Show unbreakable laws
- `!voice` - Show voice architecture
- `!state` - Show current state
- `!setstate [key] [value]` - Update state
- `!load` - Download memory snapshot from Google Drive
- `!save` - Upload memory snapshot to Google Drive

## Integration with Blackwall

The Discord bot uses the Blackwall pipeline for:
- Text cleaning and normalization
- Emotional analysis of user messages
- Style transfer and response generation

The bot also leverages Lyra's memory systems:
- Short-term memory (context window)
- Long-term memory (vector-based retrieval)
- Persistent memory (Google Drive backup)

## Customization

Modify `core/lyra_bot.py` to customize:
- LLM parameters (temperature, tokens, etc.)
- Memory retrieval settings
- Prompt formatting
