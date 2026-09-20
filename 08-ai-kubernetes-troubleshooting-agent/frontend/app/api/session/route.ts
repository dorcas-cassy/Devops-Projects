import { NextResponse } from "next/server";
import { insforgeServer } from "../../lib/insforge/server";

export async function GET() {
  try {
    const insforge = await insforgeServer();
    const { data, error } = await insforge.auth.getCurrentUser();
    if (error || !data?.user) return NextResponse.json({ user: null });
    return NextResponse.json({ user: { id: data.user.id, email: data.user.email } });
  } catch {
    return NextResponse.json({ user: null, error: "Authentication is unavailable." }, { status: 503 });
  }
}
