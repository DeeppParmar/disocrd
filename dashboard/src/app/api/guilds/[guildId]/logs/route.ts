import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { logEvents } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const logs = await db.select().from(logEvents).where(eq(logEvents.guildId, guildIdNum)).orderBy(desc(logEvents.createdAt)).limit(50);
    return NextResponse.json(logs);
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
