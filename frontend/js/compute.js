const TAX = { jubilacion: 0.11, pami: 0.03, obraSocial: 0.03 };

function deduct(bruto) {
  const jub = Math.round(bruto * TAX.jubilacion);
  const pami = Math.round(bruto * TAX.pami);
  const os   = Math.round(bruto * TAX.obraSocial);
  return { jub, pami, os, neto: bruto - jub - pami - os };
}

export function enrichEntries(raw) {
  const sorted = [...raw].sort((a, b) => a.fecha.localeCompare(b.fecha));

  const entries = sorted.map(e => {
    const bruto = e.bruto ?? 0;
    const { jub, pami, os, neto } = deduct(bruto);

    const sacBruto = e.sac_bruto ?? 0;
    const sacNeto  = sacBruto > 0
      ? sacBruto - Math.round(sacBruto * TAX.jubilacion) - Math.round(sacBruto * TAX.pami) - Math.round(sacBruto * TAX.obraSocial)
      : null;

    const bonoNeto  = e.bono_neto ?? 0;
    const tarjeta   = e.tarjeta_corporativa ?? 0;
    const otros     = e.otros_beneficios ?? 0;
    const totalNeto = neto + (sacNeto ?? 0) + bonoNeto + tarjeta + otros;

    const horas     = e.horas_diarias ?? null;
    const brutoHora = horas ? Math.round(bruto / (horas * 20)) : null;
    const netoHora  = horas ? Math.round(neto  / (horas * 20)) : null;

    return {
      ...e,
      jubilacion: jub,
      pami,
      obra_social: os,
      neto,
      sac_neto: sacNeto,
      total_neto: totalNeto,
      bruto_hora: brutoHora,
      neto_hora: netoHora,
      ascenso: e.ascenso ?? false, // stored in DB, not computed
    };
  });

  return entries; // ascending order
}

// ── Formatters ──

export function ars(n) {
  if (n == null) return '—';
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(n);
}

export function fechaCorta(dateStr) {
  if (!dateStr) return '—';
  const [y, m, d] = dateStr.split('-');
  return `${d}-${m}-${y.slice(2)}`;
}

export function pct(n) {
  if (n == null) return '—';
  return (n > 0 ? '+' : '') + n.toFixed(1) + '%';
}

export function periodo(dateStr) {
  if (!dateStr) return '—';
  const [y, m, d] = dateStr.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
}

export function monthsDiff(d1, d2) {
  const [y1, m1] = d1.split('-').map(Number);
  const [y2, m2] = d2.split('-').map(Number);
  return (y2 - y1) * 12 + (m2 - m1);
}
