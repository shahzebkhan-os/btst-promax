// Stock Card Component
const StockCard = ({ stock }) => (
  <div className="stock-card">
    {/* HEADER: Quick glance */}
    <div className="card-header">
      <span className="stock-symbol">{stock.symbol}</span>
      <span
        className="confidence-badge"
        style={{
          backgroundColor:
            stock.confidence > 80
              ? '#10B981'
              : stock.confidence > 65
              ? '#F59E0B'
              : '#EF4444',
        }}
      >
        {stock.confidence}% Confidence
      </span>
    </div>

    {/* COMPANY INFO */}
    <div className="company-info">
      <h3>{stock.name}</h3>
      <span className="sector-tag">{stock.sector}</span>
      <span className={`trend-tag ${stock.trend}`}>
        {stock.trend === 'bullish' ? '📈' : '📉'} {stock.trend}
      </span>
    </div>

    {/* PRICE ACTION */}
    <div className="price-action">
      <div className="current-price">
        <span className="price">₹{stock.price.toLocaleString()}</span>
        <span className={`change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
          {stock.change >= 0 ? '▲' : '▼'} {Math.abs(stock.change)}%
        </span>
      </div>
      <div className="price-range">
        <small>
          Day Range: ₹{stock.low} - ₹{stock.high}
        </small>
      </div>
    </div>

    {/* TRADE SETUP - VISUAL */}
    <div className="trade-visual">
      <div className="levels-bar">
        <div className="level stop-loss" style={{ left: '10%' }}>
          <span>SL: ₹{stock.stopLoss}</span>
        </div>
        <div className="level entry" style={{ left: '40%', right: '40%' }}>
          <span>
            Entry: ₹{stock.entryLow} - ₹{stock.entryHigh}
          </span>
        </div>
        <div className="level target" style={{ left: '80%' }}>
          <span>Target: ₹{stock.target}</span>
        </div>
      </div>
    </div>

    {/* KEY METRICS - GRID */}
    <div className="metrics-grid">
      <div className="metric">
        <label>Expected Return</label>
        <value className="positive">+{stock.expectedReturn}%</value>
      </div>
      <div className="metric">
        <label>Risk-Reward</label>
        <value>1:{stock.riskReward}</value>
      </div>
      <div className="metric">
        <label>Holding Period</label>
        <value>{stock.holdingPeriod} days</value>
      </div>
      <div className="metric">
        <label>Volatility</label>
        <value className={stock.volatility > 30 ? 'warning' : ''}>
          {stock.volatility}%
        </value>
      </div>
    </div>

    {/* QUICK ACTIONS */}
    <div className="card-actions">
      <button className="btn-primary">📊 View Detailed Analysis</button>
      <button className="btn-secondary">📝 Paper Trade</button>
      <button className="btn-icon">⭐ Add to Watchlist</button>
    </div>

    {/* ONE-CLICK INFO EXPANSION */}
    <div className="expand-section">
      <button className="expand-btn">▼ Why this pick? (AI Explanation)</button>
      {/* Expands to show:
          - Top 3 reasons from AI
          - Technical setup summary
          - Risk factors
      */}
    </div>
  </div>
);

export default StockCard;
