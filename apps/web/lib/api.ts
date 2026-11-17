const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  supabase_connected: boolean;
  timestamp: string;
}

export interface Department {
  code: string;
  name: string;
  description: string;
  icon: string;
}

export interface Course {
  department_code: string;
  code: string;
  title: string;
  level: string;
  description: string;
  order_index?: number;
}

export interface ProblemModule {
  course_code: string;
  slug: string;
  title: string;
  description: string;
  discipline: string;
  category: string;
  status: 'active' | 'beta' | 'planned';
  version: string;
  icon: string;
}

export async function fetchHealth(): Promise<HealthStatus | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchDepartments(): Promise<Department[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/departments`, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch departments');
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchCourses(department = 'civil'): Promise<Course[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/courses?department=${department}`, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch courses');
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchProblemModules(courseCode?: string): Promise<ProblemModule[]> {
  try {
    const url = courseCode
      ? `${API_BASE}/api/v1/problem-modules?course_code=${courseCode}`
      : `${API_BASE}/api/v1/problem-modules`;
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch problem modules');
    return await res.json();
  } catch {
    return [];
  }
}
