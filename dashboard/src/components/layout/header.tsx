'use client';
import { signOut, useSession } from 'next-auth/react';
import { Button } from '@/components/ui/button';

export default function Header() {
  const { data: session } = useSession();

  return (
    <header className="h-16 border-b border-gray-800 bg-discord_dark flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold">Dashboard</h1>
      </div>
      <div className="flex items-center gap-4">
        {session?.user && (
          <>
            <span className="text-sm text-gray-300">{session.user.name}</span>
            <Button variant="outline" size="sm" onClick={() => signOut({ callbackUrl: '/' })}>
              Sign Out
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
