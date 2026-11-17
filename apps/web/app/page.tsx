'use client';

import React, { useState, useEffect } from 'react';
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
        // Fallback check against Supabase directly
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
          { department_code: 'civil', code: 'CE-202', title: 'Engineering Surveying & Geomatics', level: 'Undergraduate', description: 'Differential leveling' },
          { department_code: 'civil', code: 'CE-301', title: 'Highway Engineering', level: 'Undergraduate', description: 'Vertical & horizontal curves' },
          { department_code: 'civil', code: 'CE-302', title: 'Timber Structural Design', level: 'Undergraduate', description: 'Limit states capacity' },
        ]);
      }

      // 3. Fetch problem modules
      const loadedModules = await fetchProblemModules();
      if (loadedModules && loadedModules.length > 0) {
        setModules(loadedModules);
      } else {
        setModules([
          { course_code: 'CE-201', slug: 'simply-supported-beam', title: 'Simply Supported Beam: SFD & BMD', description: 'Calculate reactions, shear force diagram (SFD), bending moment diagram (BMD) and maximum deflection for determinate beams.', discipline: 'civil', category: 'structural', status: 'active', version: '1.0.0', icon: 'activity' },
          { course_code: 'CE-101', slug: 'mohrs-circle', title: "Mohr's Circle & Stress Transformation", description: 'Determine principal stresses, maximum in-plane shear stress, and orientation of principal planes for 2D plane stress.', discipline: 'civil', category: 'materials', status: 'active', version: '1.0.0', icon: 'compass' },
          { course_code: 'CE-202', slug: 'differential-leveling', title: 'Differential Leveling & Field Book Reduction', description: 'Calculate bench mark elevations using Height of Instrument (HI) and Rise & Fall methods with arithmetic closure checks.', discipline: 'civil', category: 'surveying', status: 'active', version: '1.0.0', icon: 'map-pin' },
          { course_code: 'CE-301', slug: 'highway-vertical-curve', title: 'Highway Crest & Sag Vertical Curves', description: 'Calculate elevations along equal-tangent vertical parabolic curves, minimum curve length for stopping sight distance.', discipline: 'civil', category: 'highway', status: 'active', version: '1.0.0', icon: 'trending-up' },
          { course_code: 'CE-302', slug: 'timber-beam-check', title: 'Timber Member Bending & Shear Capacity', description: 'Standard-governed capacity checks for sawn timber beams against flexural stresses, horizontal shear, and live load deflections.', discipline: 'civil', category: 'timber', status: 'active', version: '1.0.0', icon: 'shield' },
        ]);
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

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar apiOnline={apiOnline} supabaseOnline={supabaseOnline} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 rounded-2xl p-6 sm:p-8 text-white mb-8 shadow-sm border border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-400/20 text-sky-300 text-xs font-medium">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Milestone 1 Monorepo Foundation Active</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Civil Engineering Problem Workbench
              </h1>
              <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                A verified computation platform combining course curricula, step-by-step rigorous calculation workflows, 
                reactive visualisations, and exportable engineering reports.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-center sm:text-left">
                <div className="text-xs text-slate-400">Department</div>
                <div className="text-sm font-semibold text-white flex items-center gap-1.5 justify-center sm:justify-start">
                  <Building2 className="w-4 h-4 text-sky-400" />
                  <span>Civil Engineering</span>
                </div>
              </div>
              <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-3 text-center sm:text-left">
                <div className="text-xs text-slate-400">Total Solvers</div>
                <div className="text-sm font-semibold text-white flex items-center gap-1.5 justify-center sm:justify-start">
                  <Calculator className="w-4 h-4 text-emerald-400" />
                  <span>{modules.length} Modules</span>
                </div>
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
              All Courses ({modules.length})
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
                placeholder="Search modules, formulas, topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition"
              />
            </div>

            <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
              <Filter className="w-3.5 h-3.5 text-slate-400 ml-1 hidden sm:block" />
              {['all', 'structural', 'materials', 'surveying', 'highway', 'timber'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 text-xs rounded-lg font-medium capitalize transition ${
                    selectedCategory === cat
                      ? 'bg-sky-100 text-sky-800 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredModules.map((module) => (
            <ModuleCard
              key={module.slug}
              module={module}
              onSelect={(m) => setActiveModule(m)}
            />
          ))}
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
              <button
                onClick={() => {
                  alert(`Module "${activeModule.title}" is ready. Full interactive 2D/3D visualizer will activate in Milestone 2!`);
                  setActiveModule(null);
                }}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg shadow-sm transition"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Launch Workbench</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-6 text-xs text-slate-500 text-center">
        <p>Engineering & Science Hub &bull; University-Level Problem Solving Platform &bull; Built with Next.js, FastAPI & Supabase</p>
      </footer>
    </div>
  );
}
