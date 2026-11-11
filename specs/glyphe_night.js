// Helium Glyphe — convertisseur « nuit rouge » des pages web.
// Injecté par le navigateur dans un monde isolé (DOM partagé, JS séparé).
// Règles de l'Atelier Glyphe : noir pur, une seule teinte rouge ; la forme
// remplace la couleur. Fond -> noir, texte -> rouge (intensité selon le
// contraste d'origine), aplats colorés -> rouge plein + texte noir,
// bordures -> trait rouge, médias -> monochrome rouge (filtre SVG).
(() => {
  'use strict';
  const KEY = '__glypheNight';
  if (window[KEY]) {
    window[KEY].enable();
    return;
  }

  const RED = [217, 68, 51];
  const ATTR = 'data-glyphe-night';
  const STYLE_ID = 'glyphe-night-style';
  const SVG_ID = 'glyphe-night-svg';
  const COLOR_PROPS = [
    ['background-color', 'bg'],
    ['color', 'fg'],
    ['border-top-color', 'border'],
    ['border-right-color', 'border'],
    ['border-bottom-color', 'border'],
    ['border-left-color', 'border'],
    ['outline-color', 'border'],
    ['text-decoration-color', 'fg'],
    ['caret-color', 'fg'],
    ['fill', 'svg'],
    ['stroke', 'svg'],
  ];

  // ---- couleurs -----------------------------------------------------------
  const ctx = document.createElement('canvas').getContext('2d');
  const cache = new Map();

  function parse(value) {
    if (!value || value === 'none' || value === 'transparent' ||
        value.startsWith('url(') || value.includes('var(')) {
      return null;
    }
    let c = cache.get(value);
    if (c !== undefined) return c;
    ctx.fillStyle = '#010203';
    ctx.fillStyle = value;
    const s = ctx.fillStyle;
    c = null;
    if (s.startsWith('#')) {
      c = [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16),
           parseInt(s.slice(5, 7), 16), 1];
      if (s === '#010203' && value.trim() !== '#010203') c = null;
    } else {
      const m = s.match(/rgba?\(([^)]+)\)/);
      if (m) {
        const p = m[1].split(',').map(Number);
        c = [p[0], p[1], p[2], p[3] === undefined ? 1 : p[3]];
      }
    }
    cache.set(value, c);
    return c;
  }

  function luminance([r, g, b]) {
    const f = (v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  }

  function saturation([r, g, b]) {
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    return max === 0 ? 0 : (max - min) / max;
  }

  const red = (a) => `rgba(${RED[0]}, ${RED[1]}, ${RED[2]}, ${+a.toFixed(3)})`;

  // Un aplat « mis en avant » : coloré et moyen (bouton, badge, surlignage).
  function isAccent(c) {
    const l = luminance(c);
    return saturation(c) > 0.35 && l > 0.06 && l < 0.75 && c[3] > 0.5;
  }

  // Déjà dans la palette (noir ou rouge Glyphe) : ne pas convertir deux fois.
  function isOurs(c) {
    return (c[0] === 0 && c[1] === 0 && c[2] === 0) ||
           (c[0] === RED[0] && c[1] === RED[1] && c[2] === RED[2]);
  }

  function mapColor(c, role, el) {
    if (!c || isOurs(c)) return null;
    const a = c[3];
    if (a === 0) return 'transparent';
    const l = luminance(c);
    switch (role) {
      case 'bg':
        if (isAccent(c)) return red(a);
        // Surfaces : noir, avec une trace rouge pour garder l'élévation.
        return l > 0.5 ? `rgba(0, 0, 0, ${a})` : red(Math.min(0.18, (1 - l) * 0.12) * a);
      case 'fg': {
        // Texte sur aplat rouge : noir.
        if (el && el[ATTR + 'OnAccent']) return '#000';
        // Plus le texte était contrasté, plus il est franc.
        const strength = l < 0.5 ? 1 - l * 1.2 : 0.55 + l * 0.45;
        return red(Math.max(0.55, Math.min(1, strength)) * a);
      }
      case 'border':
        return red(0.45 * a);
      case 'svg':
        return isAccent(c) || l < 0.5 ? red(a) : red(0.6 * a);
    }
    return null;
  }


  // Feuille adoptée : la CSP « style-src » de la page ne la bloque pas.
  const sheets = new Map();
  function setSheet(id, text) {
    let sheet = sheets.get(id);
    try {
      if (!sheet) {
        sheet = new CSSStyleSheet();
        sheets.set(id, sheet);
        document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
      }
      sheet.replaceSync(text);
      return;
    } catch (e) { /* repli ci-dessous */ }
    let style = document.getElementById(id);
    if (!style) {
      style = document.createElement('style');
      style.id = id;
      (document.head || document.documentElement).appendChild(style);
    }
    style.textContent = text;
  }

  // ---- feuilles de style : on réécrit les règles ---------------------------
  const processedSheets = new WeakSet();
  const overrideRules = [];

  function rewriteRule(rule) {
    if (rule.cssRules) {
      for (const r of rule.cssRules) rewriteRule(r);
      return;
    }
    if (!rule.style || !rule.selectorText) return;
    const decls = [];
    for (const [prop, role] of COLOR_PROPS) {
      const v = rule.style.getPropertyValue(prop);
      if (!v) continue;
      const mapped = mapColor(parse(v), role);
      if (mapped) decls.push(`${prop}: ${mapped} !important`);
    }
    const bgImage = rule.style.getPropertyValue('background-image') ||
                    rule.style.getPropertyValue('background');
    if (bgImage && bgImage.includes('gradient')) {
      decls.push('background-image: none !important');
    }
    if (rule.style.getPropertyValue('box-shadow')) {
      decls.push(`box-shadow: none !important`);
    }
    if (decls.length) {
      overrideRules.push(`${rule.selectorText} { ${decls.join('; ')} }`);
    }
  }

  function processSheets() {
    let changed = false;
    for (const sheet of document.styleSheets) {
      if (processedSheets.has(sheet)) continue;
      if (sheet.ownerNode && sheet.ownerNode.id && sheet.ownerNode.id.startsWith(STYLE_ID)) continue;
      processedSheets.add(sheet);
      let rules;
      try {
        rules = sheet.cssRules;  // Feuilles d'une autre origine : illisibles.
      } catch (e) {
        continue;
      }
      for (const r of rules) rewriteRule(r);
      changed = true;
    }
    if (changed) flushOverrides();
  }

  function flushOverrides() {
    setSheet(STYLE_ID + '-rules', overrideRules.join('\n'));
  }

  // ---- styles calculés : éléments inline et sans règle lisible -------------
  const done = new WeakSet();

  // Icône dessinée par un masque : sa couleur de fond est la couleur du trait.
  function hasMask(cs) {
    const m = cs.maskImage || cs.webkitMaskImage;
    return !!m && m !== 'none';
  }

  // Pseudo-éléments (::before / ::after) : pas de style inline possible, on
  // génère une règle partagée par toutes les déclarations identiques.
  const PSEUDO_ATTR = {'::before': ATTR + '-b', '::after': ATTR + '-a'};
  const pseudoKeys = new Map();
  const pseudoRules = [];
  let pseudoDirty = false;

  function processPseudo(el, which, accent) {
    const cs = getComputedStyle(el, which);
    const content = cs.content;
    if (!content || content === 'none' || content === 'normal') return;
    const decls = [];
    const bg = parse(cs.backgroundColor);
    if (bg && bg[3] > 0 && !isOurs(bg)) {
      const role = hasMask(cs) ? 'svg' : 'bg';
      decls.push(`background-color: ${accent && role === 'svg' ? '#000' : mapColor(bg, role)}`);
    }
    if (cs.backgroundImage && cs.backgroundImage !== 'none') {
      decls.push(cs.backgroundImage.includes('gradient')
          ? 'background-image: none' : 'filter: url(#glyphe-night-red)');
    }
    const fg = parse(cs.color);
    if (fg && !isOurs(fg)) decls.push(`color: ${accent ? '#000' : mapColor(fg, 'fg')}`);
    if (parseFloat(cs.borderTopWidth) || parseFloat(cs.borderBottomWidth) ||
        parseFloat(cs.borderLeftWidth) || parseFloat(cs.borderRightWidth)) {
      decls.push(`border-color: ${red(0.45)}`);
    }
    if (cs.boxShadow && cs.boxShadow !== 'none') decls.push('box-shadow: none');
    if (!decls.length) return;
    const body = decls.map((d) => d + ' !important').join('; ');
    const attr = PSEUDO_ATTR[which];
    const mapKey = which + body;
    let k = pseudoKeys.get(mapKey);
    if (k === undefined) {
      k = 'k' + pseudoKeys.size;
      pseudoKeys.set(mapKey, k);
      pseudoRules.push(`[${attr}="${k}"]${which} { ${body} }`);
      pseudoDirty = true;
    }
    el.setAttribute(attr, k);
  }

  function flushPseudo() {
    if (!pseudoDirty) return;
    pseudoDirty = false;
    setSheet(STYLE_ID + '-pseudo', pseudoRules.join('\n'));
  }

  function processElement(el) {
    if (done.has(el) || el.nodeType !== 1) return;
    done.add(el);
    const tag = el.tagName;
    if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'LINK' || tag === 'META') return;
    const cs = getComputedStyle(el);
    const bg = parse(cs.backgroundColor);
    if (bg && bg[3] > 0 && hasMask(cs)) {
      // Icône à masque : trait rouge (noir sur un aplat rouge).
      const onAccent = el.parentElement && el.parentElement[ATTR + 'OnAccent'];
      if (!isOurs(bg) || onAccent) {
        el.style.setProperty('background-color', onAccent ? '#000' : mapColor(bg, 'svg'), 'important');
      }
    } else if (bg && bg[3] > 0 && isOurs(bg) && bg[0] === RED[0]) {
      el[ATTR + 'OnAccent'] = true;  // aplat déjà converti par une règle
      el.setAttribute(ATTR + '-accent', '');
    } else if (bg && bg[3] > 0 && !isOurs(bg)) {
      if (isAccent(bg)) {
        el[ATTR + 'OnAccent'] = true;
        el.style.setProperty('background-color', red(bg[3]), 'important');
        el.style.setProperty('color', '#000', 'important');
        el.setAttribute(ATTR + '-accent', '');
      } else {
        el.style.setProperty('background-color', mapColor(bg, 'bg'), 'important');
      }
    }
    if (cs.backgroundImage && cs.backgroundImage.includes('gradient')) {
      el.style.setProperty('background-image', 'none', 'important');
    }
    if (!el[ATTR + 'OnAccent']) {
      const parentAccent = el.parentElement && el.parentElement[ATTR + 'OnAccent'];
      if (parentAccent) {
        el[ATTR + 'OnAccent'] = true;
        el.style.setProperty('color', '#000', 'important');
      } else {
        const fg = mapColor(parse(cs.color), 'fg', el);
        if (fg) el.style.setProperty('color', fg, 'important');
      }
    }
    if (parseFloat(cs.borderTopWidth) || parseFloat(cs.borderBottomWidth) ||
        parseFloat(cs.borderLeftWidth) || parseFloat(cs.borderRightWidth)) {
      el.style.setProperty('border-color', red(0.45), 'important');
    }
    if (cs.boxShadow && cs.boxShadow !== 'none') {
      el.style.setProperty('box-shadow', 'none', 'important');
    }
    processPseudo(el, '::before', !!el[ATTR + 'OnAccent']);
    processPseudo(el, '::after', !!el[ATTR + 'OnAccent']);
  }

  function walk(root) {
    if (root.nodeType === 1) processElement(root);
    const it = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
    let n;
    let count = 0;
    while ((n = it.nextNode())) {
      processElement(n);
      if (n.shadowRoot) walk(n.shadowRoot);
      if (++count > 20000) break;  // garde-fou sur les très grosses pages
    }
    flushPseudo();
  }

  // ---- base : fond, médias, sélection --------------------------------------
  function baseCss() {
    return `
:root, html, body { background-color: #000 !important; color-scheme: dark !important; }
html { color: ${red(1)} !important; }
::selection { background: ${red(1)} !important; color: #000 !important; }
mark { background: ${red(1)} !important; color: #000 !important; }
a, a * { color: ${red(1)} !important; text-decoration-color: ${red(0.6)} !important; }
input, textarea, select, button {
  background-color: #000 !important; color: ${red(1)} !important;
  border-color: ${red(0.58)} !important; }
img, video, picture, canvas, svg image, [style*="background-image"] {
  filter: url(#glyphe-night-red) !important; }
iframe { filter: none !important; }
hr { border-color: ${red(0.45)} !important; background: ${red(0.45)} !important; }
::-webkit-scrollbar { background: #000 !important; }
::-webkit-scrollbar-thumb { background: ${red(0.45)} !important; }
[${ATTR}-accent] * { color: #000 !important; }
`;
  }

  function installBase() {
    if (!sheets.has(STYLE_ID)) setSheet(STYLE_ID, baseCss());
    if (!document.getElementById(SVG_ID)) {
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.id = SVG_ID;
      svg.setAttribute('aria-hidden', 'true');
      svg.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
      // Luminance (Rec. 709) -> canal rouge seul, assombrie à 85 %.
      svg.innerHTML = `<filter id="glyphe-night-red" color-interpolation-filters="sRGB">
        <feColorMatrix type="matrix" values="
          0.13 0.43 0.04 0 0
          0.03 0.10 0.01 0 0
          0.02 0.08 0.01 0 0
          0 0 0 1 0"/></filter>`;
      (document.body || document.documentElement).appendChild(svg);
    }
  }

  // ---- cycle de vie ----------------------------------------------------------
  let observer = null;
  let pending = new Set();
  let scheduled = false;

  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      processSheets();
      for (const n of pending) walk(n);
      pending = new Set();
    });
  }

  function enable() {
    document.documentElement.setAttribute(ATTR, '');
    installBase();
    processSheets();
    if (document.body) walk(document.body);
    if (!observer) {
      observer = new MutationObserver((records) => {
        for (const r of records) {
          for (const n of r.addedNodes) {
            if (n.nodeType === 1) {
              pending.add(n);
              if (n.tagName === 'STYLE' || n.tagName === 'LINK') {
                n.addEventListener('load', schedule, {once: true});
              }
            }
          }
        }
        if (pending.size) schedule();
      });
      observer.observe(document.documentElement, {childList: true, subtree: true});
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        installBase();
        processSheets();
        walk(document.body);
      }, {once: true});
    }
  }

  function disable() {
    // Le plus sûr pour retrouver la page d'origine : recharger.
    if (observer) observer.disconnect();
    location.reload();
  }

  window[KEY] = {enable, disable};
  enable();
})();
