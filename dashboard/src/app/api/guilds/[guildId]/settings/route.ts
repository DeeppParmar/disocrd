import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { db } from '@/lib/db';
import { guildConfigs } from '@/lib/schema';
import { eq } from 'drizzle-orm';

export async function GET(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);

  try {
    const config = await db.select().from(guildConfigs).where(eq(guildConfigs.guildId, guildIdNum)).limit(1);
    return NextResponse.json(config[0] || null);
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}

export async function PATCH(req: Request, { params }: { params: { guildId: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new NextResponse('Unauthorized', { status: 401 });

  const guildIdNum = Number(params.guildId);
  
  try {
    const body = await req.json();
    await db.update(guildConfigs).set(body).where(eq(guildConfigs.guildId, guildIdNum));
    return NextResponse.json({ success: true });
  } catch (error) {
    return new NextResponse('Internal Error', { status: 500 });
  }
}
