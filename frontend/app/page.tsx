'use client';
import Chatbot from './components/Chatbot';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Incident {
  id: number;
  event_id: string;
  event_type: string;
  severity: string | null;
  status: string;
  source_ip: string;
  target_host: string;
  created_at: string;
  is_duplicate: boolean;
  is_correlated: boolean;
}

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const incidentsRes = await axios.get(`${API_URL}/api/incidents?limit=50`);
      setIncidents(incidentsRes.data);
      const statsRes = await axios.get(`${API_URL}/api/incidents/stats`);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch:', error);
    } finally {
      setLoading(false);
    }
  };

  const severityColors: Record<string, string> = {
    CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308',
    LOW: '#84cc16', INFO: '#3b82f6', UNKNOWN: '#6b7280',
  };

  const getSeverityColor = (severity: string | null) => 
    severityColors[severity || 'UNKNOWN'] || '#6b7280';

  const severityData = stats?.by_severity ? 
    Object.entries(stats.by_severity).map(([name, value]: [string, any]) => ({
      name, value, fill: severityColors[name]
    })) : [];

  const eventTypeData = stats?.by_event_type ? 
    Object.entries(stats.by_event_type).map(([name, value]: [string, any]) => ({name, value})) : [];

  if (loading) return <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-5xl font-bold mb-2">SOC Dashboard</h1>
        <p className="text-gray-400">AI-Powered Threat Analysis</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total', value: stats?.total_incidents, color: 'text-blue-400' },
          { label: 'Critical', value: stats?.by_severity?.CRITICAL || 0, color: 'text-red-500' },
          { label: 'Duplicates', value: incidents.filter(i => i.is_duplicate).length, color: 'text-yellow-500' },
          { label: 'Correlated', value: incidents.filter(i => i.is_correlated).length, color: 'text-green-500' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 rounded-lg p-6">
            <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Severity Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={severityData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label>
                {severityData.map((e: any, i: number) => <Cell key={i} fill={e.fill} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Event Types</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={eventTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b' }} />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 overflow-x-auto">
        <h2 className="text-xl font-bold mb-4">Recent Incidents</h2>
        <table className="w-full text-sm">
          <thead className="border-b border-slate-700">
            <tr>
              <th className="text-left py-2 px-4">Event ID</th>
              <th className="text-left py-2 px-4">Type</th>
              <th className="text-left py-2 px-4">Severity</th>
              <th className="text-left py-2 px-4">Source IP</th>
              <th className="text-left py-2 px-4">Target</th>
              <th className="text-left py-2 px-4">Tags</th>
            </tr>
          </thead>
          <tbody>
            {incidents.slice(0, 15).map((i) => (
              <tr key={i.id} className="border-b border-slate-800 hover:bg-slate-800">
                <td className="py-2 px-4 text-blue-400 font-mono">{i.event_id}</td>
                <td className="py-2 px-4">{i.event_type}</td>
                <td className="py-2 px-4">
                  <span style={{ color: getSeverityColor(i.severity) }} className="font-bold">
                    {i.severity || 'UNKNOWN'}
                  </span>
                </td>
                <td className="py-2 px-4 font-mono text-xs">{i.source_ip}</td>
                <td className="py-2 px-4">{i.target_host}</td>
                <td className="py-2 px-4">
                  <div className="flex gap-1">
                    {i.is_duplicate && <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs">DUP</span>}
                    {i.is_correlated && <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs">CORR</span>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Buttons */}
      <div className="mt-8 flex gap-4">
        <button onClick={() => window.open(`${API_URL}/api/export/csv`)} className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded font-bold">
          📥 CSV
        </button>
        <button onClick={() => window.open(`${API_URL}/api/export/json`)} className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-bold">
          📥 JSON
        </button>
        <button onClick={fetchData} className="bg-slate-700 hover:bg-slate-600 px-6 py-2 rounded font-bold">
          🔄 Refresh
        </button>
      </div>


    {/* Chatbot Sidebar */}
      <Chatbot />
    </div>
  );
}
