import { NextResponse } from "next/server";
import { insforgeServer } from "../../lib/insforge/server";

type ProgressEvent = { stage: string; result?: Record<string, unknown>; error?: string };

export async function POST(request: Request) {
  const insforge = await insforgeServer();
  const { data: session } = await insforge.auth.getCurrentUser();
  if (!session?.user) return NextResponse.json({ error: "Sign in to investigate." }, { status: 401 });
  const token = process.env.BACKEND_INTERNAL_TOKEN;
  if (!token) return NextResponse.json({ error: "Backend authentication is not configured." }, { status: 503 });

  let context: string;
  try {
    const body = await request.json();
    context = String(body.context ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Choose a Kubernetes cluster." }, { status: 400 });
  }
  if (!context) return NextResponse.json({ error: "Choose a Kubernetes cluster." }, { status: 400 });

  const { data: row, error: insertError } = await insforge.database
    .from("investigations")
    .insert([{ cluster_context: context, status: "running", stage: "starting" }])
    .select("id")
    .single();
  if (insertError || !row) {
    return NextResponse.json({ error: "Investigation history is unavailable. Check the InsForge migration." }, { status: 503 });
  }
  const rowId = row.id;

  let upstream: Response;
  try {
    upstream = await fetch(`${process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000"}/investigate/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Internal-Token": token },
      body: JSON.stringify({ context }), cache: "no-store", signal: request.signal,
    });
  } catch {
    await insforge.database.from("investigations").update({ status: "error", stage: "error", error_message: "Investigation backend is unavailable." }).eq("id", rowId);
    return NextResponse.json({ error: "Unable to contact the investigation backend." }, { status: 503 });
  }
  if (!upstream.ok || !upstream.body) {
    const payload = await upstream.json().catch(() => ({}));
    const message = payload.detail ?? "Could not start the investigation.";
    await insforge.database.from("investigations").update({ status: "error", stage: "error", error_message: message }).eq("id", rowId);
    return NextResponse.json({ error: message }, { status: upstream.status });
  }

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      const reader = upstream.body!.getReader();
      const decoder = new TextDecoder();
      let pending = "";
      controller.enqueue(encoder.encode(JSON.stringify({ stage: "starting", id: rowId }) + "\n"));
      async function handleLine(line: string) {
        if (!line.trim()) return;
        const event: ProgressEvent = JSON.parse(line);
        if (event.stage === "complete" && event.result) {
          const diagnosis = event.result.diagnosis as Record<string, unknown> | null;
          const investigation = event.result.investigation as Record<string, unknown> | undefined;
          const pods = investigation?.pods as Record<string, unknown> | undefined;
          const firstPod = (pods?.problematic_pods as Array<Record<string, unknown>> | undefined)?.[0];
          await insforge.database.from("investigations").update({
            status: String(event.result.status ?? "success"), stage: "complete",
            root_cause: typeof diagnosis?.root_cause === "string" ? diagnosis.root_cause : null,
            namespace: typeof firstPod?.namespace === "string" ? firstPod.namespace : null,
            confidence: typeof diagnosis?.confidence === "number" ? diagnosis.confidence : null,
          }).eq("id", rowId);
        } else if (event.stage === "error") {
          await insforge.database.from("investigations").update({ status: "error", stage: "error", error_message: event.error ?? "Investigation failed." }).eq("id", rowId);
        } else {
          await insforge.database.from("investigations").update({ stage: event.stage }).eq("id", rowId);
        }
        controller.enqueue(encoder.encode(JSON.stringify(event) + "\n"));
      }
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          pending += decoder.decode(value, { stream: true });
          const lines = pending.split("\n");
          pending = lines.pop() ?? "";
          for (const line of lines) await handleLine(line);
        }
        if (pending.trim()) await handleLine(pending);
      } catch {
        const message = "Investigation stopped before completion.";
        await insforge.database.from("investigations").update({ status: "error", stage: "error", error_message: message }).eq("id", rowId);
        controller.enqueue(encoder.encode(JSON.stringify({ stage: "error", error: message }) + "\n"));
      } finally {
        controller.close();
      }
    },
  });
  return new Response(stream, { headers: { "Content-Type": "application/x-ndjson", "Cache-Control": "no-store" } });
}
