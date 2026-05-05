import { api } from './api.js';
import { renderSalary, initSalaryForm } from './salary.js';
import { renderAnalysis } from './analysis.js';
import { renderDashboard } from './dashboard.js';

let _entries = [];

// ── Tab switching ──
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.add('hidden'));
    btn.classList.add('active');
    const tab = document.getElementById(btn.dataset.tab);
    tab.classList.remove('hidden');
    if (btn.dataset.tab === 'dashboard') renderDashboard(_entries);
  });
});

// ── Toast ──
let _toastTimer = null;
export function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    el.classList.remove('show');
    el.classList.add('hidden');
  }, 2500);
}

// ── Data loading ──
export async function reload() {
  try {
    _entries = await api.salary.list();
    renderSalary(_entries);
    renderAnalysis(_entries);
    // Dashboard only re-renders when tab is active to avoid re-creating charts
    const dashActive = document.getElementById('dashboard').classList.contains('active');
    if (dashActive) renderDashboard(_entries);
  } catch (err) {
    showToast(`Error cargando datos: ${err.message}`);
  }
}

// ── Init ──
initSalaryForm();
reload();
