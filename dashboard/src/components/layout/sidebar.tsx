import Link from 'next/link';
import { Home, Settings, Users, Shield, MessageSquare, Activity, FileText } from 'lucide-react';

export default function Sidebar({ guildId }: { guildId?: string }) {
  const links = [
    { name: 'Overview', href: `/dashboard/${guildId}`, icon: Home },
    { name: 'Settings', href: `/dashboard/${guildId}/settings`, icon: Settings },
    { name: 'Moderation', href: `/dashboard/${guildId}/moderation`, icon: Shield },
    { name: 'Analytics', href: `/dashboard/${guildId}/analytics`, icon: Activity },
    { name: 'Logs', href: `/dashboard/${guildId}/logs`, icon: FileText },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800 flex items-center justify-between">
        <h2 className="text-xl font-bold">Discord OS</h2>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        {guildId ? (
          <nav className="space-y-1 px-3">
            {links.map((link) => (
              <Link key={link.name} href={link.href} className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-gray-800 transition-colors text-gray-300 hover:text-white">
                <link.icon className="w-5 h-5" />
                {link.name}
              </Link>
            ))}
          </nav>
        ) : (
          <div className="px-6 text-gray-400">Select a server to manage</div>
        )}
      </div>
      <div className="p-4 border-t border-gray-800">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-white flex items-center gap-2">
          ← Back to Servers
        </Link>
      </div>
    </div>
  );
}
