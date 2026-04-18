function TodaySummary({ region }) {
  const { today, label } = region;

  return (
    <section className="panel today-summary">
      <article className="summary-main">
        <div className="weather-icon" aria-hidden="true">
          {today.icon}
        </div>
        <div>
          <h2>{label}の今日</h2>
          <p>{today.condition}</p>
        </div>
      </article>

      <article className="summary-metric">
        <span className="metric-label">最高 / 最低気温</span>
        <div className="metric-value">
          {today.maxTemp}° / {today.minTemp}°
        </div>
      </article>

      <article className="summary-metric">
        <span className="metric-label">降水確率</span>
        <div className="metric-value">{today.precipitation}%</div>
      </article>

      <article className="summary-metric">
        <span className="metric-label">風速</span>
        <div className="metric-value">{today.windSpeed} m/s</div>
      </article>

      <article className="summary-metric">
        <span className="metric-label">体感メモ</span>
        <div className="metric-value">{today.condition}</div>
      </article>
    </section>
  );
}

export default TodaySummary;
