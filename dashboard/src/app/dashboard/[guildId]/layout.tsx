import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '@/lib/auth';
import Sidebar from '@/components/layout/sidebar';
import Header from '@/components/layout/header';

export default async function GuildLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: { guildId: string }
}) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    redirect('/login');
  }

  return (
    <div className="flex h-screen overflow-hidden bg-discord_darker text-gray-100 absolute inset-0 z-50">
      <Sidebar guildId={params.guildId} />
      <div className="flex-1 flex flex-col h-full relative">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
