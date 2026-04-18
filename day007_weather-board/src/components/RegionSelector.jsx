function RegionSelector({ regions, selectedRegion, onSelect }) {
  return (
    <section className="panel region-selector" aria-label="地域切り替え">
      <div className="region-tabs" role="tablist" aria-label="地域一覧">
        {regions.map((region) => (
          <button
            key={region}
            type="button"
            role="tab"
            aria-selected={selectedRegion === region}
            className={`region-tab ${selectedRegion === region ? 'is-active' : ''}`}
            onClick={() => onSelect(region)}
          >
            {region}
          </button>
        ))}
      </div>
    </section>
  );
}

export default RegionSelector;
