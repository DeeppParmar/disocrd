'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function SettingsPage({ params }: { params: { guildId: string } }) {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/guilds/${params.guildId}/settings`)
      .then(res => res.json())
      .then(data => setConfig(data || {}));
  }, [params.guildId]);

  const handleSave = async () => {
    setSaving(true);
    setStatus(null);
    try {
      const res = await fetch(`/api/guilds/${params.guildId}/settings`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prefix: config.prefix, language: config.language, logChannelId: config.logChannelId ? Number(config.logChannelId) : null })
      });
      if (res.ok) setStatus('success');
      else setStatus('error');
    } catch {
      setStatus('error');
    }
    setSaving(false);
    setTimeout(() => setStatus(null), 3000);
  };

  if (!config) return <div className="animate-pulse">Loading settings...</div>;

  return (
    <div className="space-y-6 max-w-3xl">
      <h2 className="text-2xl font-bold">Server Settings</h2>

      <Card>
        <CardHeader><CardTitle>General Configuration</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Bot Prefix</label>
            <input 
              className="w-full bg-discord_darker border border-gray-700 rounded-md p-2 text-white" 
              value={config.prefix || ''} 
              onChange={e => setConfig({...config, prefix: e.target.value})} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Language</label>
            <select 
              className="w-full bg-discord_darker border border-gray-700 rounded-md p-2 text-white"
              value={config.language || 'en'}
              onChange={e => setConfig({...config, language: e.target.value})}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Log Channel ID</label>
            <input 
              className="w-full bg-discord_darker border border-gray-700 rounded-md p-2 text-white" 
              value={config.logChannelId || ''} 
              onChange={e => setConfig({...config, logChannelId: e.target.value})} 
              placeholder="e.g. 123456789012345678"
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-4">
        <Button onClick={handleSave} disabled={saving}>{saving ? 'Saving...' : 'Save Settings'}</Button>
        {status === 'success' && <span className="text-green-500 text-sm">Settings saved successfully!</span>}
        {status === 'error' && <span className="text-red-500 text-sm">Failed to save settings.</span>}
      </div>
    </div>
  );
}
