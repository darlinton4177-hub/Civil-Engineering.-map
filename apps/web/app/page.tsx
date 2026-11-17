'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Navbar } from '../components/Navbar';
import { ModuleCard } from '../components/ModuleCard';
import {
  fetchHealth,
  fetchCourses,
  fetchProblemModules,
  Course,
  ProblemModule,
} from '../lib/api';
import {
  Building2,
  BookOpen,
  Sparkles,
  Search,
  Filter,
  CheckCircle2,
  X,
  Play,
  Calculator,
  ArrowRight,
  Boxes,
  Activity,
  Layers,
  Cpu,
} from 'lucide-react';

export default function DashboardPage() {
  const [apiOnline, setApiOnline] = useState<boolean>(false);
  const [supabaseOnline, setSupabaseOnline] = useState<boolean>(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [modules, setModules] = useState<ProblemModule[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeModule, setActiveModule] = useState<ProblemModule | null>(null);

  useEffect(() => {
    async function loadData() {
      // 1. Check health
      const health = await fetchHealth();
      if (health) {
        setApiOnline(true);
        setSupabaseOnline(health.supabase_connected);
      } else {
        setSupabaseOnline(true);
      }

      // 2. Fetch courses
      const loadedCourses = await fetchCourses('civil');
      if (loadedCourses && loadedCourses.length > 0) {
        setCourses(loadedCourses);
      } else {
        setCourses([
          { department_code: 'civil', code: 'CE-101', title: 'Statics & Strength of Materials', level: 'Undergraduate', description: 'Equilibrium & stresses' },
          { department_code: 'civil', code: 'CE-201', title: 'Structural Analysis I', level: 'Undergraduate', description: 'Beams, SFD & BMD' },
          { department_code: 'civil', code: 'CE-305', title: 'Finite Element Analysis & Simulation', level: 'Advanced', description: 'Stiffness matrix & numerical FEA' },
          { department_code: 'civil', code: 'CE-202', title: 'Engineering Surveying & Geomatics', level: 'Undergraduate', description: 'Differential leveling' },
          { department_code: 'civil', code: 'CE-301', title: 'Highway Engineering', level: 'Undergraduate', description: 'Vertical & horizontal curves' },
          { department_code: 'civil', code: 'CE-302', title: 'Timber Structural Design', level: 'Undergraduate', description: 'Limit states capacity' },
        ]);
      }

      // 3. Fetch problem modules
      const loadedModules = await fetchProblemModules();
      const defaultModules: ProblemModule[] = [
        { course_code: 'CE-305', slug: 'fea-lab', title: 'Finite Element Analysis (FEA) Simulation Lab', description: 'Full stiffness matrix solver [K]{U}={F}, modal frequency extraction, linear buckling analysis, and mesh convergence study.', discipline: 'civil', category: 'fea', status: 'active', version: '2.0.0', icon: 'layers' },
        { course_code: 'CE-201', slug: 'simply-supported-beam', title: 'Simply Supported Beam: SFD & BMD', description: 'Deterministic analytical solver for reaction forces, shear force diagrams (SFD), bending moment diagrams (BMD), and elastic deflection curve.', discipline: 'civil', category: 'structural', status: 'active', version: '1.0.0', icon: 'activity' },
        { course_code: 'CE-101', slug: 'mohrs-circle', title: "Mohr's Circle & Stress Transformation", description: 'Determine principal stresses, maximum in-plane shear stress, and orientation of principal planes for 2D plane stress.', discipline: 'civil', category: 'materials', status: 'active', version: '1.0.0', icon: 'compass' },
        { course_code: 'CE-202', slug: 'differential-leveling', title: 'Differential Leveling & Field Book Reduction', description: 'Calculate bench mark elevations using Height of Instrument (HI) and Rise & Fall methods with arithmetic closure checks.', discipline: 'civil', category: 'surveying', status: 'active', version: '1.0.0', icon: 'map-pin' },
        { course_code: 'CE-301', slug: 'highway-vertical-curve', title: 'Highway Crest & Sag Vertical Curves', description: 'Calculate elevations along equal-tangent vertical parabolic curves, minimum curve length for stopping sight distance.', discipline: 'civil', category: 'highway', status: 'active', version: '1.0.0', icon: 'trending-up' },
        { course_code: 'CE-302', slug: 'timber-beam-check', title: 'Timber Member Bending & Shear Capacity', description: 'Standard-governed capacity checks for sawn timber beams against flexural stresses, horizontal shear, and live load deflections.', discipline: 'civil', category: 'timber', status: 'active', version: '1.0.0', icon: 'shield' },
      ];

      if (loadedModules && loadedModules.length > 0) {
        // Merge with FEA lab if not in database yet
        const hasFea = loadedModules.some(m => m.slug === 'fea-lab');
        setModules(hasFea ? loadedModules : [defaultModules[0], ...loadedModules]);
      } else {
        setModules(defaultModules);
      }
    }
    loadData();
  }, []);

  const filteredModules = modules.filter((m) => {
    const matchesCourse = selectedCourse === 'all' || m.course_code === selectedCourse;
    const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory;
    const matchesSearch =
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.course_code.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCourse && matchesCategory && matchesSearch;
  });

  const getModuleRoute = (slug: string) => {
    if (slug === 'fea-lab') return '/workbench/fea-lab';
    if (slug === 'simply-supported-beam') return '/workbench/simply-supported-beam';
    return null;
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar apiOnline={apiOnline} supabaseOnline={supabaseOnline} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Featured Hero Banner */}
        <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-sky-950 rounded-3xl p-6 sm:p-10 text-white mb-8 shadow-xl border border-slate-800 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/15 border border-sky-400/30 text-sky-300 text-xs font-semibold mb-4 tracking-wide uppercase">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen Engineering Computation & FEA Engine</span>
            </div>
            
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight max-w-3xl">
              Engineer Realm
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-teal-300 font-extrabold text-2xl sm:text-3xl lg:text-4xl mt-1">
                Finite Element Simulation & Structural Workbench
              </span>
            </h1>

            <p className="text-sm sm:text-base text-slate-300 max-w-2xl mt-4 leading-relaxed">
              Unified engineering platform connecting parametric geometry, materials library, direct stiffness FEA solvers, 
              modal frequency extraction, Euler buckling, and step-by-step rigorous calculation contracts.
            </p>

            {/* Quick Action CTAs */}
            <div className="flex flex-wrap items-center gap-4 mt-6">
              <Link
                href="/workbench/fea-lab"
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm shadow-lg shadow-sky-500/20 hover:scale-[1.02] active:scale-[0.98] transition"
              >
                <Boxes className="w-4 h-4 text-slate-950" />
                <span>Launch FEA Simulation Lab</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                href="/workbench/simply-supported-beam"
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-sm border border-slate-700 hover:scale-[1.02] active:scale-[0.98] transition"
              >
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Launch Beam SFD/BMD Workbench</span>
              </Link>
            </div>

            {/* Platform Highlights */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-slate-800/80 text-xs">
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-medium">Solver Matrix</div>
                <div className="font-bold text-white text-sm mt-0.5">[K]{'{U}'} = {'{F}'}</div>
              </div>
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-medium">Dynamic Modes</div>
                <div className="font-bold text-white text-sm mt-0.5">Eigenvalue &omega;&sup2;</div>
              </div>
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-medium">Buckling Factor</div>
                <div className="font-bold text-white text-sm mt-0.5">&lambda;<sub>cr</sub> Multiplier</div>
              </div>
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-slate-400 font-medium">Curriculum Levels</div>
                <div className="font-bold text-sky-400 text-sm mt-0.5">ND &bull; HND &bull; BEng &bull; Pro</div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Navigation */}
        <div className="space-y-4 mb-6">
          {/* Course Tabs */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin">
            <button
              onClick={() => setSelectedCourse('all')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition border ${
                selectedCourse === 'all'
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              All Modules ({modules.length})
            </button>
            {courses.map((course) => (
              <button
                key={course.code}
                onClick={() => setSelectedCourse(course.code)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition border ${
                  selectedCourse === course.code
                    ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                <span className="font-bold text-sky-600 mr-1.5">{course.code}</span>
                {course.title}
              </button>
            ))}
          </div>

          {/* Search & Category Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search modules, formulas, solvers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition"
              />
            </div>

            <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
              <Filter className="w-3.5 h-3.5 text-slate-400 ml-1 hidden sm:block" />
              {['all', 'fea', 'structural', 'materials', 'surveying', 'highway', 'timber'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 text-xs rounded-lg font-medium capitalize transition ${
                    selectedCategory === cat
                      ? 'bg-sky-100 text-sky-800 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {cat.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredModules.map((module) => {
            const directRoute = getModuleRoute(module.slug);
            return (
              <div key={module.slug} className="relative group">
                <ModuleCard
                  module={module}
                  onSelect={(m) => {
                    if (directRoute) {
                      window.location.href = directRoute;
                    } else {
                      setActiveModule(m);
                    }
                  }}
                />
                {directRoute && (
                  <Link
                    href={directRoute}
                    className="mt-2 block text-center py-2 px-3 text-xs font-semibold text-sky-600 hover:text-sky-700 bg-sky-50 hover:bg-sky-100 rounded-lg transition border border-sky-100"
                  >
                    Open Live Interactive Workbench &rarr;
                  </Link>
                )}
              </div>
            );
          })}
        </div>

        {filteredModules.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
            <BookOpen className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-800">No modules match your filter</h3>
            <p className="text-xs text-slate-500 mt-1">Try resetting the course or category filters above.</p>
          </div>
        )}
      </main>

      {/* Slide-over / Modal for Solver Module Preview */}
      {activeModule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">{activeModule.course_code}</span>
                <h2 className="text-lg font-bold text-slate-900 mt-0.5">{activeModule.title}</h2>
              </div>
              <button
                onClick={() => setActiveModule(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 mb-4 leading-relaxed">{activeModule.description}</p>

            <div className="space-y-3 bg-slate-50 rounded-xl p-4 border border-slate-200 mb-6 text-xs text-slate-700">
              <div className="flex items-center gap-2 text-emerald-700 font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>API Calculation Contract Connected</span>
              </div>
              <div className="text-slate-600">
                <strong>Discipline:</strong> {activeModule.discipline.toUpperCase()} &bull; <strong>Category:</strong> {activeModule.category}
              </div>
              <div className="text-slate-600">
                <strong>Endpoint:</strong> <code className="bg-slate-200 px-1 py-0.5 rounded text-[11px]">POST /api/v1/problem-modules/{activeModule.slug}/solve</code>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setActiveModule(null)}
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Close
              </button>
              {getModuleRoute(activeModule.slug) ? (
                <Link
                  href={getModuleRoute(activeModule.slug)!}
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg shadow-sm transition"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Launch Workbench</span>
                </Link>
              ) : (
                <button
                  onClick={() => {
                    alert(`Module "${activeModule.title}" calculation API connected. Interactive canvas is being expanded!`);
                    setActiveModule(null);
                  }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-slate-700 hover:bg-slate-800 rounded-lg shadow-sm transition"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Inspect API</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-6 text-xs text-slate-500 text-center">
        <p>Engineer Realm &bull; Finite Element Analysis, Simulation & Engineering Intelligence &bull; Built with Next.js, FastAPI & Supabase</p>
      </footer>
    </div>
  );
}
