import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function HourlyChart({ hourly, label }) {
  return (
    <section className="panel hourly-chart">
      <h2 className="section-title">24時間チャート</h2>
      <div className="chart-stack">
        <div className="chart-card">
          <div className="chart-header">
            <h3>気温の推移</h3>
            <span>{label} / 24時間</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={hourly}>
              <CartesianGrid stroke="rgba(80, 130, 170, 0.14)" vertical={false} />
              <XAxis dataKey="time" stroke="#547690" tickLine={false} axisLine={false} />
              <YAxis
                stroke="#547690"
                tickLine={false}
                axisLine={false}
                unit="°"
                width={40}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: '16px',
                  border: '1px solid rgba(255,255,255,0.7)',
                  background: 'rgba(255,255,255,0.92)',
                }}
              />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#ff8d5b"
                strokeWidth={3}
                dot={{ r: 4, fill: '#ff8d5b' }}
                activeDot={{ r: 6 }}
                unit="°"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>降水確率</h3>
            <span>時間帯別</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={hourly}>
              <CartesianGrid stroke="rgba(80, 130, 170, 0.14)" vertical={false} />
              <XAxis dataKey="time" stroke="#547690" tickLine={false} axisLine={false} />
              <YAxis
                stroke="#547690"
                tickLine={false}
                axisLine={false}
                unit="%"
                width={40}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: '16px',
                  border: '1px solid rgba(255,255,255,0.7)',
                  background: 'rgba(255,255,255,0.92)',
                }}
              />
              <Bar
                dataKey="precipitation"
                fill="#4ba3e2"
                radius={[8, 8, 0, 0]}
                maxBarSize={36}
                unit="%"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

export default HourlyChart;
