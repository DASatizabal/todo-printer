const BASE = '';

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg);
  }
  return res.json();
}

export function listTasks(status = 'open', category = null, sortBy = 'sort_order') {
  const params = new URLSearchParams({ status, sort_by: sortBy });
  if (category) params.set('category', category);
  return request(`/api/tasks?${params}`);
}

export function createTask(data) {
  return request('/api/tasks', { method: 'POST', body: JSON.stringify(data) });
}

export function updateTask(id, data) {
  return request(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export function archiveTask(id) {
  return request(`/api/tasks/${id}/archive`, { method: 'POST' });
}

export function restoreTask(id) {
  return request(`/api/tasks/${id}/restore`, { method: 'POST' });
}

export function deleteTask(id) {
  return request(`/api/tasks/${id}`, { method: 'DELETE' });
}

export function reorderTasks(taskIds) {
  return request('/api/tasks/reorder', {
    method: 'POST',
    body: JSON.stringify({ task_ids: taskIds }),
  });
}

export function getStats() {
  return request('/api/stats');
}

export function printTasks(options) {
  return request('/api/print', { method: 'POST', body: JSON.stringify(options) });
}

export function previewPrint(options) {
  return request('/api/print/preview', { method: 'POST', body: JSON.stringify(options) });
}

export function printDailyTicket() {
  return request('/api/print/daily', { method: 'POST' });
}

export function previewDailyTicket() {
  return request('/api/print/daily/preview', { method: 'POST' });
}

export function bulkCreateTasks(tasks) {
  return request('/api/tasks/bulk', {
    method: 'POST',
    body: JSON.stringify({ tasks }),
  });
}

export function syncRemoteTasks() {
  return request('/api/sync', { method: 'POST' });
}

export function getSyncPending() {
  return request('/api/sync/pending');
}
