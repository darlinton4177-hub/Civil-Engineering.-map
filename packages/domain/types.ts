export interface Department {
  id?: string;
  code: string;
  name: string;
  description: string;
  icon: string;
  created_at?: string;
}

export interface Course {
  id?: string;
  department_code: string;
  code: string;
  title: string;
  level: string;
  description: string;
  order_index?: number;
  created_at?: string;
}

export interface ProblemModule {
  id?: string;
  course_code: string;
  slug: string;
  title: string;
  description: string;
  discipline: string;
  category: string;
  status: 'active' | 'beta' | 'planned';
  version: string;
  icon: string;
  created_at?: string;
}

export interface CalculationRun {
  id?: string;
  user_id?: string | null;
  module_slug: string;
  title: string;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  notes?: string;
  created_at?: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  supabase_connected: boolean;
  timestamp: string;
}
