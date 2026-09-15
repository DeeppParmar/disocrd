import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '@/lib/auth';
import Link from 'next/link';

export default async function Home() {
  const session = await getServerSession(authOptions);
  
  if (session) {
    redirect('/dashboard');
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
      <h1 className="text-6xl font-bold mb-4">Discord Server OS</h1>
      <p className="text-xl mb-8 text-gray-400">The ultimate management dashboard for your community.</p>
      <Link href="/login" className="bg-blurple hover:bg-opacity-80 text-white font-bold py-3 px-8 rounded-lg text-lg transition-all">
        Login with Discord
      </Link>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-5xl">
        {['Moderation', 'Analytics', 'Tickets', 'Logs', 'Automation', 'Security'].map(feature => (
          <div key={feature} className="bg-discord_dark p-6 rounded-xl border border-gray-800 hover:border-gray-600 transition-colors">
            <h3 className="text-xl font-bold mb-2">{feature}</h3>
            <p className="text-gray-400">Manage {feature.toLowerCase()} settings and view insights in real-time.</p>
          </div>
        ))}
      </div>
    </main>
  );
}
