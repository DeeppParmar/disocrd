import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { channelMappings } from '@/lib/schema';
import { eq } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const channels = await db.select().from(channelMappings).where(eq(channelMappings.guildId, guildIdNum));
    return NextResponse.json(channels);
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
