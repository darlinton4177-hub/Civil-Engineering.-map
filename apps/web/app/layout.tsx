import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Engineering & Science Hub | Civil Engineering Problem Solver',
  description: 'Advanced university-level engineering problem-solving and scientific computation platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 antialiased">
        {children}
      </body>
    </html>
  );
}
