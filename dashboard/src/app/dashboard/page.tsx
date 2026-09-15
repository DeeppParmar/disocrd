'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DiscordGuild, getGuildIcon } from '@/lib/discord';

export default function DashboardHome() {
  const [guilds, setGuilds] = useState<DiscordGuild[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/guilds')
      .then(res => res.json())
      .then(data => {
        setGuilds(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-center mt-20 text-gray-400 animate-pulse">Loading your servers...</div>;
  }

  if (guilds.length === 0) {
    return <div className="text-center mt-20 text-gray-400">No mutual servers found where you have Manage Server permissions.</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Select a Server</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {guilds.map(guild => {
          const iconUrl = getGuildIcon(guild);
          return (
            <Link href={`/dashboard/${guild.id}`} key={guild.id}>
              <Card className="hover:border-blurple transition-colors cursor-pointer h-full">
                <CardHeader className="flex flex-col items-center text-center">
                  {iconUrl ? (
                    <img src={iconUrl} alt={guild.name} className="w-20 h-20 rounded-full mb-4" />
                  ) : (
                    <div className="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center text-2xl font-bold mb-4">
                      {guild.name.charAt(0)}
                    </div>
                  )}
                  <CardTitle className="text-lg">{guild.name}</CardTitle>
                </CardHeader>
              </Card>
            </Link>
          )
        })}
      </div>
    </div>
  );
}
