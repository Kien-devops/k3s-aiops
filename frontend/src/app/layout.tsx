import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'K3s AIOps Platform - Homelab SRE Copilot',
  description: 'Intelligent Observability & Incident Copilot powered by GPT-5.6 Sol',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}

