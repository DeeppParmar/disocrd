export const MANAGE_GUILD = 0x20;
export const ADMINISTRATOR = 0x8;

export interface DiscordGuild {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
  permissions: number;
  features: string[];
}

export async function getUserGuilds(accessToken: string): Promise<DiscordGuild[]> {
  const res = await fetch('https://discord.com/api/v10/users/@me/guilds', {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  if (!res.ok) return [];
  return res.json();
}

export async function getBotGuilds(): Promise<DiscordGuild[]> {
  const res = await fetch('https://discord.com/api/v10/users/@me/guilds', {
    headers: { Authorization: `Bot ${process.env.DISCORD_BOT_TOKEN}` }
  });
  if (!res.ok) return [];
  return res.json();
}

export function hasPermission(permissions: number, flag: number): boolean {
  return (permissions & flag) === flag;
}

export function getMutualGuilds(userGuilds: DiscordGuild[], botGuilds: DiscordGuild[]) {
  const botGuildIds = new Set(botGuilds.map(g => g.id));
  return userGuilds.filter(g => 
    botGuildIds.has(g.id) && (hasPermission(g.permissions, MANAGE_GUILD) || hasPermission(g.permissions, ADMINISTRATOR))
  );
}

export function getGuildIcon(guild: DiscordGuild): string | null {
  if (!guild.icon) return null;
  return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`;
}
