import { enrichEntries, ars, pct, periodo } from './compute.js';
import { api } from './api.js';
import { showToast, reload } from './app.js';

export function renderSalary(raw) {
  const tbody = document.getElementById('salary-body');
  if (!raw.length) {
    tbody.innerHTML = '<tr><td colspan="19" class="empty">Sin datos. Agregá tu primer sueldo.</td></tr>';
    return;
  }

  const entries = enrichEntries(raw).reverse(); // newest first

  tbody.innerHTML = entries.map(e => `
    <tr data-id="${e.id}" class="${e.ascenso ? 'row-ascenso' : ''}">
      <td>${periodo(e.fecha)}</td>
      <td class="input-col">${e.fecha}</td>
      <td class="num input-col">${ars(e.bruto)}</td>
      <td class="num calc">${ars(e.jubilacion)}</td>
      <td class="num calc">${ars(e.pami)}</td>
      <td class="num calc">${ars(e.obra_social)}</td>
      <td class="num bold">${ars(e.neto)}</td>
      <td class="num input-col">${e.sac_bruto ? ars(e.sac_bruto) : '—'}</td>
      <td class="num calc">${e.sac_neto  ? ars(e.sac_neto)  : '—'}</td>
      <td class="num input-col">${e.bono_neto           ? ars(e.bono_neto)           : '—'}</td>
      <td class="num input-col">${e.tarjeta_corporativa ? ars(e.tarjeta_corporativa) : '—'}</td>
      <td class="num input-col">${e.otros_beneficios    ? ars(e.otros_beneficios)    : '—'}</td>
      <td class="num bold">${ars(e.total_neto)}</td>
      <td class="num input-col">${e.horas_diarias ?? '—'}</td>
      <td class="num calc">${e.bruto_hora ? ars(e.bruto_hora) : '—'}</td>
      <td class="num calc">${e.neto_hora  ? ars(e.neto_hora)  : '—'}</td>
      <td class="center">${e.ascenso ? '↑' : ''}</td>
      <td class="num ${e.aumento ? 'green' : ''}">${e.aumento ? pct(e.aumento) : '—'}</td>
      <td>
        <button class="btn-edit" data-id="${e.id}" title="Editar">✎</button>
        <button class="btn-del"  data-id="${e.id}" title="Eliminar">×</button>
      </td>
    </tr>
  `).join('');

  // Delete
  tbody.querySelectorAll('.btn-del').forEach(btn => {
    btn.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      if (!confirm('¿Eliminar esta entrada?')) return;
      try {
        await api.salary.remove(btn.dataset.id);
        showToast('Entrada eliminada');
        reload();
      } catch (err) {
        showToast(`Error: ${err.message}`);
      }
    });
  });

  // Edit: fill form with existing data
  tbody.querySelectorAll('.btn-edit').forEach(btn => {
    btn.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const entry = raw.find(e => String(e.id) === btn.dataset.id);
      if (!entry) return;
      fillForm(entry);
    });
  });
}

function fillForm(entry) {
  const form = document.getElementById('salary-form');
  form.querySelector('[name=entry_id]').value = entry.id;
  form.querySelector('[name=fecha]').value = entry.fecha;
  form.querySelector('[name=bruto]').value = entry.bruto;
  form.querySelector('[name=sac_bruto]').value = entry.sac_bruto ?? '';
  form.querySelector('[name=bono_neto]').value = entry.bono_neto ?? '';
  form.querySelector('[name=tarjeta_corporativa]').value = entry.tarjeta_corporativa ?? '';
  form.querySelector('[name=otros_beneficios]').value = entry.otros_beneficios ?? '';
  form.querySelector('[name=horas_diarias]').value = entry.horas_diarias ?? '';
  document.getElementById('form-title').textContent = 'Editar entrada';
  form.classList.remove('hidden');
  form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

export function initSalaryForm() {
  const form    = document.getElementById('salary-form');
  const btnAdd  = document.getElementById('btn-add');
  const btnCancel = document.getElementById('btn-cancel');

  btnAdd.addEventListener('click', () => {
    form.reset();
    form.querySelector('[name=entry_id]').value = '';
    document.getElementById('form-title').textContent = 'Nueva entrada';
    form.classList.toggle('hidden');
  });

  btnCancel.addEventListener('click', () => {
    form.classList.add('hidden');
    form.reset();
  });

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(form);
    const entryId = fd.get('entry_id');

    const payload = {};
    for (const [k, v] of fd.entries()) {
      if (k === 'entry_id') continue;
      if (v === '') { payload[k] = null; continue; }
      payload[k] = k === 'fecha' ? v : Number(v);
    }

    try {
      if (entryId) {
        await api.salary.update(entryId, payload);
        showToast('Entrada actualizada');
      } else {
        await api.salary.create(payload);
        showToast('Entrada guardada');
      }
      form.classList.add('hidden');
      form.reset();
      reload();
    } catch (err) {
      showToast(`Error: ${err.message}`);
    }
  });
}
