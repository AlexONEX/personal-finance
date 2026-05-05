import { enrichEntries, ars, pct, periodo } from './compute.js';

let chartEvolution = null;
let chartBreakdown = null;

export function renderDashboard(raw) {
  if (!raw.length) {
    document.getElementById('summary-cards').innerHTML =
      '<p class="empty" style="padding:1rem">Sin datos.</p>';
    return;
  }

  const entries = enrichEntries(raw); // ascending
  const last    = entries.at(-1);
  const prev    = entries.length > 1 ? entries.at(-2) : null;

  // Last raise
  let lastRaiseEntry = null;
  for (let i = entries.length - 1; i >= 0; i--) {
    if (entries[i].ascenso) { lastRaiseEntry = entries[i]; break; }
  }

  renderCards(last, prev, lastRaiseEntry);
  renderEvolutionChart(entries);
  renderBreakdownChart(last);
}

function renderCards(last, prev, lastRaise) {
  const varBruto = prev ? ((last.bruto - prev.bruto) / prev.bruto * 100) : null;

  const cards = [
    { label: 'Último Bruto',    value: ars(last.bruto),      sub: last.fecha },
    { label: 'Último Neto',     value: ars(last.neto),       sub: 'después de descuentos' },
    { label: 'Total Neto',      value: ars(last.total_neto), sub: 'con beneficios' },
    { label: 'Var. Bruto MoM',  value: varBruto ? pct(varBruto) : '—',
      sub: prev ? `vs ${periodo(prev.fecha)}` : 'primer registro',
      color: varBruto > 0 ? 'var(--green)' : varBruto < 0 ? 'var(--red)' : '' },
    { label: 'Último Aumento',  value: lastRaise ? periodo(lastRaise.fecha) : '—',
      sub: lastRaise ? pct(lastRaise.aumento) : '' },
    { label: 'Registros',       value: String(raw?.length ?? 0), sub: 'meses cargados' },
  ];

  document.getElementById('summary-cards').innerHTML = cards.map(c => `
    <div class="card">
      <div class="card-label">${c.label}</div>
      <div class="card-value" style="${c.color ? `color:${c.color}` : ''}">${c.value}</div>
      <div class="card-sub">${c.sub ?? ''}</div>
    </div>
  `).join('');
}

function renderEvolutionChart(entries) {
  const labels = entries.map(e => e.fecha.slice(0, 7)); // YYYY-MM
  const brutos = entries.map(e => e.bruto);
  const netos  = entries.map(e => e.neto);

  const ctx = document.getElementById('chart-evolution');
  if (chartEvolution) chartEvolution.destroy();

  chartEvolution = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Bruto', data: brutos, borderColor: '#2563eb', backgroundColor: '#dbeafe', fill: false, tension: 0.2 },
        { label: 'Neto',  data: netos,  borderColor: '#16a34a', backgroundColor: '#dcfce7', fill: false, tension: 0.2 },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { ticks: { callback: v => '$' + v.toLocaleString('es-AR') } },
      },
    },
  });
}

function renderBreakdownChart(last) {
  const ctx = document.getElementById('chart-breakdown');
  if (chartBreakdown) chartBreakdown.destroy();

  const data = [
    last.neto,
    last.jubilacion,
    last.pami,
    last.obra_social,
    (last.sac_neto ?? 0) + (last.bono_neto ?? 0) + (last.tarjeta_corporativa ?? 0) + (last.otros_beneficios ?? 0),
  ].map(n => n || 0);

  chartBreakdown = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Neto', 'Jubilación', 'PAMI', 'Obra Social', 'Extras'],
      datasets: [{
        data,
        backgroundColor: ['#2563eb', '#f59e0b', '#10b981', '#6366f1', '#ec4899'],
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
    },
  });
}
