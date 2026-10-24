// gpx_anonymizer_v1_4_0_tests.js - Micro Unit Test System for GPX Anonymizer (v1.4.0)
// Loaded only when the page URL contains ?test=  (runs automatically with ?test=run).
window.__runTests = async function () {
  console.log('%c🚀 Starting GPX Anonymizer unit tests...', 'color:#2f6fde;font-weight:bold;font-size:14px;');
  let passed = 0, failed = 0;
  const failures = [];
  const api = window.__TEST_API__;
  if (!api) {
    console.error('%c❌ FATAL: __TEST_API__ is not exposed. The URL must contain ?test=', 'color:#f44336;font-weight:bold;');
    return;
  }
  const root = api.root;
  const q = (r) => root.querySelector('[data-r="' + r + '"]');
  // ==================== HELPERS ====================
  function record(ok, name, detail) {
    if (ok) {
      console.log('%c✅ PASS: ' + name, 'color:#4CAF50;font-weight:bold;');
      passed++;
    } else {
      console.error('❌ FAIL: ' + name + (detail ? '\n   ' + detail : ''));
      failures.push(name);
      failed++;
    }
    return ok;
  }
  function assert(name, actual, expected, message = '') {
    const ok = typeof expected === 'object' && expected !== null
      ? JSON.stringify(actual) === JSON.stringify(expected)
      : actual === expected;
    return record(ok, name, 'Expected: ' + JSON.stringify(expected) + '\n   Actual:   ' + JSON.stringify(actual) + (message ? '\n   ' + message : ''));
  }
  function assertTrue(name, condition, message = '') {
    return record(!!condition, name, 'Condition not met.' + (message ? ' ' + message : ''));
  }
  function assertStartsWith(name, str, prefix) {
    return record(typeof str === 'string' && str.indexOf(prefix) === 0, name, 'Expected to start with ' + JSON.stringify(prefix) + ', got ' + JSON.stringify(String(str).slice(0, 80)));
  }
  function assertNear(name, actual, expected, tol) {
    return record(typeof actual === 'number' && Math.abs(actual - expected) <= tol, name, 'Expected ' + expected + ' ± ' + tol + ', got ' + actual);
  }
  function assertThrows(name, fn, pattern) {
    try { fn(); } catch (e) { return record(!pattern || pattern.test(e.message), name, 'Wrong error: ' + e.message); }
    return record(false, name, 'No error was thrown.');
  }
  const sleep = (ms) => new Promise((res) => setTimeout(res, ms));
  // Resolves when condition() is true, rejects after timeout.
  function waitFor(condition, timeout = 6000, label = 'condition') {
    return new Promise((resolve, reject) => {
      const t0 = Date.now();
      (function poll() {
        let ok = false;
        try { ok = condition(); } catch (e) { ok = false; }
        if (ok) return resolve(true);
        if (Date.now() - t0 > timeout) return reject(new Error('Timed out waiting for ' + label));
        setTimeout(poll, 50);
      })();
    });
  }
  function gpx(body, extraNs = '') {
    return '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1"' + extraNs + '>\n' + body + '\n</gpx>';
  }
  const HR_NS = ' xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"';
  // Track with known speeds: 5 × 0.0009° per 10 s, 20 s stop, 5 × 0.0018° per 10 s.
  function speedTrack() {
    const pts = [];
    let lat = 10, t = 0;
    const add = () => {
      const tm = new Date(Date.UTC(2024, 0, 1, 0, 0, t)).toISOString().replace('.000', '');
      pts.push('<trkpt lat="' + lat.toFixed(7) + '" lon="20"><ele>5</ele><time>' + tm + '</time></trkpt>');
    };
    add();
    for (let i = 0; i < 5; i++) { lat += 0.0009; t += 10; add(); }
    for (let i = 0; i < 2; i++) { t += 10; add(); }
    for (let i = 0; i < 5; i++) { lat += 0.0018; t += 10; add(); }
    return gpx('<trk><trkseg>' + pts.join('\n') + '</trkseg></trk>');
  }
  const MIXED = gpx(
    '<metadata><name>Secret</name><author><name>Me</name></author></metadata>\n' +
    '<wpt lat="55.75" lon="37.62"><ele>140</ele><name>Home</name><desc>my house</desc></wpt>\n' +
    '<rte><name>Plan</name><rtept lat="55.70" lon="37.60"/><rtept lat="55.71" lon="37.61"/></rte>\n' +
    '<trk><name>Run</name><trkseg>\n' +
    '<trkpt lat="55.7512345678" lon="37.6200001"><ele>150.5</ele><time>2023-05-01T10:00:05.250+03:00</time>' +
    '<extensions>\n  <gpxtpx:TrackPointExtension>\n    <gpxtpx:hr>120</gpxtpx:hr>\n  </gpxtpx:TrackPointExtension>\n</extensions></trkpt>\n' +
    '<trkpt lat="55.7400" lon="37.7"><ele>149</ele><time>2023-05-01T07:00:00Z</time></trkpt>\n' +
    '</trkseg><trkseg>\n' +
    '<trkpt lat="-0.5" lon="37.65"><time>2023-05-01T07:10:00Z</time></trkpt>\n' +
    '</trkseg></trk>', HR_NS);
  // ==================== TEST SUITE ====================
  console.log('%c📝 Running tests...', 'color:#FF9800;font-weight:bold;');
  try {
    // ---------- Exact decimal arithmetic ----------
    const d = api.parseDec('55.7512345678');
    assert('Decimal: round trip keeps all digits', api.fmtDec(d.v, d.s), '55.7512345678');
    const e = api.parseDec('1.5e-3');
    assert('Decimal: exponent notation is supported', api.fmtDec(e.v, e.s), '0.0015');
    assert('Decimal: negative value round trip', (() => { const x = api.parseDec('-0.50'); return api.fmtDec(x.v, x.s); })(), '-0.5');
    assert('Decimal: invalid text gives null', api.parseDec('abc'), null);
    assert('Decimal: empty text gives null', api.parseDec(''), null);
    assert('Shift: 0.3 - 0.1 is exactly 0.2 (no float error)', api.shiftToZero(['0.1', '0.3']).out, ['0', '0.2']);
    const sh = api.shiftToZero(['55.75', '-0.5', '37.6200001']);
    assert('Shift: minimum becomes 0, differences kept', sh.out, ['56.25', '0', '38.1200001']);
    assert('Shift: span equals max - min', sh.span, '56.25');
    assert('Shift: null entries stay null', api.shiftToZero(['5', null, '7']).out, ['0', null, '2']);
    // ---------- Time ----------
    assert('Time: +03:00 offset converted to UTC', api.parseTime('2023-05-01T10:00:05.250+03:00').ms, Date.UTC(2023, 4, 1, 7, 0, 5, 250));
    assert('Time: fractional seconds are flagged', api.parseTime('2023-05-01T10:00:05.250Z').frac, true);
    assert('Time: no time zone is treated as UTC', api.parseTime('2023-05-01T07:00:00').ms, Date.UTC(2023, 4, 1, 7, 0, 0));
    assert('Time: -0530 offset without colon', api.parseTime('2023-05-01T00:00:00-0530').ms, Date.UTC(2023, 4, 1, 5, 30, 0));
    assert('Time: invalid text gives null', api.parseTime('yesterday'), null);
    assert('Time: base time formatted without fraction', api.fmtTime(api.BASE_MS, false), '2020-01-01T00:00:00Z');
    assert('Time: base time formatted with fraction', api.fmtTime(api.BASE_MS + 250, true), '2020-01-01T00:00:00.250Z');
    assert('Duration: 3723 s formatted', api.fmtDuration(3723000), '1 h 2 min 3 s');
    assert('Duration: 45 s formatted', api.fmtDuration(45000), '45 s');
    // ---------- Distance ----------
    assertNear('Haversine: 0.0009° of latitude ≈ 100.08 m', api.haversine({ lat: 10, lon: 20 }, { lat: 10.0009, lon: 20 }), 100.08, 0.1);
    assertNear('Haversine: 1° of longitude at equator ≈ 111.195 km', api.haversine({ lat: 0, lon: 0 }, { lat: 0, lon: 1 }) / 1000, 111.195, 0.01);
    // ---------- Parsing & validation ----------
    assertThrows('Parse: invalid XML is rejected', () => api.parseGpx('<gpx><trk>'), /not valid XML/);
    assertThrows('Parse: non-GPX root is rejected', () => api.parseGpx('<kml></kml>'), /not a GPX file/);
    assertThrows('Parse: GPX without points is rejected', () => api.parseGpx(gpx('<trk><trkseg></trkseg></trk>')), /No waypoints/);
    assertThrows('Parse: invalid latitude is rejected', () => api.parseGpx(gpx('<wpt lat="north" lon="1"/>')), /invalid lat\/lon/);
    const m = api.parseGpx(MIXED);
    assert('Parse: all points found (1 wpt + 2 rtept + 3 trkpt)', m.all.length, 6);
    assert('Parse: point kinds in document order', m.all.map((p) => p.kind), ['wpt', 'rtept', 'rtept', 'trkpt', 'trkpt', 'trkpt']);
    assert('Parse: two track segments', m.trks[0].length, 2);
    assert('Parse: slider path uses track points', m.path.length, 3);
    // ---------- Anonymization ----------
    const info = api.anonymize(m, 'keep');
    assert('Anon: lowest latitude becomes 0', m.all[5].aLat, '0');
    assert('Anon: latitude difference kept exactly', m.all[3].aLat, '56.2512345678');
    assert('Anon: lowest longitude becomes 0', m.all[1].aLon, '0');
    assert('Anon: longitude difference kept exactly', m.all[3].aLon, '0.0200001');
    assert('Anon: earliest time (not first point) becomes 2020-01-01', m.all[4].aTime, '2020-01-01T00:00:00.000Z');
    assert('Anon: time difference kept with time zone', m.all[3].aTime, '2020-01-01T00:00:05.250Z');
    assert('Anon: 10 minute gap kept', m.all[5].aTime, '2020-01-01T00:10:00.000Z');
    assert('Anon: point without time stays without time', m.all[0].aTime, null);
    assert('Anon: elevation kept as is', m.all[3].aEle, '150.5');
    assert('Anon: info counts timed points', info.timed, 3);
    api.anonymize(m, 'shift');
    assert('Elevation: shift mode puts lowest at 0', [m.all[0].aEle, m.all[3].aEle, m.all[4].aEle], ['0', '10.5', '9']);
    api.anonymize(m, 'drop');
    assertTrue('Elevation: drop mode removes all elevations', m.all.every((p) => p.aEle === null));
    // ---------- Speed ----------
    const sm = api.parseGpx(speedTrack());
    const si = api.anonymize(sm, 'keep');
    const total = api.haversine({ lat: 10, lon: 20 }, { lat: 10.0135, lon: 20 });
    const fast = api.haversine({ lat: 10, lon: 20 }, { lat: 10.0018, lon: 20 }) / 10 * 3.6;
    assertNear('Speed: average = distance / time', si.vAvg, total / 120 * 3.6, 0.01);
    assertNear('Speed: maximum ≈ 72.06 km/h', si.vMax, fast, 0.01);
    assertNear('Speed: minimum is 0 during the stop', si.vMin, 0, 1e-9);
    assertNear('Speed: track length ≈ 1501 m', si.length, total, 0.5);
    const noTime = api.anonymize(api.parseGpx(gpx('<trk><trkseg><trkpt lat="1" lon="1"/><trkpt lat="1.1" lon="1"/></trkseg></trk>')), 'keep');
    assert('Speed: no timestamps gives no speeds', [noTime.vAvg, noTime.vMax, noTime.vMin], [null, null, null]);
    // ---------- Output generation ----------
    api.anonymize(m, 'keep');
    const out = api.buildGpx(m, false);
    assertStartsWith('GPX: starts with XML declaration', out, '<?xml version="1.0" encoding="UTF-8"?>');
    assertTrue('GPX: creator replaced', out.indexOf('creator="GPX Anonymizer"') !== -1);
    assertTrue('GPX: metadata, names and descriptions removed', !/<metadata|<name|<desc|<author|Secret|Home/.test(out));
    const trkLines = out.split('\n').filter((l) => l.indexOf('<trkpt') !== -1);
    assertTrue('GPX: every <trkpt> is on one line', trkLines.length === 3 && trkLines.every((l) => /<trkpt[^>]*(\/>|>.*<\/trkpt>)\s*$/.test(l)), trkLines.join('\n'));
    assertTrue('GPX: extensions dropped by default', out.indexOf('extensions') === -1);
    const outExt = api.buildGpx(m, true);
    const extLine = outExt.split('\n').find((l) => l.indexOf('gpxtpx:hr') !== -1) || '';
    assertTrue('GPX: extensions kept on the same line when enabled', /<trkpt.*<gpxtpx:hr>120<\/gpxtpx:hr>.*<\/trkpt>/.test(extLine), extLine);
    assertTrue('GPX: extension namespace declared on root', outExt.indexOf('xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"') !== -1);
    const again = api.parseGpx(out);
    api.anonymize(again, 'keep');
    assert('GPX: output parses back with the same points', again.all.map((p) => [p.kind, p.aLat, p.aLon, p.aTime]), m.all.map((p) => [p.kind, p.aLat, p.aLon, p.aTime]));
    const csv = api.buildCsv(m).trim().split('\n');
    assert('CSV: header row', csv[0], 'n,type,lat,lon,ele,time');
    assert('CSV: one row per point', csv.length, 7);
    assert('CSV: track point row', csv[4], '4,trkpt,56.2512345678,0.0200001,150.5,2020-01-01T00:00:05.250Z');
    // ==================== DOM / UI ====================
    api.reset();
    q('sample').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    await waitFor(() => /Done/.test(q('status').textContent), 3000, 'sample to load');
    assertTrue('UI: sample button loads a track', /Done: 423 points/.test(q('status').textContent), q('status').textContent);
    assertTrue('UI: result sections become visible', !q('viz').classList.contains('ga-hidden') && !q('out').classList.contains('ga-hidden'));
    assert('UI: CSV lists every point', q('csv').value.trim().split('\n').length, 424);
    assert('UI: SVG draws 2 track segments', q('svg').querySelectorAll('polyline.ga-trk').length, 2);
    assert('UI: SVG draws 2 waypoints', q('svg').querySelectorAll('circle.ga-wpt').length, 2);
    const statText = q('stats').textContent;
    assertTrue('UI: stats show avg / max / min speed', /Avg speed[\d.]+ km\/h/.test(statText) && /Max speed[\d.]+ km\/h/.test(statText) && /Min speed[\d.]+ km\/h/.test(statText), statText);
    assertTrue('UI: speed note shown', q('note').textContent.length > 0);
    // slider
    q('scrub').value = '120';
    q('scrub').dispatchEvent(new Event('input', { bubbles: true }));
    assertTrue('UI: slider updates the point readout', /^#\s*121 \/ 421/.test(q('readout').textContent), q('readout').textContent);
    // tapping the shape selects the nearest point (3 far-apart points; clientX/Y are whole pixels)
    api.loadText(gpx('<trk><trkseg><trkpt lat="0" lon="0"/><trkpt lat="1" lon="1"/><trkpt lat="0" lon="2"/></trkseg></trk>'));
    const svg = q('svg');
    const tap = (cls) => {
      const dot = svg.querySelector('circle.' + cls), sp = svg.createSVGPoint();
      sp.x = +dot.getAttribute('cx'); sp.y = +dot.getAttribute('cy');
      const scr = sp.matrixTransform(svg.getScreenCTM());
      svg.dispatchEvent(new MouseEvent('click', { bubbles: true, clientX: scr.x, clientY: scr.y }));
      return q('scrub').value;
    };
    assert('UI: tapping the end marker selects the last point', tap('ga-end'), '2');
    assert('UI: tapping the start marker selects point 1', tap('ga-start'), '0');
    q('sample').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    // options
    q('ele').value = 'drop';
    q('ele').dispatchEvent(new Event('change', { bubbles: true }));
    assertTrue('UI: "remove elevation" removes <ele> from output', q('gpx').value.indexOf('<ele>') === -1);
    q('ele').value = 'shift';
    q('ele').dispatchEvent(new Event('change', { bubbles: true }));
    assertTrue('UI: "shift elevation" writes 0 m minimum', /<ele>0<\/ele>/.test(q('gpx').value));
    q('ext').checked = true;
    q('ext').dispatchEvent(new Event('change', { bubbles: true }));
    assertTrue('UI: keep extensions adds heart rate', q('gpx').value.indexOf('<gpxtpx:hr>') !== -1);
    const vb1 = q('svg').getAttribute('viewBox');
    q('aspect').checked = false;
    q('aspect').dispatchEvent(new Event('change', { bubbles: true }));
    assertTrue('UI: proportions toggle redraws the shape', q('svg').getAttribute('viewBox') !== vb1, vb1 + ' vs ' + q('svg').getAttribute('viewBox'));
    // download (anchor click intercepted, no real file saved)
    const origClick = HTMLAnchorElement.prototype.click;
    let dl = null;
    HTMLAnchorElement.prototype.click = function () { dl = { name: this.download, href: this.href }; };
    try {
      q('dlGpx').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    } finally {
      HTMLAnchorElement.prototype.click = origClick;
    }
    assertTrue('UI: Download GPX creates "anonymized.gpx"', dl && dl.name === 'anonymized.gpx' && dl.href.indexOf('blob:') === 0, JSON.stringify(dl));
    // copy
    q('copyCsv').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    await waitFor(() => /Copied|Copy failed/.test(q('copyCsv').textContent), 3000, 'copy feedback').catch(() => {});
    assertTrue('UI: Copy CSV gives feedback', /Copied|Copy failed/.test(q('copyCsv').textContent), q('copyCsv').textContent);
    // file input
    let dtOk = true;
    try { new DataTransfer().items.add(new File(['x'], 'x.gpx')); } catch (err) { dtOk = false; }
    if (dtOk) {
      api.reset();
      const dt = new DataTransfer();
      dt.items.add(new File([speedTrack()], 'test.gpx', { type: 'application/gpx+xml' }));
      q('file').files = dt.files;
      q('file').dispatchEvent(new Event('change', { bubbles: true }));
      await waitFor(() => /Done|error/i.test(q('status').textContent), 4000, 'file to load');
      assertTrue('UI: choosing a file processes it', /Done: 13 points/.test(q('status').textContent), q('status').textContent);
      // drag & drop of an invalid file
      const bad = new DataTransfer();
      bad.items.add(new File(['hello'], 'bad.gpx'));
      q('drop').dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: bad }));
      await waitFor(() => q('status').classList.contains('is-error'), 4000, 'error status');
      assertTrue('UI: dropping an invalid file shows an error', /not valid XML/.test(q('status').textContent), q('status').textContent);
      assertTrue('UI: results hidden after an error', q('viz').classList.contains('ga-hidden'));
    } else {
      console.warn('DataTransfer is not supported here: file input and drop tests skipped.');
    }
    // ---------- paste ----------
    const st = () => q('status').textContent;
    const waitDone = (n, label) => waitFor(() => new RegExp('Done: ' + n + ' points').test(st()), 3000, label).then(() => true, () => false);
    api.reset();
    q('paste').value = speedTrack();
    q('pasteGo').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    assertTrue('Paste: "Anonymize pasted text" processes the box', await waitDone(13, 'paste box'), st());
    api.reset();
    q('pasteGo').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    assertTrue('Paste: empty box shows an error', q('status').classList.contains('is-error') && /empty/.test(st()), st());
    q('paste').value = 'abc';
    q('pasteClear').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    assert('Paste: Clear empties the box', q('paste').value, '');
    const clipEvent = (data) => {
      const dt = new DataTransfer();
      if (typeof data === 'string') dt.setData('text/plain', data); else dt.items.add(data);
      return new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: dt });
    };
    let ceOk = false;
    try { ceOk = !!clipEvent('x').clipboardData; } catch (err) { ceOk = false; }
    if (ceOk) {
      api.reset();
      q('paste').dispatchEvent(clipEvent(speedTrack()));
      assertTrue('Paste: pasting into the box processes it at once', await waitDone(13, 'box paste'), st());
      api.reset();
      const ev = clipEvent(api.sampleGpx());
      document.body.dispatchEvent(ev);
      assertTrue('Paste: Ctrl+V on the page loads GPX text', await waitDone(423, 'page paste'), st());
      assertTrue('Paste: page paste is consumed (default prevented)', ev.defaultPrevented);
      api.reset();
      const plain = clipEvent('just some text');
      document.body.dispatchEvent(plain);
      await sleep(100);
      assertTrue('Paste: non-GPX text on the page is ignored', st() === '' && !plain.defaultPrevented, st());
      const hostInput = document.createElement('input');
      document.body.appendChild(hostInput);
      const hostEv = clipEvent(speedTrack());
      hostInput.dispatchEvent(hostEv);
      await sleep(100);
      document.body.removeChild(hostInput);
      assertTrue('Paste: pasting into another text field on the page is left alone', st() === '' && !hostEv.defaultPrevented, st());
      api.reset();
      document.body.dispatchEvent(clipEvent(new File([speedTrack()], 'copied.gpx', { type: 'application/gpx+xml' })));
      assertTrue('Paste: a copied file is loaded', await waitDone(13, 'file paste'), st());
    } else {
      console.warn('ClipboardEvent with clipboardData is not supported here: paste event tests skipped.');
    }
    if (navigator.clipboard) {
      const clip = navigator.clipboard;
      try {
        api.reset();
        clip.readText = () => Promise.resolve(speedTrack());
        q('clip').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        assertTrue('Clipboard button: reads and processes clipboard text', await waitDone(13, 'clipboard button'), st());
        api.reset();
        clip.readText = () => Promise.reject(new Error('NotAllowedError'));
        q('clip').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        await waitFor(() => /blocked/.test(st()), 3000, 'blocked message').catch(() => {});
        assertTrue('Clipboard button: when blocked, opens the paste box', q('pasteBox').open && /blocked/.test(st()), st());
        api.reset();
        clip.readText = () => Promise.resolve('   ');
        q('clip').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        await waitFor(() => /empty/.test(st()), 3000, 'empty message').catch(() => {});
        assertTrue('Clipboard button: empty clipboard shows an error', /clipboard is empty/i.test(st()), st());
      } finally {
        delete clip.readText;
      }
    } else {
      console.warn('navigator.clipboard is not available here: clipboard button tests skipped.');
    }
    // invalid text via the load path
    api.loadText('<gpx xmlns="http://www.topografix.com/GPX/1/1"></gpx>');
    assertTrue('UI: GPX without points shows an error', q('status').classList.contains('is-error') && /No waypoints/.test(q('status').textContent));
  } catch (err) {
    assertTrue('Test suite execution should not throw exceptions', false, err && err.stack ? err.stack : String(err));
  }
  // ==================== RESET ====================
  api.reset();
  window.scrollTo(0, 0);
  // ==================== SUMMARY & UI ENFORCER ====================
  console.log('%c📊 Final test summary:', 'color:#2f6fde;font-weight:bold;');
  console.table({
    'Total Passed': { Count: passed, Status: passed > 0 ? '✅' : '-' },
    'Total Failed': { Count: failed, Status: failed === 0 ? '✅' : '❌' }
  });
  const color = failed > 0 ? '#f44336' : '#4CAF50';
  const text = '🧪 Tests: ' + passed + ' passed, ' + failed + ' failed. App reset.';
  const detail = failures.slice(0, 5).join('\n') + (failures.length > 5 ? '\n…and ' + (failures.length - 5) + ' more (see console)' : '');
  setTimeout(() => {
    let toast = document.getElementById('gpx-anon-test-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'gpx-anon-test-toast';
      toast.setAttribute('role', 'status');
      document.body.appendChild(toast);
    }
    if (window._gpxToastTimer) clearTimeout(window._gpxToastTimer);
    if (window._gpxToastEnforcer) clearInterval(window._gpxToastEnforcer);
    const enforce = () => {
      const s = toast.style;
      s.position = 'fixed'; s.top = '50%'; s.left = '50%'; s.transform = 'translate(-50%, -50%)';
      s.padding = '24px 28px'; s.width = detail ? 'min(92vw, 640px)' : 'min(92vw, 560px)'; s.maxWidth = '92vw'; s.boxSizing = 'border-box';
      s.fontSize = 'clamp(1.15rem, 5vw, 1.8rem)'; s.fontFamily = 'system-ui, sans-serif'; s.textAlign = 'center'; s.lineHeight = '1.3';
      s.borderRadius = '16px'; s.boxShadow = '0 8px 24px rgba(0,0,0,0.25)';
      s.background = color; s.color = '#fff'; s.zIndex = '99999'; s.display = 'block'; s.opacity = '1';
      if (toast.getAttribute('data-text') !== text + detail) {
        toast.textContent = '';
        const head = document.createElement('div');
        head.textContent = text;
        toast.appendChild(head);
        if (detail) {
          const list = document.createElement('div');
          list.textContent = detail;
          list.style.cssText = 'white-space:pre-line;font-size:.55em;text-align:left;margin-top:12px;opacity:.95;';
          toast.appendChild(list);
        }
        toast.setAttribute('data-text', text + detail);
      }
    };
    enforce();
    window._gpxToastEnforcer = setInterval(enforce, 100);
    window._gpxToastTimer = setTimeout(() => {
      clearInterval(window._gpxToastEnforcer);
      toast.style.display = 'none';
    }, 7000);
  }, 300);
  return { passed, failed, failures };
};
console.log('%c💡 gpx_anonymizer tests loaded. Run window.__runTests() or open the page with ?test=run', 'color:#2f6fde;');
