const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
export const tenantIds: Record<string,string> = {'Acme Labs':'00000000-0000-0000-0000-000000000001','Globex Cloud':'00000000-0000-0000-0000-000000000002'};
export async function request(path:string, init:RequestInit={}, token='', tenant='Acme Labs') {
  const headers = new Headers(init.headers); headers.set('Content-Type','application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`); if (tenantIds[tenant]) headers.set('X-Tenant-ID', tenantIds[tenant]);
  const response = await fetch(`${API}${path}`, {...init, headers}); const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail?.message ?? data.detail?.code ?? `HTTP ${response.status}`); return data;
}
export async function login(email:string, password:string) { return request('/api/auth/login', {method:'POST', body:JSON.stringify({email,password})}); }
