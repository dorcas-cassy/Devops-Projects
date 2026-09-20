"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createBrowserClient } from "@insforge/sdk/ssr";
import { signIn, signOut, signUp, verifyEmail } from "./actions";

type User = { id: string; email: string };
type History = { id: string; cluster_context: string; status: string; root_cause: string | null; namespace: string | null; confidence: number | null; created_at: string };
type Diagnosis = { root_cause?: string; explanation?: string; suggested_fix?: string; kubectl_commands?: string[]; confidence?: number; confidence_reasoning?: string; error?: string; available?: boolean };
type Result = { status: string; context: string; diagnosis: Diagnosis | null; investigation: Record<string, unknown> };
type Event = { stage: string; id?: string; error?: string; result?: Result };

const stages = [
  ["checking_pods", "Checking Pods"], ["reading_logs", "Reading Logs"],
  ["analyzing_events", "Analyzing Events"], ["inspecting_deployments", "Inspecting Deployments"],
  ["checking_networking", "Checking Networking"], ["ai_reasoning", "AI Reasoning"],
] as const;

function messageFromResponse(value: unknown, fallback: string) {
  if (value && typeof value === "object") {
    const item = value as { error?: string; detail?: string };
    return item.error ?? item.detail ?? fallback;
  }
  return fallback;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [mode, setMode] = useState<"sign-in" | "sign-up" | "verify">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [otp, setOtp] = useState("");
  const [authError, setAuthError] = useState("");
  const [authBusy, setAuthBusy] = useState(false);
  const [contexts, setContexts] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [clusterError, setClusterError] = useState("");
  const [history, setHistory] = useState<History[]>([]);
  const [historyError, setHistoryError] = useState("");
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const clientRef = useRef<ReturnType<typeof createBrowserClient> | null>(null);

  const loadHistory = useCallback(async () => {
    const client = clientRef.current;
    if (!client) return;
    const { data, error: readError } = await client.database.from("investigations")
      .select("id, cluster_context, status, root_cause, namespace, confidence, created_at")
      .order("created_at", { ascending: false }).limit(10);
    if (readError) setHistoryError("Investigation history is unavailable. Check the InsForge migration.");
    else { setHistory((data ?? []) as History[]); setHistoryError(""); }
  }, []);

  useEffect(() => {
    let active = true;
    fetch("/api/session", { cache: "no-store" })
      .then(async response => response.json())
      .then(payload => { if (active) setUser(payload.user ?? null); })
      .catch(() => { if (active) setAuthError("Authentication service is unavailable."); })
      .finally(() => { if (active) setSessionLoading(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!user) return;
    const client = createBrowserClient();
    clientRef.current = client;
    let active = true;
    fetch("/api/clusters", { cache: "no-store" })
      .then(async response => {
        const payload = await response.json();
        if (!response.ok) throw new Error(messageFromResponse(payload, "Unable to list clusters."));
        return payload;
      })
      .then(payload => {
        if (!active) return;
        setContexts(payload.contexts ?? []);
        setSelected(payload.current_context || payload.contexts?.[0] || "");
        setClusterError("");
      })
      .catch(reason => { if (active) setClusterError(reason.message); });
    void loadHistory();
    const channel = `investigations:${user.id}`;
    const onProgress = (payload: { stage?: string; meta?: { channel?: string } }) => {
      if (payload.meta?.channel === channel && payload.stage) setStage(payload.stage);
    };
    client.realtime.on("investigation_progress", onProgress);
    void client.realtime.subscribe(channel).then(response => {
      if (active && !response.ok) setHistoryError("Realtime progress is unavailable; request progress will still appear.");
    });
    return () => {
      active = false;
      client.realtime.off("investigation_progress", onProgress);
      client.realtime.unsubscribe(channel);
      client.realtime.disconnect();
      clientRef.current = null;
    };
  }, [user, loadHistory]);

  async function submitAuth(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true); setAuthError("");
    try {
      if (mode === "verify") {
        const response = await verifyEmail(email, otp);
        if (!response.ok) throw new Error(response.message || "Verification failed.");
        window.location.reload();
      } else if (mode === "sign-up") {
        const response = await signUp(email, password, name);
        if (!response.ok) throw new Error(response.message || "Account creation failed.");
        if (response.needsVerification) setMode("verify");
        else window.location.reload();
      } else {
        const response = await signIn(email, password);
        if (!response.ok) throw new Error(response.message || "Sign-in failed.");
        window.location.reload();
      }
    } catch (reason) {
      setAuthError(reason instanceof Error ? reason.message : "Authentication failed.");
    } finally { setAuthBusy(false); }
  }

  async function investigate() {
    if (!selected || busy) return;
    setBusy(true); setError(""); setResult(null); setStage("starting");
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 120_000);
    try {
      const response = await fetch("/api/investigate", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context: selected }), signal: controller.signal,
      });
      if (!response.ok || !response.body) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(messageFromResponse(payload, "Investigation could not start."));
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let pending = "";
      let finished = false;
      const handle = (line: string) => {
        if (!line.trim()) return;
        const event: Event = JSON.parse(line);
        setStage(event.stage);
        if (event.stage === "error") { setError(event.error ?? "Investigation failed."); finished = true; }
        if (event.stage === "complete" && event.result) { setResult(event.result); finished = true; void loadHistory(); }
      };
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        pending += decoder.decode(value, { stream: true });
        const lines = pending.split("\n"); pending = lines.pop() ?? "";
        for (const line of lines) handle(line);
      }
      if (pending.trim()) handle(pending);
      if (!finished) throw new Error("Investigation ended before a result was returned.");
    } catch (reason) {
      setError(controller.signal.aborted ? "Investigation timed out. Check cluster access and try again." : reason instanceof Error ? reason.message : "Investigation failed.");
      setStage("error");
    } finally { clearTimeout(timer); setBusy(false); void loadHistory(); }
  }

  const currentIndex = stages.findIndex(([id]) => id === stage);
  return (
    <main className="app-main">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" />
      <section className="shell dashboard-shell">
        <header className="topbar">
          <div className="brand"><span className="brand-mark">K</span><span>AI Kubernetes Agent</span></div>
          {user && <div className="account"><span>{user.email}</span><button className="text-button" onClick={async () => { await signOut(); window.location.reload(); }}>Sign out</button></div>}
        </header>
        {sessionLoading ? <div className="content"><p>Checking your session...</p></div> : !user ? (
          <div className="content auth-wrap">
            <p className="eyebrow">ON-DEMAND CLUSTER DIAGNOSIS</p>
            <h1>Understand your cluster.</h1>
            <p className="subtitle">Sign in to investigate Kubernetes and review past diagnoses.</p>
            <form className="auth-form" onSubmit={submitAuth}>
              <h2>{mode === "verify" ? "Verify your email" : mode === "sign-up" ? "Create account" : "Sign in"}</h2>
              {mode === "sign-up" && <label>Name<input value={name} onChange={event => setName(event.target.value)} required /></label>}
              <label>Email<input type="email" value={email} onChange={event => setEmail(event.target.value)} required disabled={mode === "verify"} /></label>
              {mode === "verify" ? <label>Verification code<input value={otp} onChange={event => setOtp(event.target.value)} inputMode="numeric" required /></label> :
                <label>Password<input type="password" value={password} onChange={event => setPassword(event.target.value)} required /></label>}
              {authError && <p className="error" role="alert">{authError}</p>}
              <button type="submit" disabled={authBusy}>{authBusy ? "Please wait..." : mode === "verify" ? "Verify email" : mode === "sign-up" ? "Create account" : "Sign in"}</button>
              {mode !== "verify" && <button className="text-button" type="button" onClick={() => { setAuthError(""); setMode(mode === "sign-in" ? "sign-up" : "sign-in"); }}>{mode === "sign-in" ? "Create an account" : "Already have an account? Sign in"}</button>}
            </form>
          </div>
        ) : (
          <div className="content">
            <p className="eyebrow">ON-DEMAND CLUSTER DIAGNOSIS</p>
            <h1>Investigate your cluster.</h1>
            <p className="subtitle">Choose a context from your local kubeconfig. The agent collects read-only evidence and suggests a fix.</p>
            <div className="control-row">
              <label className="cluster-field">Kubernetes cluster ({contexts.length} available)
                <select className="cluster-list" size={Math.min(Math.max(contexts.length, 1), 5)} value={selected} onChange={event => setSelected(event.target.value)} disabled={busy || !contexts.length}>
                  {contexts.map(context => <option key={context} value={context}>{context}</option>)}
                </select>
              </label>
              <button onClick={investigate} disabled={!selected || busy}>{busy ? "Investigating Kubernetes Cluster..." : "Investigate Cluster"}</button>
            </div>
            {clusterError && <p className="error" role="alert">{clusterError}</p>}
            <section className="panel" aria-live="polite">
              <h2>Investigation status</h2>
              {!stage && <p className="muted">Ready when you are.</p>}
              {stage && <ol className="progress-list">{stages.map(([id, label], index) => <li key={id} className={stage === "complete" || (currentIndex >= 0 && index < currentIndex) ? "done" : id === stage ? "active" : ""}>{stage === "complete" || (currentIndex >= 0 && index < currentIndex) ? "✓" : id === stage ? "●" : "○"} {label}</li>)}</ol>}
              {error && <p className="error" role="alert">{error}</p>}
            </section>
            {result && <section className="panel diagnosis-card">
              <h2>Diagnosis</h2>
              {result.status === "healthy" ? <p>No critical Kubernetes issues detected. Cluster appears healthy.</p> : result.diagnosis?.available === false ? <p className="error">{result.diagnosis.error}</p> : result.diagnosis ? <>
                <h3>{result.diagnosis.root_cause}</h3>
                <p>{result.diagnosis.explanation}</p>
                <h4>Suggested fix</h4><p>{result.diagnosis.suggested_fix}</p>
                <h4>Suggested kubectl commands</h4><pre>{(result.diagnosis.kubectl_commands ?? []).join("\n") || "No command suggested."}</pre>
                <p className="confidence">Confidence: {result.diagnosis.confidence ?? "—"}%</p>
                <p className="muted">{result.diagnosis.confidence_reasoning}</p>
              </> : null}
            </section>}
            <section className="panel">
              <h2>Recent investigations</h2>
              {historyError && <p className="error">{historyError}</p>}
              {!history.length && !historyError && <p className="muted">No investigations yet.</p>}
              {!!history.length && <div className="table-wrap"><table><thead><tr><th>When</th><th>Cluster</th><th>Root cause</th><th>Namespace</th><th>Confidence</th><th>Status</th></tr></thead><tbody>{history.map(item => <tr key={item.id}><td>{new Date(item.created_at).toLocaleString()}</td><td>{item.cluster_context}</td><td>{item.root_cause ?? "—"}</td><td>{item.namespace ?? "—"}</td><td>{item.confidence == null ? "—" : `${item.confidence}%`}</td><td>{item.status}</td></tr>)}</tbody></table></div>}
            </section>
          </div>
        )}
        <footer><span>Read-only investigation. Suggested commands are never run automatically.</span><span>FASTAPI · KUBECTL · INSFORGE</span></footer>
      </section>
    </main>
  );
}
