async function api(method, url, body) {
  const r = await fetch(url, {
    method,
    headers: body ? {'Content-Type': 'application/json'} : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (r.status === 401) {
    location.href = '/login';
    return Promise.reject('unauthorized');
  }
  if (!r.ok) {
    const e = await r.json().catch(() => ({detail: 'error'}));
    throw new Error(e.detail || 'API error');
  }
  if (r.status === 204) return null;
  return r.json();
}

let currentProject = null;

async function loadMe() {
  const me = await api('GET', '/api/auth/me');
  document.getElementById('userEmail').textContent = me.email;
}

async function loadProjects() {
  const projects = await api('GET', '/api/projects');
  const grid = document.getElementById('projectsGrid');
  grid.innerHTML = '';
  if (!projects.length) {
    grid.innerHTML = `<div class="md:col-span-3 bg-white p-10 rounded-2xl border border-dashed border-slate-300 text-center text-slate-500">
      У вас пока нет проектов. Нажмите «Новый проект».</div>`;
    return;
  }
  for (const p of projects) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition cursor-pointer';
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="font-bold text-slate-800">${p.name}</div>
        <span class="text-xs px-2 py-1 rounded-full ${p.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}">
          ${p.is_active ? '🟢 активен' : '⏸ пауза'}
        </span>
      </div>
      <div class="text-sm text-slate-500 mt-1">${p.domain}</div>
      <div class="mt-3 flex gap-3 text-xs text-slate-500">
        <span class="bg-indigo-50 text-indigo-700 px-2 py-1 rounded">тариф: ${p.plan}</span>
        <span class="bg-slate-50 px-2 py-1 rounded">регион: ${p.region}</span>
        <span class="bg-slate-50 px-2 py-1 rounded">визитов/сутки: ${p.daily_visits_target}</span>
      </div>
    `;
    card.addEventListener('click', () => openProject(p));
    grid.appendChild(card);
  }
}

async function openProject(p) {
  currentProject = p;
  document.getElementById('projectDetails').classList.remove('hidden');
  document.getElementById('pdName').textContent = p.name;
  document.getElementById('pdMeta').textContent = `${p.domain} • тариф ${p.plan} • регион ${p.region} • визитов в сутки: ${p.daily_visits_target}`;
  await Promise.all([loadKeywords(), loadTasks()]);
  document.getElementById('projectDetails').scrollIntoView({behavior: 'smooth', block: 'start'});
}

async function loadKeywords() {
  if (!currentProject) return;
  const kws = await api('GET', `/api/projects/${currentProject.id}/keywords`);
  const tbody = document.getElementById('kwTable');
  tbody.innerHTML = '';
  if (!kws.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="py-4 text-slate-500 text-center">Запросов ещё нет</td></tr>';
    return;
  }
  for (const k of kws) {
    const tr = document.createElement('tr');
    tr.className = 'border-b border-slate-100';
    tr.innerHTML = `
      <td class="py-2">${k.query}</td>
      <td>${k.last_position ?? '—'}</td>
      <td>${k.last_checked_at ? new Date(k.last_checked_at).toLocaleString('ru-RU') : '—'}</td>
      <td><button class="text-red-500 hover:text-red-700 text-xs" data-del="${k.id}">удалить</button></td>
    `;
    tbody.appendChild(tr);
  }
  tbody.querySelectorAll('[data-del]').forEach(btn => {
    btn.addEventListener('click', async () => {
      await api('DELETE', `/api/projects/${currentProject.id}/keywords/${btn.dataset.del}`);
      loadKeywords();
    });
  });
}

async function loadTasks() {
  if (!currentProject) return;
  const tasks = await api('GET', `/api/projects/${currentProject.id}/tasks?limit=80`);
  const kws = await api('GET', `/api/projects/${currentProject.id}/keywords`);
  const kwMap = Object.fromEntries(kws.map(k => [k.id, k.query]));
  const tbody = document.getElementById('tasksTable');
  tbody.innerHTML = '';
  if (!tasks.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="py-4 text-slate-500 text-center">Задач ещё не было</td></tr>';
    return;
  }
  for (const t of tasks) {
    const ua = (t.user_agent || '').slice(0, 40);
    const statusColor = {pending: 'text-slate-500', running: 'text-amber-600', done: 'text-emerald-600', failed: 'text-red-600'}[t.status] || '';
    const tr = document.createElement('tr');
    tr.className = 'border-b border-slate-100';
    tr.innerHTML = `
      <td class="py-1">${t.id}</td>
      <td class="truncate" title="${kwMap[t.keyword_id] || ''}">${(kwMap[t.keyword_id] || '').slice(0, 40)}</td>
      <td class="font-semibold ${statusColor}">${t.status}</td>
      <td>${t.found_position ?? '—'}</td>
      <td>${t.pages_visited ?? '—'}</td>
      <td>${t.session_seconds ?? '—'}</td>
      <td class="text-slate-400" title="${t.user_agent || ''}">${ua}…</td>
      <td>${new Date(t.scheduled_at).toLocaleString('ru-RU')}</td>
    `;
    tbody.appendChild(tr);
  }
}

document.getElementById('logoutBtn').addEventListener('click', async () => {
  await api('POST', '/api/auth/logout');
  location.href = '/';
});

document.getElementById('newProjectBtn').addEventListener('click', () => {
  document.getElementById('newProjectModal').classList.remove('hidden');
  document.getElementById('newProjectModal').classList.add('flex');
});
document.getElementById('cancelNewProject').addEventListener('click', () => {
  document.getElementById('newProjectModal').classList.add('hidden');
});
document.getElementById('newProjectForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const data = Object.fromEntries(fd);
  data.region = parseInt(data.region);
  data.daily_visits_target = parseInt(data.daily_visits_target);
  data.avg_session_seconds = parseInt(data.avg_session_seconds);
  await api('POST', '/api/projects', data);
  document.getElementById('newProjectModal').classList.add('hidden');
  e.target.reset();
  await loadProjects();
});

document.getElementById('addKwBtn').addEventListener('click', async () => {
  if (!currentProject) return;
  const text = document.getElementById('kwInput').value;
  const queries = text.split('\n').map(s => s.trim()).filter(Boolean);
  if (!queries.length) return;
  await api('POST', `/api/projects/${currentProject.id}/keywords/bulk`, {queries});
  document.getElementById('kwInput').value = '';
  loadKeywords();
});

document.getElementById('runNowBtn').addEventListener('click', async () => {
  if (!currentProject) return;
  await api('POST', `/api/projects/${currentProject.id}/run-now?count=5`);
  await loadTasks();
  alert('5 задач поставлены в очередь. Обновите вкладку «Задачи роботов» через несколько секунд.');
});
document.getElementById('toggleProjectBtn').addEventListener('click', async () => {
  if (!currentProject) return;
  await api('POST', `/api/projects/${currentProject.id}/toggle`);
  await loadProjects();
});
document.getElementById('deleteProjectBtn').addEventListener('click', async () => {
  if (!currentProject) return;
  if (!confirm('Удалить проект и все его данные?')) return;
  await api('DELETE', `/api/projects/${currentProject.id}`);
  document.getElementById('projectDetails').classList.add('hidden');
  currentProject = null;
  loadProjects();
});
document.getElementById('reloadTasks').addEventListener('click', loadTasks);

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.remove('text-indigo-600', 'border-indigo-600');
      b.classList.add('text-slate-500', 'border-transparent');
    });
    btn.classList.add('text-indigo-600', 'border-indigo-600');
    btn.classList.remove('text-slate-500', 'border-transparent');
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'));
    document.getElementById('tab-' + btn.dataset.tab).classList.remove('hidden');
  });
});

setInterval(() => { if (currentProject) loadTasks(); }, 5000);

(async () => {
  try {
    await loadMe();
    await loadProjects();
  } catch (e) {
    location.href = '/login';
  }
})();
