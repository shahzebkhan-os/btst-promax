import './App.css';
import '../../styles.css';
import StockCard from './components/StockCard';
import VoiceAssistant from './components/VoiceAssistant';

const sampleStock = {
  symbol: 'RELIANCE',
  name: 'Reliance Industries',
  sector: 'Energy',
  trend: 'bullish',
  confidence: 87,
  price: 2452,
  change: 2.3,
  low: 2420,
  high: 2480,
  stopLoss: 2420,
  entryLow: 2450,
  entryHigh: 2470,
  target: 2550,
  expectedReturn: 3.2,
  riskReward: 2.1,
  holdingPeriod: 1,
  volatility: 24,
};

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>BTST PROMAX – UX Preview</h1>
        <p>3‑Click Trading Decisions · Glanceable Insights</p>
      </header>

      <main className="main">
        <section className="section">
          <h2>Today’s Top Pick</h2>
          <StockCard stock={sampleStock} />
        </section>

        <section className="section">
          <h2>Voice Assistant</h2>
          <VoiceAssistant />
        </section>
      </main>
    </div>
  );
}

export default App;
