import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { guildConfigs, moderationCases, tickets, analyticsSnapshots } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const config = await db.select().from(guildConfigs).where(eq(guildConfigs.guildId, guildIdNum)).limit(1);
    const modCount = await db.select().from(moderationCases).where(eq(moderationCases.guildId, guildIdNum));
    const ticketsData = await db.select().from(tickets).where(eq(tickets.guildId, guildIdNum));
    const analytics = await db.select().from(analyticsSnapshots).where(eq(analyticsSnapshots.guildId, guildIdNum)).orderBy(desc(analyticsSnapshots.date)).limit(1);

    return NextResponse.json({
      config: config[0] || null,
      modCaseCount: modCount.length,
      openTickets: ticketsData.filter(t => t.status === 'open').length,
      analytics: analytics[0] || null
    });
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
