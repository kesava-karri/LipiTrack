import { useState, useEffect } from 'react';
import axios from 'axios';
import SummaryCard from './SummaryCard';
import LDLTrendChart from './LDLTrendChart';

const API_BASE = 'http://127.0.0.1:8000';

export default function Dashboard() {
  const [userId, setUserId] = useState(1);
  const [users, setUsers] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchSummary(userId);
  }, [userId]);

  async function fetchUsers() {
    try {
      const res = await axios.get(`${API_BASE}/users/`);
      setUsers(res.data || []);
      // Default to first user returned
      if (res.data?.length) setUserId(res.data[1].id);
    } catch (err) {
      console.error('Failed fetching users:', err);
    }
  }

  async function fetchSummary(id) {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/users/${id}/summary/`);
      setSummary(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <label style={{ marginRight: 8 }}>User ID:</label>
        <select
          value={userId}
          onChange={(e) => setUserId(Number(e.target.value))}
        >
          {users.length === 0 ? (
            <option value={1}>1</option>
          ) : (
            users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.id} - {u.full_name ?? u.email}
              </option>
            ))
          )}
        </select>
        <button onClick={() => fetchSummary(userId)} style={{ marginLeft: 8 }}>
          Refresh
        </button>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red' }}>Error</div>}

      {summary && (
        <div
          style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}
        >
          <div>
            <SummaryCard
              latest={summary.latest_lab}
              last30={summary.last_30_days}
            />
          </div>
          <div>
            <LDLTrendChart trend={summary.trend_last5 || []} />
          </div>
        </div>
      )}
    </div>
  );
}
