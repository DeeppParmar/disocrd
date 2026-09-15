'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';

export default function ModerationPage({ params }: { params: { guildId: string } }) {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetch(`/api/guilds/${params.guildId}/moderation`)
      .then(res => res.json())
      .then(data => {
        setCases(data);
        setLoading(false);
      });
  }, [params.guildId]);

  const getActionColor = (action: string) => {
    switch(action.toLowerCase()) {
      case 'warn': return 'warning';
      case 'timeout': return 'warning';
      case 'kick': return 'danger';
      case 'ban': return 'danger';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Moderation Logs</h2>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-800/50 text-gray-400 text-sm">
              <tr>
                <th className="p-4 font-medium">Case #</th>
                <th className="p-4 font-medium">User ID</th>
                <th className="p-4 font-medium">Moderator ID</th>
                <th className="p-4 font-medium">Action</th>
                <th className="p-4 font-medium">Reason</th>
                <th className="p-4 font-medium">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <tr key={i}>
                    <td colSpan={6} className="p-4"><Skeleton className="h-8 w-full" /></td>
                  </tr>
                ))
              ) : cases.length > 0 ? (
                cases.map(c => (
                  <tr key={c.id} className="hover:bg-gray-800/30">
                    <td className="p-4">#{c.id}</td>
                    <td className="p-4 text-gray-300">{c.userId}</td>
                    <td className="p-4 text-gray-300">{c.modId}</td>
                    <td className="p-4"><Badge variant={getActionColor(c.action) as any}>{c.action}</Badge></td>
                    <td className="p-4 text-gray-400 max-w-xs truncate">{c.reason || 'No reason provided'}</td>
                    <td className="p-4 text-gray-400">{new Date(c.createdAt).toLocaleDateString()}</td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan={6} className="p-8 text-center text-gray-500">No moderation cases found</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-800 flex justify-between items-center text-sm text-gray-400">
          <div>Page {page}</div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
            <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)}>Next</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
