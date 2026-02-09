// Voice Interface UI
const VoiceAssistant = () => (
  <div className="voice-assistant">
    <button className="mic-button">🎙️ Tap & Speak</button>

    {/* Visual feedback */}
    <div className="voice-feedback">
      <div className="sound-waves">{/* Animated waves when listening */}</div>
      <div className="transcript">"Finding bullish stocks with RSI below 30..."</div>
    </div>

    {/* Suggested commands */}
    <div className="suggested-commands">
      <button>"Show defensive stocks"</button>
      <button>"Check market sentiment"</button>
      <button>"Paper trade top pick"</button>
    </div>
  </div>
);

export default VoiceAssistant;
