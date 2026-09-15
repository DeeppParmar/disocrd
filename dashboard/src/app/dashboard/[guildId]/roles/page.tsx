'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

export default function RolesPage({ params }: { params: { guildId: string } }) {
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/guilds/${params.guildId}/roles`)
      .then(res => res.json())
      .then(data => {
        setRoles(data);
        setLoading(false);
      });
  }, [params.guildId]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Role Mappings</h2>
      <p className="text-gray-400">View how Discord roles map to bot features.</p>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-800/50 text-gray-400 text-sm">
              <tr>
                <th className="p-4 font-medium">Role ID</th>
                <th className="p-4 font-medium">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {loading ? (
                <tr><td colSpan={2} className="p-4"><Skeleton className="h-8 w-full" /></td></tr>
              ) : roles.length > 0 ? (
                roles.map(r => (
                  <tr key={r.id} className="hover:bg-gray-800/30">
                    <td className="p-4 text-gray-300">{r.roleId}</td>
                    <td className="p-4"><Badge variant="outline">{r.type}</Badge></td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan={2} className="p-8 text-center text-gray-500">No role mappings found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
