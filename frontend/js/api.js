const BASE = '/api';

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail ?? `Error ${res.status}`);
  return data;
}

export const api = {
  salary: {
    list:   ()        => req('/salary/'),
    create: (d)       => req('/salary/',      { method: 'POST',  body: JSON.stringify(d) }),
    update: (id, d)   => req(`/salary/${id}`, { method: 'PATCH', body: JSON.stringify(d) }),
    remove: (id)      => req(`/salary/${id}`, { method: 'DELETE' }),
  },
};
