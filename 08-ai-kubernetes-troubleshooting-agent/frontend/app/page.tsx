"use client";

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("System Status: Ready");
  return <main><section><p className="eyebrow">ON-DEMAND CLUSTER DIAGNOSIS</p><h1>AI Kubernetes Agent</h1><p className="subtitle">Troubleshoot Kubernetes with AI</p><button onClick={() => setMessage("Investigation is not implemented yet")}>Investigate Cluster</button><p className="status"><span />{message}</p></section></main>;
}
