import React from 'react';
import { Layers, Database, Cpu, ExternalLink } from 'lucide-react';

interface NavbarProps {
  apiOnline: boolean;
  supabaseOnline: boolean;
}

export function Navbar({ apiOnline, supabaseOnline }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-sky-500 flex items-center justify-center text-white shadow-md">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight">Engineering & Science Hub</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
                v0.1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Civil & Structural Engineering Platform</p>
          </div>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700">
            <Database className={`w-3.5 h-3.5 ${supabaseOnline ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-slate-300">Supabase:</span>
            <span className={supabaseOnline ? 'text-emerald-400 font-medium' : 'text-amber-400 font-medium'}>
              {supabaseOnline ? 'Connected' : 'Connecting'}
            </span>
          </div>

          <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700">
            <Cpu className={`w-3.5 h-3.5 ${apiOnline ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-slate-300">FastAPI:</span>
            <span className={apiOnline ? 'text-emerald-400 font-medium' : 'text-amber-400 font-medium'}>
              {apiOnline ? 'Online (8000)' : 'Standby'}
            </span>
          </div>

          <a
            href="https://github.com/darlinton4177-hub/Civil-Engineering.-map"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:flex items-center space-x-1 text-xs text-slate-300 hover:text-white transition"
          >
            <span>GitHub</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </header>
  );
}
