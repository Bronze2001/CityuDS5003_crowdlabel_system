import { User, ImageTask, Annotation, UserStats, UnpaidUser } from '../types';

const API_URL = 'http://localhost:8000/api';

// Helper function for API requests
async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include',  // send cookies
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP Error ${res.status}`);
  }
  
  // handle empty response
  const text = await res.text();
  if (!text.trim()) return null as T;
  return JSON.parse(text);
}

export const api = {
  // ===== Auth APIs =====
  login: (username: string, password: string) => 
    request<User>('/auth/login/', { method: 'POST', body: JSON.stringify({ username, password }) }),
  
  logout: () => request('/auth/logout/', { method: 'POST' }),
  
  checkAuth: () => request<User>('/auth/check/', { method: 'GET' }),

  // ===== Annotator APIs =====
  getAvailableTask: async () => {
    const res = await request<ImageTask | null>('/tasks/next/', { method: 'GET' });
    if (!res || (typeof res === 'object' && Object.keys(res).length === 0)) return null;
    return res;
  },
  
  submitAnnotation: (image_id: number, label: string) => 
    request('/annotate/', { method: 'POST', body: JSON.stringify({ image_id, label }) }),
  
  getStats: () => request<UserStats>('/stats/', { method: 'GET' }),
  
  getHistory: () => request<Annotation[]>('/history/', { method: 'GET' }),

  // ===== Admin APIs =====
  getReviewQueue: () => request<ImageTask[]>('/admin/reviews/', { method: 'GET' }),
  
  resolveConflict: (image_id: number, true_label: string) => 
    request('/admin/resolve/', { method: 'POST', body: JSON.stringify({ image_id, true_label }) }),
    
  getUnpaidUsers: () => request<UnpaidUser[]>('/admin/unpaid/', { method: 'GET' }),
  
  runPayroll: () => request<{total: number}>('/admin/payroll/', { method: 'POST' }),
  
  getAllActiveTasks: () => request<ImageTask[]>('/tasks/active/', { method: 'GET' }),
  
  addTask: (url: string, categories: string, bounty: number) => 
    request('/tasks/add/', { method: 'POST', body: JSON.stringify({ url, categories, bounty }) }),
};