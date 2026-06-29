/**
 * Chronos CDK v0.2 - Observatory Frontend
 * Real-time NPC behavior visualization with field display
 */

const API_BASE = 'http://localhost:5000';
const POLL_INTERVAL_MS = 500;
const NPC_RADIUS = 10;

// Canvas
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// HUD Elements
const engineJsonEl = document.getElementById('engine-json');
const bannerTextEl = document.getElementById('banner-text');
const bannerSubEl = document.getElementById('banner-sub');
const hudMoodEl = document.getElementById('hud-mood');
const hudFitnessEl = document.getElementById('hud-fitness');
const hudNicheEl = document.getElementById('hud-niche');
const hudGenEl = document.getElementById('hud-gen');
const hudDiscEl = document.getElementById('hud-disc');
const hudOpsEl = document.getElementById('hud-ops');
const hudPlanckEl = document.getElementById('hud-planck');
const playerStatusEl = document.getElementById('player-status');
const npcListEl = document.getElementById('npc-list');
const msgPanelEl = document.getElementById('msg-panel');
const storyFeedEl = document.getElementById('story-feed');
const fieldToggleBtn = document.getElementById('field-toggle');
const infoToggleBtn = document.getElementById('info-toggle');
const infoSection = document.getElementById('info-section');
const fieldLegend = document.getElementById('field-legend');

// Game state
let currentState = null;
let showFields = false;
let playerState = {
  x: 0.5,
  y: 0.5,
  armed: false,
  gift_active: false,
  kills: 0
};

// Resize canvas
function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Toggle buttons
fieldToggleBtn.addEventListener('click', () => {
  showFields = !showFields;
  fieldToggleBtn.style.background = showFields ? '#4bff7a' : '';
  fieldToggleBtn.style.color = showFields ? '#050814' : '';
  fieldLegend.style.display = showFields ? 'block' : 'none';
});

infoToggleBtn.addEventListener('click', () => {
  infoSection.style.display = infoSection.style.display === 'none' ? 'block' : 'none';
  infoToggleBtn.style.background = infoSection.style.display === 'none' ? '' : 'rgba(0,255,136,0.2)';
});

/**
 * Fetch current game state from engine
 */
async function fetchGameState() {
  try {
    const res = await fetch(`${API_BASE}/api/game/state`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    currentState = await res.json();
    
    render();
    updateHud();
  } catch (err) {
    console.error('Game state error:', err);
    ctx.fillStyle = '#ff4b4b';
    ctx.font = '14px monospace';
    ctx.fillText('ERROR: Engine offline', 20, 20);
  }
}

/**
 * Draw field heatmaps
 */
function drawFields() {
  if (!currentState) return;
  
  const threat = currentState.npcs?.A1?.threat || 0;
  const intensity = currentState.intensity || 0.5;
  
  // Threat field (red gradient)
  ctx.fillStyle = `rgba(255, 75, 75, ${threat * 0.15})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Calm field (green gradient)
  const calmField = 1 - (threat + intensity) / 2;
  ctx.fillStyle = `rgba(75, 255, 122, ${calmField * 0.1})`;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

/**
 * Render arena with NPCs
 */
function render() {
  if (!currentState) return;

  // Clear
  ctx.fillStyle = '#0a0e1a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Fields (if enabled)
  if (showFields) {
    drawFields();
  }

  // Grid background
  ctx.strokeStyle = '#1f2336';
  ctx.lineWidth = 0.5;
  const gridSize = 40;
  for (let x = 0; x < canvas.width; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }

  // NPCs
  const npcs = currentState.npcs || {};
  const npcIds = Object.keys(npcs);

  npcIds.forEach((npcId, idx) => {
    const npc = npcs[npcId];
    
    // Spread NPCs around arena
    const angle = (idx / npcIds.length) * Math.PI * 2;
    const radius = Math.min(canvas.width, canvas.height) / 3;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;

    // Color by intent
    const color = intentColor(npc.intent);
    
    // NPC circle
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, NPC_RADIUS, 0, Math.PI * 2);
    ctx.fill();

    // Highlight if leader
    if (npc.is_leader) {
      ctx.strokeStyle = '#ffd54b';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(x, y, NPC_RADIUS + 4, 0, Math.PI * 2);
      ctx.stroke();
    }

    // NPC ID
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(npcId, x, y);

    // Coalition circle
    const coalColor = coalitionColor(npc.coalition);
    ctx.strokeStyle = coalColor;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.arc(x, y, NPC_RADIUS + 8, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1.0;

    // Emotion indicator
    const emotionY = y + NPC_RADIUS + 14;
    drawEmotionBar(x, emotionY, npc);
  });

  // Player
  ctx.fillStyle = '#00ff88';
  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, NPC_RADIUS + 5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 11px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('YOU', canvas.width / 2, canvas.height / 2);

  // Player armed indicator
  if (playerState.armed) {
    ctx.strokeStyle = '#ff4b4b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(canvas.width / 2, canvas.height / 2, NPC_RADIUS + 10, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Gift indicator
  if (playerState.gift_active) {
    ctx.fillStyle = '#ffd54b';
    ctx.beginPath();
    ctx.arc(canvas.width / 2 - 18, canvas.height / 2 - 18, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#0a0e1a';
    ctx.font = '12px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('♥', canvas.width / 2 - 18, canvas.height / 2 - 18);
  }
}

/**
 * Draw emotion bar under NPC
 */
function drawEmotionBar(x, y, npc) {
  const barWidth = 20;
  const barHeight = 2;

  ctx.fillStyle = '#ff4b4b';
  ctx.fillRect(x - barWidth/2, y, (npc.fear || 0) * barWidth, barHeight);

  if (npc.trust > 0) {
    ctx.fillStyle = '#4bff7a';
    ctx.fillRect(x - barWidth/2 + (npc.fear || 0) * barWidth, y, npc.trust * barWidth, barHeight);
  }

  ctx.fillStyle = '#ff7a4b';
  ctx.fillRect(x - barWidth/2, y + 3, (npc.anger || 0) * barWidth, barHeight);
}

/**
 * Intent → color
 */
function intentColor(intent) {
  switch (intent) {
    case 'attack':  return '#ff4b4b';
    case 'flee':    return '#4b9dff';
    case 'guard':   return '#7a4bff';
    case 'orbit':   return '#4bfff0';
    case 'scatter': return '#ff7a4b';
    case 'curious': return '#ffd54b';
    case 'idle':    return '#9ca0b8';
    default:        return '#b0b3c0';
  }
}

/**
 * Coalition → color
 */
function coalitionColor(coalition) {
  switch (coalition) {
    case 'red':     return '#ff4b4b';
    case 'green':   return '#4bff7a';
    case 'blue':    return '#4b9dff';
    case 'neutral': return '#9ca0b8';
    default:        return '#9ca0b8';
  }
}

/**
 * Update HUD panels
 */
function updateHud() {
  if (!currentState) return;

  // Engine JSON
  engineJsonEl.textContent = JSON.stringify(currentState, null, 2).substring(0, 400);

  // Mood banner
  const mood = currentState.mood || 'neutral';
  bannerTextEl.textContent = mood.toUpperCase();
  bannerSubEl.textContent = `intensity: ${(currentState.intensity || 0).toFixed(1)}`;

  // Status
  hudMoodEl.textContent = mood.toUpperCase();
  hudFitnessEl.textContent = (currentState.fitness || 0).toFixed(1);
  hudNicheEl.textContent = currentState.niche || '–';
  hudGenEl.textContent = currentState.generation || '–';
  hudDiscEl.textContent = currentState.discoveries || '–';
  hudOpsEl.textContent = (currentState.operators || []).join(', ') || '–';
  hudPlanckEl.textContent = currentState.planck ? 'YES' : 'NO';

  // Player
  playerStatusEl.innerHTML = `
    <div class="value">Armed: ${playerState.armed ? 'YES' : 'NO'}</div>
    <div class="value">Gift: ${playerState.gift_active ? 'YES' : 'NO'}</div>
    <div class="value">Kills: ${playerState.kills}</div>
  `;

  // NPC list
  const npcs = currentState.npcs || {};
  npcListEl.innerHTML = Object.entries(npcs).map(([id, npc]) => `
    <div class="npc-item">
      <strong>${id}</strong>
      <div class="intent">${npc.intent || '–'}</div>
      <div class="intent">[${npc.coalition || 'neutral'}]</div>
    </div>
  `).join('');

  // Messages
  const messages = currentState.messages || [];
  msgPanelEl.innerHTML = messages.slice(-8).map(msg => `
    <div class="msg-item">
      <span class="msg-from">${msg.from}</span> → ${msg.to}
      <div class="msg-content">${msg.content}</div>
    </div>
  `).join('') || '<div class="msg-item" style="color: var(--text-dim); font-size: 0.7rem;">No messages</div>';

  // Narrative events
  const narrative = currentState.narrative || [];
  storyFeedEl.innerHTML = narrative.slice(-6).map(ev => `
    <div class="story-item">
      <span class="story-name">${ev.name || 'Event'}</span>
      <div class="story-desc">${ev.desc || ev.type}</div>
    </div>
  `).join('') || '<div class="story-item" style="color: var(--text-dim); font-size: 0.7rem;">Waiting for events...</div>';
}

/**
 * Send player state to engine
 */
async function sendPlayerState() {
  try {
    await fetch(`${API_BASE}/api/arena/player`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(playerState)
    });
  } catch (err) {
    console.error('Player update error:', err);
  }
}

/**
 * Keyboard controls
 */
window.addEventListener('keydown', (e) => {
  const key = e.key.toLowerCase();

  if (key === 'w') playerState.y = Math.max(0, playerState.y - 0.05);
  if (key === 's') playerState.y = Math.min(1, playerState.y + 0.05);
  if (key === 'a') playerState.x = Math.max(0, playerState.x - 0.05);
  if (key === 'd') playerState.x = Math.min(1, playerState.x + 0.05);

  if (key === ' ' || key === 'spacebar') {
    e.preventDefault();
    playerState.armed = !playerState.armed;
  }

  if (key === 'g') {
    playerState.gift_active = !playerState.gift_active;
  }

  if (key === 'f') {
    fieldToggleBtn.click();
  }

  if (key === '?') {
    infoToggleBtn.click();
  }

  sendPlayerState();
});

/**
 * Main loop
 */
setInterval(fetchGameState, POLL_INTERVAL_MS);

console.log('[Observatory] Connecting to Chronos engine at', API_BASE);
fetchGameState();
