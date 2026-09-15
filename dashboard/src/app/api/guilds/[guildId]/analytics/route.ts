import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { analyticsSnapshots } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const analytics = await db.select().from(analyticsSnapshots).where(eq(analyticsSnapshots.guildId, guildIdNum)).orderBy(desc(analyticsSnapshots.date)).limit(30);
    return NextResponse.json(analytics.reverse());
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
