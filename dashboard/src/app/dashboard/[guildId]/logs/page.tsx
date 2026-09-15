'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function LogsPage({ params }: { params: { guildId: string } }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = () => {
    fetch(`/api/guilds/${params.guildId}/logs`)
      .then(res => res.json())
      .then(data => {
        setLogs(data);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, [params.guildId]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Audit Logs</h2>
        <span className="text-sm text-gray-400">Auto-refreshing every 30s</span>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-800/50 text-gray-400 text-sm">
              <tr>
                <th className="p-4 font-medium">Time</th>
                <th className="p-4 font-medium">Category</th>
                <th className="p-4 font-medium">Action</th>
                <th className="p-4 font-medium">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {loading ? (
                <tr><td colSpan={4} className="p-8 text-center">Loading...</td></tr>
              ) : logs.length > 0 ? (
                logs.map(log => (
                  <tr key={log.id} className="hover:bg-gray-800/30">
                    <td className="p-4 text-gray-400 whitespace-nowrap">{new Date(log.createdAt).toLocaleString()}</td>
                    <td className="p-4"><Badge variant="outline">{log.category}</Badge></td>
                    <td className="p-4 text-gray-300 font-medium">{log.action}</td>
                    <td className="p-4 text-gray-400 text-sm"><pre>{JSON.stringify(log.details)}</pre></td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan={4} className="p-8 text-center text-gray-500">No logs found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
