'use client';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SettingsPage() {
  const { logout } = useAuth();
  const router = useRouter();
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  
  const [formData, setFormData] = useState({
    email: '',
    theme: 'dark',
    email_notifications: true,
    slack_webhook_url: '',
    slack_notifications: false,
  });

  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [showNewKey, setShowNewKey] = useState('');

  const [twoFAStatus, setTwoFAStatus] = useState<any>(null);
  const [showQRCode, setShowQRCode] = useState('');
  const [verifyCode, setVerifyCode] = useState('');
  const [disableCode, setDisableCode] = useState('');
  const [showBackupCodes, setShowBackupCodes] = useState<string[]>([]);

  const [sessions, setSessions] = useState<any[]>([]);
  
  const [alertRules, setAlertRules] = useState<any[]>([]);
  const [newRule, setNewRule] = useState({
    name: '',
    severity_threshold: 'high',
    event_type: '',
    action: 'email'
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }
    fetchAllData(token);
  }, [router]);

  const fetchAllData = async (token: string) => {
    try {
      const [settingsRes, keysRes, twoFARes, sessionsRes, rulesRes] = await Promise.all([
        axios.get(`${API_URL}/user/settings`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api-keys/`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/2fa/status`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/sessions/`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/alert-rules/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setSettings(settingsRes.data);
      setFormData({
        email: settingsRes.data.email,
        theme: settingsRes.data.theme,
        email_notifications: settingsRes.data.email_notifications,
        slack_webhook_url: settingsRes.data.slack_webhook_url || '',
        slack_notifications: settingsRes.data.slack_notifications,
      });
      setApiKeys(keysRes.data);
      setTwoFAStatus(twoFARes.data);
      setSessions(sessionsRes.data);
      setAlertRules(rulesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/user/settings`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Settings saved! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('Passwords do not match!');
      return;
    }

    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/user/change-password`, 
        {
          old_password: passwordData.old_password,
          new_password: passwordData.new_password,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage('Password changed! ✅');
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleCreateApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(`${API_URL}/api-keys/`, 
        { name: newKeyName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowNewKey(res.data.key);
      setNewKeyName('');
      const updatedKeys = await axios.get(`${API_URL}/api-keys/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys(updatedKeys.data);
      setMessage('API Key created! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleRevokeApiKey = async (keyId: number) => {
    if (!confirm('Delete this key?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api-keys/${keyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const updatedKeys = await axios.get(`${API_URL}/api-keys/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApiKeys(updatedKeys.data);
      setMessage('Key deleted! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleLogoutSession = async (sessionId: number) => {
    if (!confirm('Logout from this device?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/sessions/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const updatedSessions = await axios.get(`${API_URL}/sessions/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(updatedSessions.data);
      setMessage('Session logged out! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleCreateAlertRule = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/alert-rules/`, newRule, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewRule({ name: '', severity_threshold: 'high', event_type: '', action: 'email' });
      const updatedRules = await axios.get(`${API_URL}/alert-rules/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlertRules(updatedRules.data);
      setMessage('Alert rule created! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAlertRule = async (ruleId: number) => {
    if (!confirm('Delete this rule?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/alert-rules/${ruleId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const updatedRules = await axios.get(`${API_URL}/alert-rules/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlertRules(updatedRules.data);
      setMessage('Rule deleted! ✅');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleSetup2FA = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(`${API_URL}/2fa/setup`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowQRCode(res.data.qr_code);
      setMessage('Scan QR code');
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleVerify2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/2fa/verify`, 
        { code: verifyCode },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const backupRes = await axios.get(`${API_URL}/2fa/backup-codes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowBackupCodes(backupRes.data.backup_codes);
      setMessage('2FA enabled! Save codes! ✅');
      setVerifyCode('');
      const statusRes = await axios.get(`${API_URL}/2fa/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTwoFAStatus(statusRes.data);
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleDisable2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirm('Disable 2FA?')) return;
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/2fa/disable`, 
        { code: disableCode },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage('2FA disabled! ✅');
      setDisableCode('');
      const statusRes = await axios.get(`${API_URL}/2fa/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTwoFAStatus(statusRes.data);
    } catch (error: any) {
      setMessage('Error: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/auth');
  };

  if (loading) return <div className="text-white p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-bold"
      >
        Logout
      </button>

      <div className="p-8 max-w-2xl mx-auto">
        <div className="flex gap-4 mb-8">
          <button onClick={() => router.push('/')} className="bg-slate-700 px-4 py-2 rounded">
            ← Dashboard
          </button>
          <h1 className="text-4xl font-bold">Settings</h1>
        </div>

        {message && (
          <div className={`p-4 rounded mb-6 ${message.includes('✅') ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
            {message}
          </div>
        )}

        {/* Profile */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">Profile</h2>
          <form onSubmit={handleSettingsSave} className="space-y-4">
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
            <select
              value={formData.theme}
              onChange={(e) => setFormData({...formData, theme: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
            <button type="submit" disabled={saving} className="bg-blue-600 px-4 py-2 rounded font-bold disabled:opacity-50">
              Save
            </button>
          </form>
        </div>

        {/* Notifications */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">Notifications</h2>
          <form onSubmit={handleSettingsSave} className="space-y-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.email_notifications}
                onChange={(e) => setFormData({...formData, email_notifications: e.target.checked})}
              />
              <span>Email Notifications</span>
            </label>
            <input
              type="text"
              placeholder="Slack Webhook"
              value={formData.slack_webhook_url}
              onChange={(e) => setFormData({...formData, slack_webhook_url: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.slack_notifications}
                onChange={(e) => setFormData({...formData, slack_notifications: e.target.checked})}
              />
              <span>Slack Notifications</span>
            </label>
            <button type="submit" disabled={saving} className="bg-blue-600 px-4 py-2 rounded font-bold disabled:opacity-50">
              Save
            </button>
          </form>
        </div>

        {/* API Keys */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">API Keys</h2>
          {showNewKey && (
            <div className="bg-green-900 p-4 rounded mb-4">
              <p className="text-green-200 mb-2">Key:</p>
              <div className="bg-slate-900 p-3 rounded font-mono text-sm break-all mb-2">{showNewKey}</div>
              <button onClick={() => setShowNewKey('')} className="bg-green-600 px-3 py-1 rounded text-sm">
                ✓ Copied
              </button>
            </div>
          )}
          <form onSubmit={handleCreateApiKey} className="mb-6 p-4 bg-slate-700 rounded">
            <input
              type="text"
              placeholder="Key name"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="w-full bg-slate-600 border border-slate-500 rounded px-3 py-2 text-white mb-3"
              required
            />
            <button type="submit" disabled={saving} className="bg-blue-600 px-4 py-2 rounded font-bold w-full">
              Generate
            </button>
          </form>
          {apiKeys.length > 0 && (
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-600">
                <tr>
                  <th className="pb-2">Name</th>
                  <th className="pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((key) => (
                  <tr key={key.id} className="border-b border-slate-700">
                    <td className="py-2">{key.name}</td>
                    <td className="py-2">
                      <button onClick={() => handleRevokeApiKey(key.id)} className="px-2 py-1 rounded text-xs bg-red-700">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* 2FA */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">2FA</h2>
          {twoFAStatus?.is_enabled ? (
            <div className="space-y-4">
              <div className="bg-green-900 p-3 rounded">✓ ENABLED</div>
              {showBackupCodes.length > 0 && (
                <div className="bg-slate-700 p-4 rounded">
                  <p className="text-gray-400 mb-2">Backup Codes:</p>
                  {showBackupCodes.map((code, i) => (
                    <p key={i} className="font-mono text-sm">{code}</p>
                  ))}
                </div>
              )}
              <form onSubmit={handleDisable2FA} className="space-y-3">
                <input
                  type="text"
                  placeholder="6-digit code"
                  value={disableCode}
                  onChange={(e) => setDisableCode(e.target.value)}
                  maxLength="6"
                  className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                  required
                />
                <button type="submit" disabled={saving} className="bg-red-600 px-4 py-2 rounded font-bold w-full">
                  Disable
                </button>
              </form>
            </div>
          ) : (
            <div className="space-y-4">
              {showQRCode ? (
                <div>
                  <img src={showQRCode} alt="QR" className="w-48 h-48 mx-auto mb-4" />
                  <form onSubmit={handleVerify2FA} className="space-y-3">
                    <input
                      type="text"
                      placeholder="6-digit code"
                      value={verifyCode}
                      onChange={(e) => setVerifyCode(e.target.value)}
                      maxLength="6"
                      className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                      required
                    />
                    <button type="submit" disabled={saving} className="bg-green-600 px-4 py-2 rounded font-bold w-full">
                      Verify
                    </button>
                  </form>
                </div>
              ) : (
                <button onClick={handleSetup2FA} disabled={saving} className="bg-blue-600 px-4 py-2 rounded font-bold w-full">
                  Enable 2FA
                </button>
              )}
            </div>
          )}
        </div>

        {/* Sessions */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">Active Sessions</h2>
          {sessions.length > 0 ? (
            <div className="space-y-3">
              {sessions.map((session) => (
                <div key={session.id} className="bg-slate-700 p-3 rounded flex justify-between items-center">
                  <div>
                    <p className="font-mono text-sm">{session.user_agent || 'Unknown device'}</p>
                    <p className="text-gray-400 text-sm">{session.ip_address || 'N/A'}</p>
                    <p className="text-gray-400 text-xs">{new Date(session.created_at).toLocaleDateString()}</p>
                  </div>
                  <button onClick={() => handleLogoutSession(session.id)} className="px-2 py-1 rounded text-sm bg-red-700">
                    Logout
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No active sessions</p>
          )}
        </div>

        {/* Alert Rules */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded mb-6">
          <h2 className="text-2xl font-bold mb-4">Alert Rules</h2>
          <form onSubmit={handleCreateAlertRule} className="mb-6 p-4 bg-slate-700 rounded space-y-3">
            <input
              type="text"
              placeholder="Rule name"
              value={newRule.name}
              onChange={(e) => setNewRule({...newRule, name: e.target.value})}
              className="w-full bg-slate-600 border border-slate-500 rounded px-3 py-2 text-white"
              required
            />
            <select
              value={newRule.severity_threshold}
              onChange={(e) => setNewRule({...newRule, severity_threshold: e.target.value})}
              className="w-full bg-slate-600 border border-slate-500 rounded px-3 py-2 text-white"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <input
              type="text"
              placeholder="Event type (optional)"
              value={newRule.event_type}
              onChange={(e) => setNewRule({...newRule, event_type: e.target.value})}
              className="w-full bg-slate-600 border border-slate-500 rounded px-3 py-2 text-white"
            />
            <select
              value={newRule.action}
              onChange={(e) => setNewRule({...newRule, action: e.target.value})}
              className="w-full bg-slate-600 border border-slate-500 rounded px-3 py-2 text-white"
            >
              <option value="email">Email</option>
              <option value="slack">Slack</option>
              <option value="both">Both</option>
            </select>
            <button type="submit" disabled={saving} className="bg-blue-600 px-4 py-2 rounded font-bold w-full">
              Create Rule
            </button>
          </form>
          {alertRules.length > 0 ? (
            <div className="space-y-3">
              {alertRules.map((rule) => (
                <div key={rule.id} className="bg-slate-700 p-3 rounded flex justify-between items-center">
                  <div>
                    <p className="font-bold">{rule.name}</p>
                    <p className="text-gray-400 text-sm">{rule.severity_threshold.toUpperCase()} • {rule.action}</p>
                  </div>
                  <button onClick={() => handleDeleteAlertRule(rule.id)} className="px-2 py-1 rounded text-sm bg-red-700">
                    Delete
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No rules yet</p>
          )}
        </div>

        {/* Password */}
        <div className="bg-slate-800 border border-slate-700 p-6 rounded">
          <h2 className="text-2xl font-bold mb-4">Password</h2>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <input
              type="password"
              placeholder="Old"
              value={passwordData.old_password}
              onChange={(e) => setPasswordData({...passwordData, old_password: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              required
            />
            <input
              type="password"
              placeholder="New"
              value={passwordData.new_password}
              onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              required
            />
            <input
              type="password"
              placeholder="Confirm"
              value={passwordData.confirm_password}
              onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              required
            />
            <button type="submit" disabled={saving} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-bold">
              Change
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
