import { useMemo, useState } from 'react';
import HourlyChart from './components/HourlyChart';
import RegionSelector from './components/RegionSelector';
import TodaySummary from './components/TodaySummary';
import WeekForecast from './components/WeekForecast';
import { weatherData } from './data/mockWeather';

const regionOptions = Object.keys(weatherData);

function App() {
  const [selectedRegion, setSelectedRegion] = useState(regionOptions[0]);

  const currentWeather = useMemo(
    () => weatherData[selectedRegion],
    [selectedRegion]
  );

  return (
    <div className="app-shell">
      <div className="app-overlay" />
      <main className="dashboard">
        <header className="hero">
          <div>
            <p className="eyebrow">Day 007</p>
            <h1>Weather Board</h1>
            <p className="hero-copy">
              地域ごとの今日の天気、7日間予報、24時間の気温と降水確率を
              一画面で確認できるモックダッシュボードです。
            </p>
          </div>
          <div className="hero-badge">
            <span>{currentWeather.label}</span>
            <strong>{currentWeather.today.condition}</strong>
          </div>
        </header>

        <RegionSelector
          regions={regionOptions}
          selectedRegion={selectedRegion}
          onSelect={setSelectedRegion}
        />

        <TodaySummary region={currentWeather} />

        <section className="content-grid">
          <WeekForecast forecast={currentWeather.weekly} />
          <HourlyChart hourly={currentWeather.hourly} label={currentWeather.label} />
        </section>
      </main>
    </div>
  );
}

export default App;
