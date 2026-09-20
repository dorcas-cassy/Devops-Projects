"use server";

import { cookies } from "next/headers";
import { createAuthActions } from "@insforge/sdk/ssr";

export async function signIn(email: string, password: string) {
  const auth = createAuthActions({ cookies: await cookies() });
  const { data, error } = await auth.signInWithPassword({ email, password });
  return { ok: Boolean(data?.user) && !error, message: error?.message ?? "" };
}

export async function signUp(email: string, password: string, name: string) {
  const auth = createAuthActions({ cookies: await cookies() });
  const { data, error } = await auth.signUp({ email, password, name });
  return {
    ok: !error,
    needsVerification: Boolean(data?.requireEmailVerification),
    message: error?.message ?? "",
  };
}

export async function verifyEmail(email: string, otp: string) {
  const auth = createAuthActions({ cookies: await cookies() });
  const { data, error } = await auth.verifyEmail({ email, otp });
  return { ok: Boolean(data?.user) && !error, message: error?.message ?? "" };
}

export async function signOut() {
  const auth = createAuthActions({ cookies: await cookies() });
  await auth.signOut();
}
