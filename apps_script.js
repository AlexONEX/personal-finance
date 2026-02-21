/**
 * Ingresos Tracker - Google Apps Script
 * 
 * Este código permite actualizar CER y CCL directamente desde Google Sheets.
 * Instrucciones:
 * 1. En tu hoja de cálculo, ve a 'Extensiones' -> 'Apps Script'.
 * 2. Borra todo y pega este código.
 * 3. Guarda con el nombre 'SyncDatos'.
 * 4. Recarga tu planilla. Aparecerá un menú '📈 Tracker'.
 */

const CONFIG = {
  HISTORIC_SHEET: "historic_data",
  FIRST_DATA_ROW: 4,
  START_DATE: "2022-01-01"
};

/**
 * Crea el menú al abrir la planilla.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('📈 Tracker')
    .addItem('Sincronizar CER y CCL', 'syncMarketData')
    .addSeparator()
    .addItem('Ayuda / Documentación', 'showHelp')
    .addToUi();
}

/**
 * Función principal de sincronización.
 */
function syncMarketData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.HISTORIC_SHEET);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert("❌ No se encontró la hoja 'historic_data'. Ejecuta el setup de Python primero.");
    return;
  }

  // 1. Determinar rango de fechas
  const lastDate = getLastDate(sheet);
  const since = lastDate ? formatDate(addDays(lastDate, 1)) : CONFIG.START_DATE;
  const until = formatDate(new Date());

  if (since > until) {
    SpreadsheetApp.getActive().toast("✅ Los datos ya están actualizados hasta hoy.");
    return;
  }

  try {
    ss.toast("⏳ Obteniendo datos de BCRA y Ambito...", "Sincronización", -1);
    
    // 2. Fetch de APIs
    const cerData = fetchCER(since, until);
    const cclData = fetchCCL(since, until);
    
    // 3. Mezclar y preparar filas
    const combined = mergeMarketData(since, until, cerData, cclData);
    
    if (combined.length > 0) {
      appendRows(sheet, combined);
      ss.toast("✓ Se agregaron " + combined.length + " nuevos registros.", "Éxito", 5);
    } else {
      ss.toast("No se encontraron datos nuevos para el periodo solicitado.", "Aviso");
    }
  } catch (e) {
    SpreadsheetApp.getUi().alert("❌ Error en la sincronización:
" + e.toString());
  }
}

/**
 * Obtiene el CER desde la API de BCRA.
 */
function fetchCER(since, until) {
  const url = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30?desde=" + since + "&hasta=" + until;
  const options = { "muteHttpExceptions": true, "validateHttpsCertificates": false };
  const resp = UrlFetchApp.fetch(url, options);
  const json = JSON.parse(resp.getContentText());
  const results = {};
  
  if (json.results) {
    json.results.forEach(variable => {
      variable.detalle.forEach(item => {
        results[item.fecha] = item.valor;
      });
    });
  }
  return results;
}

/**
 * Obtiene el CCL desde Ambito.
 */
function fetchCCL(since, until) {
  const url = "https://mercados.ambito.com//dolarrava/cl/grafico/" + since + "/" + until;
  const resp = UrlFetchApp.fetch(url);
  const data = JSON.parse(resp.getContentText());
  const results = {};
  
  // Ambito devuelve [["fecha", "precio"], ["dd/mm/yyyy", price], ...]
  if (data && data.length > 1) {
    for (let i = 1; i < data.length; i++) {
      const parts = data[i][0].split('/');
      const isoDate = parts[2] + "-" + parts[1] + "-" + parts[0];
      results[isoDate] = data[i][1];
    }
  }
  return results;
}

/**
 * Mezcla ambos datasets por fecha.
 */
function mergeMarketData(sinceStr, untilStr, cer, ccl) {
  const start = new Date(sinceStr + "T12:00:00");
  const end = new Date(untilStr + "T12:00:00");
  const rows = [];
  
  for (let d = start; d <= end; d.setDate(d.getDate() + 1)) {
    const iso = formatDate(d);
    if (cer[iso] || ccl[iso]) {
      rows.push([
        Utilities.formatDate(d, "GMT-3", "dd/MM/yyyy"),
        cer[iso] || "",
        ccl[iso] || ""
      ]);
    }
  }
  return rows;
}

// --- Helpers ---

function getLastDate(sheet) {
  const values = sheet.getRange("A4:A").getValues();
  for (let i = values.length - 1; i >= 0; i--) {
    if (values[i][0] instanceof Date) return values[i][0];
    if (values[i][0] !== "") {
      const parts = values[i][0].toString().split('/');
      if (parts.length === 3) return new Date(parts[2], parts[1]-1, parts[0]);
    }
  }
  return null;
}

function appendRows(sheet, rows) {
  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, 3).setValues(rows);
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function formatDate(date) {
  return Utilities.formatDate(date, "GMT-3", "yyyy-MM-dd");
}

function showHelp() {
  const html = "Para actualizar el <b>REM (Expectativas)</b>, debes usar el script de Python, ya que requiere procesar archivos Excel complejos.<br><br>El botón superior solo sincroniza datos diarios (CER y CCL).";
  const ui = HtmlService.createHtmlOutput(html).setWidth(400).setHeight(200);
  SpreadsheetApp.getUi().showModelessDialog(ui, "Ayuda Ingresos Tracker");
}
