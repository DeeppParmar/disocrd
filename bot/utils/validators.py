"""Validation utilities."""
import re
import discord

def validate_color(color_str: str) -> discord.Color:
    if not color_str:
        return discord.Color.default()
    color_str = color_str.strip().lstrip('#')
    try:
        return discord.Color(int(color_str, 16))
    except ValueError:
        raise ValueError(f"Invalid color format: {color_str}")

def validate_channel_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:100]

def validate_role_name(name: str) -> str:
    return name[:100]

def validate_permissions(perm_int: int) -> discord.Permissions:
    return discord.Permissions(perm_int)

def validate_duration(duration_str: str) -> int:
    pattern = re.compile(r'^(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$')
    match = pattern.match(duration_str.strip().lower())
    if not match or duration_str.strip() == "":
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    total_seconds = (
        parts['weeks'] * 604800 +
        parts['days'] * 86400 +
        parts['hours'] * 3600 +
        parts['minutes'] * 60 +
        parts['seconds']
    )
    return total_seconds

def validate_url(url: str) -> str:
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return url
