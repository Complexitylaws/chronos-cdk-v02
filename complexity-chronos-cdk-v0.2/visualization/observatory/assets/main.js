/**
 * Chronos CDK - Observatory Client v2
 * ====================================
 * Arena game client that renders NPC behavior from the Chronos engine API.
 * NPCs are NOT scripted client-side - all intents come from the engine.
 */

const API_BASE = '';
const POLL_MS = 1000;
const NPC_COUNT = 8;
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let W, H;

function resize() {
  const rect = canvas.parentElement.getBoundingClientRect();
  W = canvas.width = rect.width;
  H = canvas.height = rect.height;
}
window.addEventListener('resize', resize);
resize();

// -- Engine State --
let engineState = null;
let prevMood = '';

// -- Player --
const player = {
  x: 0, y: 0, vx: 0, vy: 0,
  speed: 3, hp: 200, maxHp: 200,
  armed: false, dead: false, kills: 0,
};
player.x = W / 2;
player.y = H / 2;

// -- NPCs --
const npcs = [];
function initNPCs() {
  for (let i = 0; i < NPC_COUNT; i++) {
    npcs.push({
      id: i, x: Math.random() * W, y: Math.random() * H,
      vx: 0, vy: 0, hp: 100, maxHp: 100,
      intent: 'idle', coalition: 'neutral', color: '#58a6ff',
      reason: '', dead: false, orbitAngle: Math.random() * Math.PI * 2,
      trail: [],
    });
  }
}

// -- Input --
const keys = {};
window.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key === ' ') { player.armed = !player.armed; postPlayerState(false); }
  if (e.key.toLowerCase() === 'g') { postPlayerState(true); }
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

// -- Spatial: Obstacles --
const obstacles = [
  { x: 0.25, y: 0.3, w: 0.08, h: 0.25 },
  { x: 0.7,  y: 0.5, w: 0.06, h: 0.3 },
  { x: 0.4,  y: 0.75, w: 0.2, h: 0.05 },
  { x: 0.5,  y: 0.15, w: 0.15, h: 0.04 },
];

function getObstacleRects() {
  return obstacles.map(o => ({ x: o.x * W, y: o.y * H, w: o.w * W, h: o.h * H }));
}

function isInsideObstacle(px, py, margin) {
  margin = margin || 0;
  for (const o of getObstacleRects()) {
    if (px > o.x - margin && px < o.x + o.w + margin &&
        py > o.y - margin && py < o.y + o.h + margin) return true;
  }
  return false;
}

// -- Flocking --
function applyFlocking(npc) {
  let cohX = 0, cohY = 0, cohN = 0;
  let sepX = 0, sepY = 0;
  for (const other of npcs) {
    if (other.id === npc.id || other.dead) continue;
    const dx = other.x - npc.x, dy = other.y - npc.y;
    const dist = Math.hypot(dx, dy);
    if (dist < 30 && dist > 0) {
      sepX -= (dx / dist) * (30 - dist) * 0.05;
      sepY -= (dy / dist) * (30 - dist) * 0.05;
    }
    if (other.coalition === npc.coalition && dist < 150) {
      cohX += other.x; cohY += other.y; cohN++;
    }
  }
  if (cohN > 0) {
    cohX /= cohN; cohY /= cohN;
    npc.vx += (cohX - npc.x) * 0.003;
    npc.vy += (cohY - npc.y) * 0.003;
  }
  npc.vx += sepX; npc.vy += sepY;
}

// -- Player Movement --
function updatePlayer() {
  if (player.dead) return;
  let dx = 0, dy = 0;
  if (keys['w'] || keys['arrowup']) dy -= 1;
  if (keys['s'] || keys['arrowdown']) dy += 1;
  if (keys['a'] || keys['arrowleft']) dx -= 1;
  if (keys['d'] || keys['arrowright']) dx += 1;
  const len = Math.hypot(dx, dy);
  if (len > 0) { dx = dx / len * player.speed; dy = dy / len * player.speed; }
  let newPX = Math.max(14, Math.min(W - 14, player.x + dx));
  let newPY = Math.max(14, Math.min(H - 14, player.y + dy));
  if (!isInsideObstacle(newPX, newPY, 10)) {
    player.x = newPX; player.y = newPY;
  } else {
    if (!isInsideObstacle(newPX, player.y, 10)) player.x = newPX;
    else if (!isInsideObstacle(player.x, newPY, 10)) player.y = newPY;
  }
}

// -- NPC Physics --
function updateNPCs() {
  if (player.dead) return;
  const intensity = engineState ? (engineState.intensity || 0.5) : 0.5;
  const speedMul = 0.8 + intensity * 1.5;

  for (const npc of npcs) {
    if (npc.dead) continue;
    let tx = npc.x, ty = npc.y;
    let speed = 0.5 * speedMul;

    switch (npc.intent) {
      case 'attack':
        tx = player.x; ty = player.y;
        speed = 1.4 * speedMul;
        break;
      case 'flee': {
        const dx = npc.x - player.x, dy = npc.y - player.y;
        const d = Math.hypot(dx, dy) || 1;
        tx = npc.x + (dx / d) * 100; ty = npc.y + (dy / d) * 100;
        speed = 1.6 * speedMul;
        break;
      }
      case 'guard': {
        const angle = (npc.id / NPC_COUNT) * Math.PI * 2;
        tx = player.x + Math.cos(angle) * 100;
        ty = player.y + Math.sin(angle) * 100;
        speed = 1.0 * speedMul;
        break;
      }
      case 'orbit': {
        npc.orbitAngle += 0.015 * speedMul;
        const r = 120 + Math.sin(npc.orbitAngle * 0.5) * 30;
        tx = player.x + Math.cos(npc.orbitAngle) * r;
        ty = player.y + Math.sin(npc.orbitAngle) * r;
        speed = 1.2 * speedMul;
        break;
      }
      case 'scatter': {
        tx = npc.x + (Math.random() - 0.5) * 80;
        ty = npc.y + (Math.random() - 0.5) * 80;
        speed = 1.8 * speedMul;
        break;
      }
      case 'curious': {
        const cdx = player.x - npc.x, cdy = player.y - npc.y;
        const cd = Math.hypot(cdx, cdy) || 1;
        const targetDist = 60;
        if (cd > targetDist) {
          tx = npc.x + (cdx / cd) * 20;
          ty = npc.y + (cdy / cd) * 20;
        } else {
          npc.orbitAngle += 0.01;
          tx = player.x + Math.cos(npc.orbitAngle) * targetDist;
          ty = player.y + Math.sin(npc.orbitAngle) * targetDist;
        }
        speed = 0.7 * speedMul;
        break;
      }
      default:
        tx = npc.x + (Math.random() - 0.5) * 10;
        ty = npc.y + (Math.random() - 0.5) * 10;
        speed = 0.3;
    }

    const dx = tx - npc.x, dy = ty - npc.y;
    const dist = Math.hypot(dx, dy);
    if (dist > 1) {
      npc.vx += (dx / dist) * speed * 0.15;
      npc.vy += (dy / dist) * speed * 0.15;
    }
    npc.vx *= 0.92; npc.vy *= 0.92;

    // Flocking
    applyFlocking(npc);

    // Obstacle avoidance
    for (const o of getObstacleRects()) {
      const cx = Math.max(o.x, Math.min(npc.x, o.x + o.w));
      const cy = Math.max(o.y, Math.min(npc.y, o.y + o.h));
      const odx = npc.x - cx, ody = npc.y - cy;
      const odist = Math.hypot(odx, ody);
      if (odist < 20 && odist > 0) {
        const push = (20 - odist) * 0.15;
        npc.vx += (odx / odist) * push;
        npc.vy += (ody / odist) * push;
      }
    }

    const spd = Math.hypot(npc.vx, npc.vy);
    const maxSpd = speed * 1.5;
    if (spd > maxSpd) { npc.vx = npc.vx / spd * maxSpd; npc.vy = npc.vy / spd * maxSpd; }

    npc.x = Math.max(14, Math.min(W - 14, npc.x + npc.vx));
    npc.y = Math.max(14, Math.min(H - 14, npc.y + npc.vy));
    npc.trail.push({ x: npc.x, y: npc.y });
    if (npc.trail.length > 40) npc.trail.shift();
  }
}

// -- Combat --
const npcHitFlash = new Map();
let screenShake = 0;
let damageFlash = 0;

function handleCombat() {
  if (player.dead) return;
  for (const npc of npcs) {
    if (npc.dead) continue;
    const dist = Math.hypot(npc.x - player.x, npc.y - player.y);

    // NPC attacks player
    if (npc.intent === 'attack' && dist < 20) {
      player.hp -= 0.15;
      damageFlash = Math.min(damageFlash + 0.1, 0.6);
      screenShake = Math.max(screenShake, 2);
      if (player.hp <= 0) {
        player.hp = 0; player.dead = true;
        storyPush('You have fallen.', 'danger');
      }
    }

    // Player attacks NPC
    if (player.armed && dist < 24) {
      npc.hp -= 0.5;
      npcHitFlash.set(npc.id, 6);
      if (npc.hp <= 0) {
        npc.hp = 0; npc.dead = true; player.kills++;
        postPlayerState(false);
        storyPush('A' + (npc.id + 1) + ' [' + npc.coalition + '] was killed!', 'danger');
      }
    }
  }
}

// -- Render --
const INTENT_COLORS = {
  attack: '#f85149', flee: '#58a6ff', guard: '#3fb950',
  orbit: '#d2a8ff', scatter: '#ffa657', curious: '#ce93d8', idle: '#555',
};
const COALITION_COLORS = { red: '#f85149', green: '#3fb950', blue: '#58a6ff', neutral: '#484f58' };
const MOOD_COLORS = { chaos: '#f85149', danger: '#ff6b6b', calm: '#3fb950', stable: '#56d364', loop: '#58a6ff', pulse: '#79c0ff', fragment: '#ffa657', rising: '#d2a8ff', complex: '#bc8cff', shift: '#8b949e', neutral: '#484f58' };
const MOOD_DESC = { chaos: 'Instability dominates', danger: 'Critical threat detected', calm: 'Equilibrium achieved', stable: 'Steady state', loop: 'Recursive patterns', pulse: 'Rhythmic oscillation', fragment: 'Structure breaking down', rising: 'Building toward emergence', complex: 'Deep interconnections', shift: 'Transition in progress' };

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function draw(t) {
  // Background
  ctx.fillStyle = '#050608';
  ctx.fillRect(0, 0, W, H);

  // Mood gradient
  const moodCol = engineState ? MOOD_COLORS[engineState.mood] || '#484f58' : '#484f58';
  const [r, g, b] = hexToRgb(moodCol);
  const grd = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, W * 0.6);
  grd.addColorStop(0, `rgba(${r},${g},${b},0.06)`);
  grd.addColorStop(1, 'transparent');
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, W, H);

  // Grid
  ctx.strokeStyle = 'rgba(20,40,80,0.2)';
  ctx.lineWidth = 1;
  for (let x = 0; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

  // Obstacles
  ctx.fillStyle = 'rgba(40, 60, 100, 0.6)';
  ctx.strokeStyle = 'rgba(80, 120, 180, 0.8)';
  ctx.lineWidth = 2;
  for (const o of getObstacleRects()) {
    ctx.fillRect(o.x, o.y, o.w, o.h);
    ctx.strokeRect(o.x, o.y, o.w, o.h);
  }

  // NPC trails
  for (const npc of npcs) {
    if (npc.dead) continue;
    const col = INTENT_COLORS[npc.intent] || '#555';
    if (npc.trail.length > 2) {
      ctx.beginPath();
      ctx.strokeStyle = col + '30';
      ctx.lineWidth = 1;
      ctx.moveTo(npc.trail[0].x, npc.trail[0].y);
      for (let i = 1; i < npc.trail.length; i++) ctx.lineTo(npc.trail[i].x, npc.trail[i].y);
      ctx.stroke();
    }
  }

  // NPCs
  for (const npc of npcs) {
    if (npc.dead) continue;
    const col = INTENT_COLORS[npc.intent] || '#555';
    const coalCol = COALITION_COLORS[npc.coalition] || '#484f58';
    const [nr, ng, nb] = hexToRgb(col);

    // Coalition ring
    ctx.beginPath();
    ctx.strokeStyle = coalCol;
    ctx.lineWidth = 2;
    ctx.arc(npc.x, npc.y, 11, 0, Math.PI * 2);
    ctx.stroke();

    // Glow
    const glow = ctx.createRadialGradient(npc.x, npc.y, 0, npc.x, npc.y, 18);
    glow.addColorStop(0, `rgba(${nr},${ng},${nb},0.3)`);
    glow.addColorStop(1, 'transparent');
    ctx.beginPath(); ctx.fillStyle = glow; ctx.arc(npc.x, npc.y, 18, 0, Math.PI * 2); ctx.fill();

    // Core
    const hitFrames = npcHitFlash.get(npc.id) || 0;
    ctx.beginPath();
    ctx.fillStyle = hitFrames > 0 ? '#ffffff' : col;
    ctx.arc(npc.x, npc.y, hitFrames > 0 ? 8 : 6, 0, Math.PI * 2);
    ctx.fill();
    if (hitFrames > 0) npcHitFlash.set(npc.id, hitFrames - 1);

    // HP bar
    const hpPct = npc.hp / npc.maxHp;
    const barW = 24, barH = 3;
    ctx.fillStyle = '#1a2a3a';
    ctx.fillRect(npc.x - barW / 2, npc.y + 10, barW, barH);
    ctx.fillStyle = hpPct > 0.5 ? '#3fb950' : hpPct > 0.25 ? '#ffa657' : '#f85149';
    ctx.fillRect(npc.x - barW / 2, npc.y + 10, barW * hpPct, barH);

    // Leader crown + anger aura
    const eNpc = engineState && engineState.npcs && engineState.npcs['A' + (npc.id + 1)];
    if (eNpc && eNpc.is_leader) {
      ctx.font = '12px serif'; ctx.textAlign = 'center';
      ctx.fillText('\u{1F451}', npc.x, npc.y - 20);
    }
    if (eNpc && eNpc.anger > 0.4) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(248,81,73,' + (eNpc.anger * 0.6) + ')';
      ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]);
      ctx.arc(npc.x, npc.y, 15 + eNpc.anger * 5, 0, Math.PI * 2);
      ctx.stroke(); ctx.setLineDash([]);
    }

    // Label
    ctx.font = '9px Courier New'; ctx.fillStyle = col; ctx.textAlign = 'center';
    ctx.fillText('A' + (npc.id + 1), npc.x, npc.y - 14);
    ctx.font = '8px Courier New'; ctx.fillStyle = `rgba(${nr},${ng},${nb},0.5)`;
    ctx.fillText(npc.intent, npc.x, npc.y + 20);
    ctx.textAlign = 'left';
  }

  // Player
  if (!player.dead) {
    ctx.beginPath();
    ctx.fillStyle = player.armed ? '#ff5555' : '#ffffff';
    ctx.arc(player.x, player.y, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.strokeStyle = player.armed ? '#ff5555' : '#3fb950';
    ctx.lineWidth = 2;
    ctx.arc(player.x, player.y, 14, 0, Math.PI * 2);
    ctx.stroke();
    ctx.font = '10px Courier New'; ctx.fillStyle = '#fff'; ctx.textAlign = 'center';
    ctx.fillText('YOU', player.x, player.y - 18);
    ctx.textAlign = 'left';
  }

  // Damage flash
  if (damageFlash > 0) {
    ctx.fillStyle = `rgba(255,0,0,${damageFlash * 0.3})`;
    ctx.fillRect(0, 0, W, H);
    damageFlash *= 0.9;
    if (damageFlash < 0.01) damageFlash = 0;
  }

  // Screen shake
  if (screenShake > 0) {
    canvas.style.transform = `translate(${(Math.random() - 0.5) * screenShake}px, ${(Math.random() - 0.5) * screenShake}px)`;
    screenShake *= 0.85;
    if (screenShake < 0.2) { screenShake = 0; canvas.style.transform = ''; }
  }
}

// -- Map Intents from Engine --
function mapIntentsFromEngine() {
  if (!engineState || !engineState.npcs) return;
  for (const npc of npcs) {
    const key = 'A' + (npc.id + 1);
    const data = engineState.npcs[key];
    if (data) {
      npc.intent = data.intent || 'idle';
      npc.coalition = data.coalition || 'neutral';
      npc.color = INTENT_COLORS[npc.intent] || '#555';
      npc.reason = data.reason || '';
    }
  }
}

// -- HUD --
function updateHUD() {
  if (!engineState) return;
  const mc = MOOD_COLORS[engineState.mood] || '#8b949e';
  document.getElementById('hud-mood').textContent = (engineState.mood || '-').toUpperCase();
  document.getElementById('hud-mood').style.color = mc;
  document.getElementById('hud-fitness').textContent = engineState.fitness || '-';
  document.getElementById('hud-niche').textContent = engineState.niche || '-';
  document.getElementById('hud-gen').textContent = engineState.generation || '-';
  document.getElementById('hud-disc').textContent = engineState.discoveries || '-';
  document.getElementById('hud-ops').textContent = (engineState.operators || []).join(', ') || '-';
  document.getElementById('hud-planck').textContent = engineState.planck ? 'ACTIVE' : 'inactive';

  // Player
  const hpColor = player.hp > 60 ? '#3fb950' : player.hp > 30 ? '#ffa657' : '#f85149';
  document.getElementById('player-status').innerHTML =
    '<div style="margin-bottom:4px">HP: <strong style="color:' + hpColor + '">' + Math.round(player.hp) + '</strong> / ' + player.maxHp + '</div>' +
    '<div class="hp-bar-bg"><div class="hp-bar" style="width:' + player.hp + '%;background:' + hpColor + '"></div></div>' +
    '<div style="margin-top:6px">' + (player.armed
      ? '<span style="color:#f85149;font-size:12px">&#x2694; WEAPON DRAWN</span>'
      : '<span style="color:#3fb950;font-size:12px">&#x1f6e1; WEAPON HOLSTERED</span>') + '</div>';

  // NPC list
  const npcEl = document.getElementById('npc-list');
  npcEl.innerHTML = npcs.map(npc => {
    if (npc.dead) return '<div class="npc-card" style="opacity:0.3"><span class="npc-id">A' + (npc.id + 1) + '</span> <span style="color:#f85149">DEAD</span></div>';
    const eData = engineState && engineState.npcs && engineState.npcs['A' + (npc.id + 1)] || {};
    const leader = eData.is_leader ? '<span style="color:gold;font-size:10px"> &#x1f451;</span>' : '';
    const emo = [];
    if ((eData.anger || 0) > 0.3) emo.push('<span style="color:#f85149" title="anger">&#x1f4a2;</span>');
    if ((eData.grief || 0) > 0.3) emo.push('<span style="color:#58a6ff" title="grief">&#x1f4a7;</span>');
    if ((eData.loyalty || 0) > 0.5) emo.push('<span style="color:#3fb950" title="loyal">&#x1f91d;</span>');
    if ((eData.trust || 0) > 0.4) emo.push('<span style="color:#ce93d8" title="trust">&#x1f49c;</span>');
    if ((eData.fear || 0) > 0.4) emo.push('<span style="color:#ffa657" title="fear">&#x26a0;</span>');
    const hpPct = Math.round(npc.hp);
    return '<div class="npc-card">' +
      '<span class="npc-id" style="color:' + npc.color + '">A' + (npc.id + 1) + '</span>' + leader +
      ' <span class="intent-tag intent-' + npc.intent + '">' + npc.intent + '</span>' +
      ' <span class="coalition-tag coalition-' + npc.coalition + '">' + npc.coalition + '</span> ' +
      emo.join('') +
      '<div class="hp-bar-bg"><div class="hp-bar" style="width:' + hpPct + '%;background:' + (hpPct > 50 ? '#3fb950' : hpPct > 25 ? '#ffa657' : '#f85149') + '"></div></div>' +
      '<div class="npc-reason">' + npc.reason + '</div></div>';
  }).join('');

  // Messages
  const msgs = engineState.messages || [];
  document.getElementById('msg-panel').innerHTML = msgs.slice(0, 8).map(m =>
    '<div class="msg-line"><span class="msg-from">' + m.from + '</span> -> <span class="msg-to">' + m.to + '</span>: <span class="msg-type">' + m.type + '</span> (' + m.content + ')</div>'
  ).join('');
}

// -- Mood Banner --
function checkMoodBanner() {
  if (!engineState) return;
  const mood = engineState.mood || 'neutral';
  if (mood !== prevMood && prevMood !== '') {
    const mc = MOOD_COLORS[mood] || '#8b949e';
    const desc = MOOD_DESC[mood] || '';
    document.getElementById('banner-text').textContent = 'MOOD SHIFT: ' + mood.toUpperCase();
    document.getElementById('banner-sub').textContent = desc;
    const banner = document.getElementById('mood-banner');
    banner.style.color = mc;
    banner.classList.add('show');
    setTimeout(() => banner.classList.remove('show'), 3500);
    storyPush('Mood shifted to ' + mood.toUpperCase() + ' - ' + desc, 'new');
  }
  prevMood = mood;
}

// -- Story Feed --
const storyLines = [];
function storyPush(msg, cls) {
  const t = new Date().toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  storyLines.unshift({ t, msg, cls: cls || '' });
  if (storyLines.length > 20) storyLines.pop();
  document.getElementById('story-feed').innerHTML = storyLines.map(l =>
    '<div class="story-line ' + l.cls + '">[' + l.t + '] ' + l.msg + '</div>'
  ).join('');
}

// -- Narrative Events --
let _lastNarrativeCount = 0;
function renderNarrativeEvents() {
  if (!engineState || !engineState.narrative) return;
  const events = engineState.narrative;
  if (events.length > _lastNarrativeCount) {
    for (let i = _lastNarrativeCount; i < events.length; i++) {
      const ev = events[i];
      const cls = ev.type === 'betrayal' ? 'danger' : ev.type === 'hunt' ? 'danger' : 'new';
      storyPush('[' + ev.name + '] ' + ev.desc, cls);
    }
    _lastNarrativeCount = events.length;
  }
}

// -- Player State -> Engine --
let _giftActiveUntil = 0;
async function postPlayerState(giftActive) {
  if (giftActive) _giftActiveUntil = Date.now() + 3000;
  const isGiftActive = Date.now() < _giftActiveUntil;
  try {
    await fetch(API_BASE + '/api/arena/player', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        armed: player.armed,
        gift_active: isGiftActive,
        kills: player.kills,
        x: player.x / W,
        y: player.y / H,
      })
    });
  } catch (e) { /* silent */ }
}

// -- Engine Polling --
async function pollEngine() {
  try {
    await postPlayerState(false);
    const r = await fetch(API_BASE + '/api/game/state');
    if (!r.ok) throw new Error('http ' + r.status);
    engineState = await r.json();
    document.getElementById('engine-json').innerHTML = highlightJSON(engineState);
    mapIntentsFromEngine();
    renderNarrativeEvents();
    updateHUD();
    checkMoodBanner();
  } catch (e) {
    document.getElementById('engine-json').textContent =
      '{ error: "' + e.message + '",\n  hint: "Start engine: python -m engine" }';
  }
}

// -- JSON Highlight --
function highlightJSON(obj) {
  const s = JSON.stringify(obj, null, 1);
  return s
    .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
    .replace(/: "([^"]*)"/g, ': <span class="json-str">"$1"</span>')
    .replace(/: (\d+\.?\d*)/g, ': <span class="json-num">$1</span>')
    .replace(/: (true|false)/g, ': <span class="json-bool">$1</span>');
}

// -- Game Loop --
function frame(t) {
  requestAnimationFrame(frame);
  updatePlayer();
  updateNPCs();
  handleCombat();
  draw(t);
}

// -- Boot --
initNPCs();
storyPush('Observatory v2 initialized. Connecting to Chronos...', 'new');
pollEngine();
setInterval(pollEngine, POLL_MS);
requestAnimationFrame(frame);
