function WeekForecast({ forecast }) {
  return (
    <section className="panel week-forecast">
      <h2 className="section-title">7日間予報</h2>
      <div className="forecast-grid">
        {forecast.map((day) => (
          <article key={day.day} className="forecast-card">
            <span className="forecast-day">{day.day}</span>
            <span className="forecast-icon" aria-hidden="true">
              {day.icon}
            </span>
            <div className="forecast-temps">
              <span className="forecast-high">{day.high}°</span>
              <span className="forecast-low">{day.low}°</span>
            </div>
            <p className="forecast-condition">{day.condition}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default WeekForecast;
