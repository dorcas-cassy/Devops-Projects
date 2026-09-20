import { NextResponse } from "next/server";
import { insforgeServer } from "../../lib/insforge/server";

export async function GET() {
  const insforge = await insforgeServer();
  const { data } = await insforge.auth.getCurrentUser();
  if (!data?.user) return NextResponse.json({ error: "Sign in to view clusters." }, { status: 401 });
  const token = process.env.BACKEND_INTERNAL_TOKEN;
  if (!token) return NextResponse.json({ error: "Backend authentication is not configured." }, { status: 503 });
  try {
    const response = await fetch(`${process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000"}/clusters`, {
      headers: { "X-Internal-Token": token }, cache: "no-store",
    });
    const payload = await response.json();
    return NextResponse.json(response.ok ? payload : { error: payload.detail ?? "Unable to list clusters." }, { status: response.status });
  } catch {
    return NextResponse.json({ error: "Unable to contact the investigation backend." }, { status: 503 });
  }
}
