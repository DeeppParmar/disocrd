import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { moderationCases } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const cases = await db.select().from(moderationCases).where(eq(moderationCases.guildId, guildIdNum)).orderBy(desc(moderationCases.createdAt)).limit(50);
    return NextResponse.json(cases);
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
