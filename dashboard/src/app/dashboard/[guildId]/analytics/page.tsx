'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function AnalyticsPage({ params }: { params: { guildId: string } }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/guilds/${params.guildId}/analytics`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      });
  }, [params.guildId]);

  const latest = data[data.length - 1] || {};

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Server Analytics</h2>
      <p className="text-gray-400">Activity summary over the last 30 days.</p>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader><CardTitle>Total Members</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-blurple">{latest.memberCount?.toLocaleString() || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Messages Sent (Today)</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-green-500">{latest.messagesSent?.toLocaleString() || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Mod Actions (Today)</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-red-500">{latest.modActions?.toLocaleString() || 0}</div></CardContent>
          </Card>
        </div>
      )}

      <Card className="mt-8">
        <CardHeader><CardTitle>Daily Overview (Data)</CardTitle></CardHeader>
        <CardContent>
           <div className="text-sm text-gray-400">
             {data.length === 0 ? "No analytics data found." : `Found ${data.length} snapshots.`}
           </div>
        </CardContent>
      </Card>
    </div>
  );
}
