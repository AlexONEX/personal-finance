import { enrichEntries, ars, pct, periodo, monthsDiff } from './compute.js';

export function renderAnalysis(raw) {
  const tbody = document.getElementById('analysis-body');
  if (!raw.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Sin datos.</td></tr>';
    return;
  }

  const entries = enrichEntries(raw); // ascending
  let lastRaiseDate = entries[0].fecha;

  const rows = entries.map((e, i) => {
    const prev = i > 0 ? entries[i - 1] : null;
    const varBruto = prev ? ((e.bruto - prev.bruto) / prev.bruto * 100) : null;
    const varNeto  = prev ? ((e.neto  - prev.neto)  / prev.neto  * 100) : null;
    const meses    = monthsDiff(lastRaiseDate, e.fecha);
    if (e.ascenso) lastRaiseDate = e.fecha;

    return { e, varBruto, varNeto, meses };
  }).reverse(); // newest first

  tbody.innerHTML = rows.map(({ e, varBruto, varNeto, meses }) => `
    <tr class="${e.ascenso ? 'row-ascenso' : ''}">
      <td>${periodo(e.fecha)}</td>
      <td class="num">${ars(e.bruto)}</td>
      <td class="num">${ars(e.neto)}</td>
      <td class="num">${ars(e.total_neto)}</td>
      <td class="num ${varBruto > 0 ? 'green' : varBruto < 0 ? 'red' : ''}">${pct(varBruto)}</td>
      <td class="num ${varNeto  > 0 ? 'green' : varNeto  < 0 ? 'red' : ''}">${pct(varNeto)}</td>
      <td class="num">${meses === 0 ? '↑ este mes' : meses + ' mes' + (meses !== 1 ? 'es' : '')}</td>
    </tr>
  `).join('');
}
