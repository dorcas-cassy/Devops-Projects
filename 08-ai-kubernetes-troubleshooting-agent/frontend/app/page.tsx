"use client";

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("System Status: Ready");
  return (
    <main>
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <section className="shell">
        <header className="topbar">
          <div className="brand"><span className="brand-mark">K</span><span>kubeflow</span></div>
          <div className="environment"><span className="pulse" />Cluster connection ready</div>
        </header>
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="eyebrow"><span />ON-DEMAND CLUSTER DIAGNOSIS</p>
            <h1>Understand your cluster.<br /><em>Act with confidence.</em></h1>
            <p className="subtitle">AI Kubernetes Agent gathers the signals your team needs to investigate incidents with clarity.</p>
            <div className="actions">
              <button onClick={() => setMessage("Investigation is not implemented yet")}>Investigate Cluster <span>→</span></button>
              <p className="status"><span className="status-dot" />{message}</p>
            </div>
          </div>
          <aside className="signal-card" aria-label="System signal summary">
            <div className="signal-header"><span>LIVE SYSTEM SIGNALS</span><i>●</i></div>
            <div className="signal-row"><b className="icon healthy">✓</b><div><strong>Cluster status</strong><small>Ready for investigation</small></div><em>Healthy</em></div>
            <div className="signal-row"><b className="icon cyan">⌘</b><div><strong>Evidence engine</strong><small>Pods, logs, events and networking</small></div><em>Standing by</em></div>
            <div className="signal-row"><b className="icon violet">✦</b><div><strong>AI diagnosis</strong><small>Senior SRE reasoning workflow</small></div><em>Available</em></div>
          </aside>
        </div>
        <footer><span>Built for focused Kubernetes troubleshooting</span><span>FASTAPI · KUBECTL · OPENROUTER</span></footer>
      </section>
    </main>
  );
}
