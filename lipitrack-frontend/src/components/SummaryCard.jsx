export default function SummaryCard({ latest, last30 }) {
  if (!latest) {
    return <div className="card">No lab results found for this user.</div>;
  }

  return (
    <div className="card">
      <h2>Latest Lab Result</h2>
      <div>
        <strong>Test Date:</strong> {latest.test_date}
      </div>
      <div>
        <strong>LDL:</strong> {latest.ldl ?? '-'}
      </div>
      <div>
        <strong>HDL:</strong>
        {latest.hdl ?? '-'}
      </div>
      <div>
        <strong>Total Cholesterol:</strong> {latest.total_cholesterol ?? '-'}
      </div>
      <div style={{ marginTop: 12 }}>
        <h4>Last 30 days (averages)</h4>
        <div>
          <strong>Diet score:</strong>
          {last30.avg_diet_score ?? '-'}
        </div>
        <div>
          <strong>Exercise (min):</strong>
          {last30.avg_exercise_minutes ?? '-'}
        </div>
        <div>
          <strong>Sleep (hrs)</strong>
          {last30.avg_sleep_hours ?? '-'}
        </div>
        <div>
          <strong>Entries:</strong>
          {last30.entries_count ?? 0}
        </div>
      </div>
    </div>
  );
}
