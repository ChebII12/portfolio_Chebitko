export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = (() => {
    try {
      return localStorage.getItem('access_token');
    } catch {
      return null;
    }
  })();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, { ...options, headers });
  if (res.status === 401 || res.status === 403) {
    window.dispatchEvent(new CustomEvent('module1-auth-error', {
      detail: { status: res.status, path },
    }));
  }
  return res;
}

