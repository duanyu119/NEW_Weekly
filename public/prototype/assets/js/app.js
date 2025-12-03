const Store = (() => {
  const KEY = 'proto_tasks_v1';
  const load = () => {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
  };
  const save = (tasks) => localStorage.setItem(KEY, JSON.stringify(tasks));
  const uid = () => Math.random().toString(36).slice(2,9);
  const now = () => new Date().toISOString();
  const defaults = () => ([
    { id: uid(), title: '设计首页信息架构', category: 'Design', priority: 'high', done: false, reminder: null, createdAt: now() },
    { id: uid(), title: '实现任务创建/编辑', category: 'Dev', priority: 'medium', done: false, reminder: null, createdAt: now() },
    { id: uid(), title: '集成通知提醒', category: 'Ops', priority: 'low', done: false, reminder: null, createdAt: now() },
  ]);
  const init = () => { const data = load(); if (!data.length) save(defaults()); };
  const all = () => load();
  const add = (t) => { const tasks = load(); tasks.unshift({ id: uid(), createdAt: now(), done: false, ...t }); save(tasks); };
  const update = (id, patch) => { const tasks = load().map(t => t.id===id?{...t, ...patch}:t); save(tasks); };
  const remove = (id) => { const tasks = load().filter(t => t.id!==id); save(tasks); };
  const toggle = (id) => { const tasks = load().map(t => t.id===id?{...t, done:!t.done}:t); save(tasks); };
  return { init, all, add, update, remove, toggle };
})();

function fmtPriority(p){
  const map = { high: 'bg-red-100 text-red-700', medium: 'bg-amber-100 text-amber-700', low: 'bg-emerald-100 text-emerald-700' };
  return map[p]||'bg-slate-100 text-slate-700';
}

function renderList(){
  const list = document.querySelector('#task-list');
  if(!list) return;
  list.innerHTML='';
  Store.all().forEach(t=>{
    const el = document.createElement('div');
    el.className = 'card p-3 mb-2 touch';
    el.innerHTML = `
      <div class="flex items-start justify-between">
        <div>
          <a class="font-medium text-slate-900" href="detail.html?id=${t.id}">${t.title}</a>
          <div class="mt-1 text-sm text-slate-600">${t.category}</div>
        </div>
        <div class="flex items-center gap-2">
          <span class="chip ${fmtPriority(t.priority)}">${t.priority}</span>
          <button class="btn px-3 py-2 bg-slate-100" data-action="toggle" aria-label="完成">
            <i class="fa-solid ${t.done?'fa-check-circle text-emerald-600':'fa-circle text-slate-400'}"></i>
          </button>
          <button class="btn px-3 py-2 bg-slate-100" data-action="delete" aria-label="删除">
            <i class="fa-solid fa-trash text-slate-700"></i>
          </button>
        </div>
      </div>`;
    el.querySelector('[data-action="toggle"]').addEventListener('click', ()=>{ Store.toggle(t.id); renderList(); });
    el.querySelector('[data-action="delete"]').addEventListener('click', ()=>{ Store.remove(t.id); renderList(); });
    list.appendChild(el);
  });
}

function bindCreate(){
  const form = document.querySelector('#create-form');
  if(!form) return;
  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const title = form.querySelector('[name=title]').value.trim();
    const category = form.querySelector('[name=category]').value.trim();
    const priority = form.querySelector('[name=priority]').value;
    if(!title) return;
    Store.add({ title, category, priority });
    form.reset();
    renderList();
  });
}

function statusBar(){
  const timeEl=document.querySelector('#status-time');
  if(!timeEl) return;
  setInterval(()=>{
    const d=new Date();
    const s=d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    timeEl.textContent=s;
  }, 1000);
}

document.addEventListener('DOMContentLoaded', ()=>{
  Store.init();
  renderList();
  bindCreate();
  statusBar();
});
