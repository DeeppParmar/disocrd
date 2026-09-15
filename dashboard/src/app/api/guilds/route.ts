import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { getUserGuilds, getBotGuilds, getMutualGuilds } from '@/lib/discord';

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session || !session.accessToken) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    const userGuilds = await getUserGuilds(session.accessToken);
    const botGuilds = await getBotGuilds();
    const mutualGuilds = getMutualGuilds(userGuilds, botGuilds);
    return NextResponse.json(mutualGuilds);
  } catch (error) {
    console.error('Error fetching guilds:', error);
    return new NextResponse('Internal Error', { status: 500 });
  }
}
