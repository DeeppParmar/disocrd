"""Configures Discord intents for the bot."""

import discord


def get_intents() -> discord.Intents:
    """Gets the required intents for the bot.
    
    Returns:
        discord.Intents: The configured intents.
    """
    intents = discord.Intents.default()
    
    # Privileged intents
    # Required for: welcoming users, tracking member count, roles management, moderation
    intents.members = True
    
    # Required for: reading message content in commands, automod scanning, message logging
    intents.message_content = True
    
    # Required for: knowing when users come online/offline, some activity tracking
    intents.presences = True
    
    # Enable other necessary standard intents
    intents.guilds = True
    intents.bans = True
    intents.emojis_and_stickers = True
    intents.integrations = True
    intents.webhooks = True
    intents.invites = True
    intents.voice_states = True
    intents.messages = True
    intents.reactions = True
    intents.moderation = True
    
    return intents
