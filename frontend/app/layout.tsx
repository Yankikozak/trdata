import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "TR-Analytix | BIST Intelligence", description: "BIST market intelligence workspace" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="tr"><body>{children}</body></html>;
}
