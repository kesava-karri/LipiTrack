import {
  CartesianGrid,
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

/**
 *
 * @param {Array} trend - lab result objects
 */
export default function LDLTrendChart({ trend }) {
  const data = (trend || []).map((r) => ({
    date: r.test_date,
    ldl: r.ldl,
  }));

  if (!data.length) return <div>No trend data available.</div>;

  return (
    <div
      style={{
        border: '1px solid $ddd',
        padding: 16,
        borderRadius: 8,
        background: '#fff',
      }}
    >
      <h3>LDL Trend</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            label={{ value: 'Date', position: 'insideBottom', dy: 10 }}
            dataKey="date"
            tickFormatter={(d) => d.slice(5)} // "MM-DD"
          />
          <YAxis
            label={{ value: 'LDL (mg/dL)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="ldl"
            stroke="#8884d8"
            strokeWidth={2}
            dot
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
