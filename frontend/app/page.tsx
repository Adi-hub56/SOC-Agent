'use client';
import Chatbot from './components/Chatbot';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

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
  const { logout } = useAuth();
  const router = useRouter();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      const [incidentsRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/api/incidents`),
        axios.get(`${API_URL}/api/incidents/stats`)
      ]);
      setIncidents(incidentsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/auth');
  };

  if (loading) return <div className="text-white p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">SOC Agent Dashboard</h1>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/settings')}
              className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded font-bold"
            >
              ⚙️ Settings
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-bold"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <p className="text-gray-400 mb-2">Total</p>
            <p className="text-3xl font-bold text-blue-500">{stats?.total_incidents || 0}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <p className="text-gray-400 mb-2">Critical</p>
            <p className="text-3xl font-bold text-red-500">{stats?.critical_count || 0}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <p className="text-gray-400 mb-2">Duplicates</p>
            <p className="text-3xl font-bold text-yellow-500">{stats?.duplicate_count || 0}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <p className="text-gray-400 mb-2">Correlated</p>
            <p className="text-3xl font-bold text-green-500">{stats?.correlated_count || 0}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8 mb-8">
          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <h2 className="text-xl font-bold mb-4">Severity Distribution</h2>
            {stats?.severity_distribution && (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.severity_distribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                  >
                    {stats.severity_distribution.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={['#ef4444', '#eab308', '#22c55e'][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="bg-slate-800 border border-slate-700 p-6 rounded">
            <h2 className="text-xl font-bold mb-4">Event Types</h2>
            {stats?.event_type_distribution && (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.event_type_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-8">
          <h2 className="text-xl font-bold mb-4">Recent Incidents</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="border-b border-slate-700">
                <tr>
                  <th className="pb-2">Event ID</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">Source IP</th>
                  <th className="pb-2">Target</th>
                  <th className="pb-2">Tags</th>
                </tr>
              </thead>
              <tbody>
                {incidents.slice(0, 10).map((incident) => (
                  <tr key={incident.id} className="border-b border-slate-700 hover:bg-slate-700">
                    <td className="py-2">{incident.event_id}</td>
                    <td className="py-2">{incident.event_type}</td>
                    <td className="py-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        incident.severity === 'high' ? 'bg-red-900 text-red-200' :
                        incident.severity === 'medium' ? 'bg-yellow-900 text-yellow-200' :
                        'bg-green-900 text-green-200'
                      }`}>
                        {incident.severity || 'N/A'}
                      </span>
                    </td>
                    <td className="py-2">{incident.source_ip}</td>
                    <td className="py-2">{incident.target_host}</td>
                    <td className="py-2">
                      {incident.is_duplicate && <span className="bg-yellow-900 text-yellow-200 px-2 py-1 rounded text-sm mr-1">Duplicate</span>}
                      {incident.is_correlated && <span className="bg-blue-900 text-blue-200 px-2 py-1 rounded text-sm">Correlated</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex gap-4 mb-8">
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-bold">📥 CSV</button>
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-bold">📋 JSON</button>
          <button onClick={fetchData} className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded font-bold">🔄 Refresh</button>
        </div>

        <Chatbot />
      </div>
    </div>
  );
}
