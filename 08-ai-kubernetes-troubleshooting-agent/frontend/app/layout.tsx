import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "AI Kubernetes Agent", description: "On-demand Kubernetes troubleshooting" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
