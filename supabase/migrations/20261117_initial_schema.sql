-- =============================================================================
-- Migration: 20261117_initial_schema.sql
-- Description: Core schema for Engineering & Science Hub
-- =============================================================================

-- Enable pgcrypto for UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS public.departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'building-2',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. COURSES TABLE
CREATE TABLE IF NOT EXISTS public.courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_code VARCHAR(50) NOT NULL REFERENCES public.departments(code) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    level VARCHAR(50) DEFAULT 'Undergraduate',
    description TEXT,
    order_index INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 3. PROBLEM MODULES TABLE
CREATE TABLE IF NOT EXISTS public.problem_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(50) NOT NULL REFERENCES public.courses(code) ON DELETE CASCADE,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    discipline VARCHAR(50) NOT NULL DEFAULT 'civil',
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planned', -- 'active', 'beta', 'planned'
    version VARCHAR(20) NOT NULL DEFAULT '0.1.0',
    icon VARCHAR(50) DEFAULT 'calculator',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 4. CALCULATION RUNS TABLE (User calculation history)
CREATE TABLE IF NOT EXISTS public.calculation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    module_slug VARCHAR(100) NOT NULL REFERENCES public.problem_modules(slug) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'Untitled Calculation',
    inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    outputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.problem_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.calculation_runs ENABLE ROW LEVEL SECURITY;

-- Allow public read access to departments, courses, and problem modules
CREATE POLICY "Allow public read access to departments" ON public.departments
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to courses" ON public.courses
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to problem_modules" ON public.problem_modules
    FOR SELECT USING (true);

-- Allow authenticated users to manage their own calculation runs
CREATE POLICY "Users can read own calculation runs" ON public.calculation_runs
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert own calculation runs" ON public.calculation_runs
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can update own calculation runs" ON public.calculation_runs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own calculation runs" ON public.calculation_runs
    FOR DELETE USING (auth.uid() = user_id);

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Departments
INSERT INTO public.departments (code, name, description, icon) VALUES
('civil', 'Civil & Environmental Engineering', 'Structural analysis, strength of materials, geotechnical, surveying, and transportation systems.', 'building-2')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon;

-- Courses
INSERT INTO public.courses (department_code, code, title, level, description, order_index) VALUES
('civil', 'CE-101', 'Statics & Strength of Materials', 'Undergraduate Year 1/2', 'Equilibrium of rigid bodies, internal shear and bending, axial stress/strain, torsion, and Mohr''s circle.', 1),
('civil', 'CE-201', 'Structural Analysis I', 'Undergraduate Year 2', 'Analysis of statically determinate beams, frames, and trusses. Shear force diagrams (SFD) and bending moment diagrams (BMD).', 2),
('civil', 'CE-202', 'Engineering Surveying & Geomatics', 'Undergraduate Year 2', 'Field measurement principles, differential leveling, height of instrument method, and error distribution.', 3),
('civil', 'CE-301', 'Highway Engineering & Geometric Design', 'Undergraduate Year 3', 'Horizontal and vertical curves, stopping sight distance, chainage profiles, and earthwork calculations.', 4),
('civil', 'CE-302', 'Timber & Masonry Structural Design', 'Undergraduate Year 3', 'Limit states design of structural timber members, bending, shear, bearing, and serviceability checks.', 5)
ON CONFLICT (code) DO UPDATE SET
    title = EXCLUDED.title,
    level = EXCLUDED.level,
    description = EXCLUDED.description,
    order_index = EXCLUDED.order_index;

-- Problem Modules
INSERT INTO public.problem_modules (course_code, slug, title, description, discipline, category, status, version, icon) VALUES
('CE-201', 'simply-supported-beam', 'Simply Supported Beam: SFD & BMD', 'Calculate support reactions, shear force distribution, bending moment distribution, and maximum deflection for determinate single-span beams.', 'civil', 'structural', 'active', '1.0.0', 'activity'),
('CE-101', 'mohrs-circle', 'Mohr''s Circle & Stress Transformation', 'Determine principal stresses, maximum in-plane shear stress, and orientation of principal planes for 2D plane stress states.', 'civil', 'materials', 'active', '1.0.0', 'compass'),
('CE-202', 'differential-leveling', 'Differential Leveling & Field Book Reduction', 'Calculate bench mark elevations using Height of Instrument (HI) and Rise & Fall methods with arithmetic closure checks.', 'civil', 'surveying', 'active', '1.0.0', 'map-pin'),
('CE-301', 'highway-vertical-curve', 'Highway Crest & Sag Vertical Curves', 'Calculate elevations along equal-tangent vertical parabolic curves, minimum curve length for stopping sight distance, and turning points.', 'civil', 'highway', 'active', '1.0.0', 'trending-up'),
('CE-302', 'timber-beam-check', 'Timber Member Bending & Shear Capacity', 'Standard-governed capacity checks for sawn timber beams against flexural stresses, horizontal shear, and live load deflections.', 'civil', 'timber', 'active', '1.0.0', 'shield')
ON CONFLICT (slug) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    version = EXCLUDED.version,
    icon = EXCLUDED.icon;
