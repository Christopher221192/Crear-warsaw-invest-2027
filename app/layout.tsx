import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Poland House Hunter | Elite Real Estate Intelligence",
  description: "Advanced investment analysis for the Polish real estate market Q1/Q2 2027.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
