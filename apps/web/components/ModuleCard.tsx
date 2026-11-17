import React from 'react';
import { Activity, Compass, MapPin, TrendingUp, Shield, ArrowRight, BookOpen } from 'lucide-react';
import { ProblemModule } from '../lib/api';

interface ModuleCardProps {
  module: ProblemModule;
  onSelect?: (module: ProblemModule) => void;
}

export function ModuleCard({ module, onSelect }: ModuleCardProps) {
  const getIcon = () => {
    switch (module.slug) {
      case 'simply-supported-beam':
        return <Activity className="w-5 h-5 text-sky-600" />;
      case 'mohrs-circle':
        return <Compass className="w-5 h-5 text-indigo-600" />;
      case 'differential-leveling':
        return <MapPin className="w-5 h-5 text-emerald-600" />;
      case 'highway-vertical-curve':
        return <TrendingUp className="w-5 h-5 text-amber-600" />;
      case 'timber-beam-check':
        return <Shield className="w-5 h-5 text-teal-600" />;
      default:
        return <BookOpen className="w-5 h-5 text-slate-600" />;
    }
  };

  const getCategoryBadgeClass = (category: string) => {
    switch (category) {
      case 'structural':
        return 'bg-sky-50 text-sky-700 border-sky-200';
      case 'materials':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'surveying':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'highway':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'timber':
        return 'bg-teal-50 text-teal-700 border-teal-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center">
            {getIcon()}
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${getCategoryBadgeClass(module.category)} uppercase tracking-wider`}>
              {module.category}
            </span>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              v{module.version}
            </span>
          </div>
        </div>

        <div className="text-xs font-semibold text-slate-500 mb-1">{module.course_code}</div>
        <h3 className="font-semibold text-slate-900 text-base mb-2 tracking-tight">{module.title}</h3>
        <p className="text-xs text-slate-600 leading-relaxed mb-4">{module.description}</p>
      </div>

      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
        <span className="text-[11px] text-slate-500 font-medium capitalize">
          Status: <strong className="text-slate-800">{module.status}</strong>
        </span>
        <button
          onClick={() => onSelect && onSelect(module)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-sky-600 transition"
        >
          <span>Open Solver</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
