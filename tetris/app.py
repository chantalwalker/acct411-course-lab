"""TETRIS — a commented, self-contained Streamlit falling-block game.

Run: streamlit run app.py
Python hosts the page; JavaScript runs the fast animation in your browser.
No images, API keys, game servers, or extra frontend installations are needed.
"""
import streamlit as st
import streamlit.components.v1 as components

# Wide layout gives our game room on both laptops and phones.
st.set_page_config(page_title="TETRIS", page_icon="🧩", layout="wide")

# A raw Python string preserves JavaScript backslashes exactly as written.
# HTML = page structure, CSS = appearance, JavaScript = game rules and input.
GAME_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
/* Theme variables are updated by applyTheme(); the layout stays the same. */
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);transition:background .35s;color-scheme:dark}
.shell{max-width:1000px;margin:auto;padding:24px;border-radius:24px;background:var(--scene);min-height:850px}
header{display:flex;justify-content:space-between;gap:20px;align-items:center}h1{font-size:38px;margin:3px 0;letter-spacing:-1px}p{line-height:1.5}.eyebrow{font:12px monospace;letter-spacing:3px;color:var(--accent)}
.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:20px 0}select,button{font:inherit;color:var(--text);background:var(--panel);border:1px solid var(--accent);border-radius:10px;padding:10px;cursor:pointer}button:hover{filter:brightness(1.3);box-shadow:0 0 14px var(--accent)}button:focus-visible,select:focus-visible,canvas:focus-visible{outline:3px solid var(--accent);outline-offset:3px}label{font-size:13px}label select{margin-left:8px}
.layout{display:grid;grid-template-columns:minmax(120px,1fr) minmax(220px,300px) minmax(120px,1fr);gap:18px;align-items:start}.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}.caption{font-size:11px;letter-spacing:2px;text-transform:uppercase;opacity:.8}.number{font-size:30px;font-weight:bold;margin-top:6px}.board-wrap{position:relative}#board{width:100%;display:block;border:2px solid var(--accent);border-radius:8px;touch-action:none;box-shadow:0 10px 35px #0005}canvas.preview{width:100%;max-width:130px;display:block;margin:auto}.overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;background:#08101bd9;border-radius:8px;color:white;padding:20px;pointer-events:none}.overlay h2{font-size:28px}.hidden{display:none}.controls{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:18px}.controls button{min-width:46px;touch-action:manipulation}.hint{font-size:12px;opacity:.85}#message{min-height:24px;color:var(--accent);font-weight:bold}.keys{font-size:13px;line-height:1.9}.foot{font-size:12px;opacity:.7;margin-top:20px}input{accent-color:var(--accent)}
@media(max-width:650px){.shell{padding:12px}h1{font-size:28px}.layout{grid-template-columns:minmax(190px,300px) minmax(85px,1fr);gap:10px}.left{grid-column:2;grid-row:1}.board-wrap{grid-column:1;grid-row:1}.right{grid-column:1 / -1;display:flex;gap:10px;flex-wrap:wrap}.right .card{flex:1}.card{padding:10px}.keys{display:none}.number{font-size:23px}header .hint{display:none}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body><div class="shell">
<header><div><div class="eyebrow">EIGHT WORLDS · ONE MORE ROUND</div><h1>TETRIS <span id="motif">✦</span></h1></div><div class="hint">A Tetris-style escape<br>Made for your next little break.</div></header>
<div class="toolbar">
<label>World <select id="theme" aria-label="Choose theme"></select></label>
<button id="start">Start game</button><button id="pause">Pause</button>
<label><input type="checkbox" id="sound"> Sound</label>
<label><input type="checkbox" id="effects" checked> Effects</label>
</div>
<div id="message" role="status" aria-live="polite">Choose your world. Find your flow.</div>
<div class="layout">
<aside class="left"><div class="card"><div class="caption">Score</div><div class="number" id="score">0</div><hr><div class="caption">Level / Lines</div><div class="number"><span id="level">1</span> / <span id="lines">0</span></div></div><div class="card"><div class="caption">Hold · C</div><canvas class="preview" id="hold" width="130" height="100" aria-label="Held piece"></canvas></div><div class="card"><div class="caption">Best on this browser</div><div class="number" id="best">0</div></div></aside>
<div class="board-wrap"><canvas id="board" width="300" height="600" tabindex="0" aria-label="Tetris game board. Arrow keys move, up rotates, space drops."></canvas><div id="overlay" class="overlay"><div><h2>Your next escape.</h2><p>Press Start game<br>then use the arrow keys.</p></div></div></div>
<aside class="right"><div class="card"><div class="caption">Coming next</div><canvas class="preview" id="next" width="130" height="300" aria-label="Next three pieces"></canvas></div><div class="card keys"><strong>How to play</strong><br>← → / A D · Move<br>↓ / S · Soft drop<br>↑ / W / X · Rotate<br>Z · Rotate back<br>Space · Hard drop<br>C / Shift · Hold<br>P / Esc · Pause<br><br>Complete rows to clear them.<br>Every 10 lines = faster play.</div></aside>
</div>
<div class="controls" aria-label="Touch controls"><button data-action="left" aria-label="Move left">←</button><button data-action="rotateBack" aria-label="Rotate left">↶</button><button data-action="rotate" aria-label="Rotate right">↷</button><button data-action="right" aria-label="Move right">→</button><button data-action="down">↓ Soft</button><button data-action="drop">⤓ Drop</button><button data-action="hold">Hold</button></div>
<p class="hint">Click the board if keys stop responding. A faint outline shows where your piece will land. Sound starts only after you enable it.</p>
<div class="foot">Theme changes preserve your game. Refreshing starts a new session. Unofficial learning project; simplified rotation and scoring.</div>
</div>
<script>
'use strict';
// =====================================================================
// 1. THEMES: edit these records to create your own world.
// palette order always matches I, J, L, O, S, T, Z. The rules never change.
// style controls block texture; glyph controls particles; wave/base sound.
// =====================================================================
const THEMES = {
 'Y2K':{bg:'#211332',panel:'#39224c',text:'#fff0ff',accent:'#ff9fe5',line:'#80558e',font:'Verdana, sans-serif',scene:'radial-gradient(ellipse at top right,#8856a8,transparent 65%),linear-gradient(140deg,#23102f,#40254d)',palette:['#a6ecff','#b0a0ff','#ffb4ea','#e5f5a1','#a5edcf','#df9bfa','#ff93b5'],style:'gloss',glyph:'✦',wave:'sine',base:660,cheer:'That’s hot!'},
 'Cottagecore':{bg:'#e9e3cf',panel:'#faf4e3',text:'#374a35',accent:'#8c4d3d',line:'#b0b894',font:'Georgia, serif',scene:'repeating-linear-gradient(0deg,#a2b58a15 0 20px,transparent 20px 40px),linear-gradient(120deg,#f7efdd,#dbe4c5)',palette:['#77a9a0','#7e91b0','#c99465','#d6bd6b','#8fa66c','#b28da8','#c67c76'],style:'leaf',glyph:'❀',wave:'sine',base:440,cheer:'A lovely little harvest!'},
 'Ocean':{bg:'#042638',panel:'#073c50',text:'#e0fbff',accent:'#67e8d0',line:'#27667b',font:'Trebuchet MS, sans-serif',scene:'radial-gradient(ellipse at top,#168598,transparent 65%),linear-gradient(#06354e,#031828)',palette:['#5be0ed','#5d9edc','#f2a674','#f3db85','#66d7b4','#a59cdd','#ec91ad'],style:'bubble',glyph:'○',wave:'sine',base:330,cheer:'Making waves!'},
 'Cyberpunk':{bg:'#100b25',panel:'#201533',text:'#f1eaff',accent:'#00f5d4',line:'#6d2e82',font:'Courier New, monospace',scene:'repeating-linear-gradient(0deg,transparent 0 5px,#c42fff10 5px 6px),linear-gradient(130deg,#240d39,#070d1c)',palette:['#00e5ff','#5977ff','#ff913b','#faff34','#00e6a4','#d451ff','#ff387c'],style:'neon',glyph:'+',wave:'sawtooth',base:220,cheer:'System upgraded.'},
 'Cosmic':{bg:'#0c102d',panel:'#1c2344',text:'#eef0ff',accent:'#bcacff',line:'#454c80',font:'Trebuchet MS, sans-serif',scene:'radial-gradient(ellipse at 20% 10%,#542a76,transparent 55%),linear-gradient(#111734,#070b1e)',palette:['#89d7ff','#859eff','#ffb38c','#ffe69b','#97e0d0','#b59bfa','#ef99c0'],style:'star',glyph:'✧',wave:'triangle',base:523,cheer:'Stellar alignment!'},
 'Candyland':{bg:'#ffe5ee',panel:'#fff5f8',text:'#68354f',accent:'#bd3c79',line:'#edb6cb',font:'Verdana, sans-serif',scene:'repeating-linear-gradient(135deg,#ffffff40 0 25px,transparent 25px 50px),linear-gradient(100deg,#ffdfeb,#e2dcff)',palette:['#75cdd4','#90a9ed','#f3af7d','#e1c76d','#94c799','#bf9bde','#ee8eb0'],style:'stripe',glyph:'♥',wave:'triangle',base:784,cheer:'Sweet combo!'},
 'Autumn':{bg:'#30211c',panel:'#493126',text:'#ffedd5',accent:'#f7b267',line:'#79523c',font:'Georgia, serif',scene:'radial-gradient(ellipse at top right,#855126,transparent 65%),linear-gradient(#39271d,#231b18)',palette:['#72a8a0','#8597ab','#d98147','#dbb75b','#a5af69','#b28b9a','#c97561'],style:'leaf',glyph:'❧',wave:'sine',base:294,cheer:'Golden hour!'},
 'Arcade':{bg:'#0c1714',panel:'#152a22',text:'#e2ffe9',accent:'#9bff9a',line:'#3b604d',font:'Courier New, monospace',scene:'repeating-linear-gradient(0deg,#0002 0 2px,transparent 2px 4px),linear-gradient(#13271e,#080f0d)',palette:['#52d9db','#657de5','#ef9d50','#e2d85b','#65cc74','#b079d7','#e57373'],style:'pixel',glyph:'▪',wave:'square',base:440,cheer:'HIGH FIVE, PLAYER ONE!'}
};
const $ = id => document.getElementById(id); // Short DOM lookup helper.
const canvas=$('board'), ctx=canvas.getContext('2d');
const COLS=10, ROWS=20, CELL=30;
let theme=THEMES.Y2K;
for(const name of Object.keys(THEMES)) $('theme').add(new Option(name,name));
function applyTheme(){
 theme=THEMES[$('theme').value];
 for(const key of ['bg','panel','text','accent','line','font','scene']) document.body.style.setProperty('--'+key,theme[key]);
 $('motif').textContent=theme.glyph;
 // Redrawing uses new colors for both existing and future blocks.
 draw(); previews();
}
// =====================================================================
// 2. STATE AND PIECES. A zero is empty; 1..7 identify a piece's color.
// Square matrices make clockwise / counterclockwise rotation simple.
// =====================================================================
const SHAPES=[
 [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
 [[2,0,0],[2,2,2],[0,0,0]], [[0,0,3],[3,3,3],[0,0,0]],
 [[4,4],[4,4]], [[0,5,5],[5,5,0],[0,0,0]],
 [[0,6,0],[6,6,6],[0,0,0]], [[7,7,0],[0,7,7],[0,0,0]]
];
const emptyBoard=()=>Array.from({length:ROWS},()=>Array(COLS).fill(0));
let board=emptyBoard(), active=null, queue=[], held=null, canHold=true;
let score=0, lines=0, level=1, best=0, running=false, paused=false, over=false;
let gravity=0, lockTime=0, lockResets=0, previous=0, particles=[];
// Storage is optional: privacy settings must not prevent the game loading.
try{best=Number(localStorage.getItem('theme-drop-best'))||0;}catch(e){}
$('best').textContent=best;
// A seven-bag randomizer supplies every shape once per shuffled bag.
function fillQueue(){
 if(queue.length>=7)return;
 const bag=[0,1,2,3,4,5,6];
 for(let i=bag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[bag[i],bag[j]]=[bag[j],bag[i]];}
 queue.push(...bag);
}
function spawn(type){
 fillQueue();
 const id=type===undefined?queue.shift():type;
 active={id,m:SHAPES[id].map(row=>row.slice()),x:Math.floor((COLS-SHAPES[id].length)/2),y:0};
 gravity=0;lockTime=0;lockResets=0;fillQueue();
 if(collides(active.m,active.x,active.y)) endGame();
 previews();
}
// Negative y is legal for rotations near the ceiling; side/floor collisions
// and occupied cells are not. Ignore the zero cells surrounding a shape.
function collides(matrix,x,y){
 return matrix.some((row,dy)=>row.some((v,dx)=>v && (x+dx<0 || x+dx>=COLS || y+dy>=ROWS || (y+dy>=0 && board[y+dy][x+dx]))));
}
function updateStats(){
 level=1+Math.floor(lines/10);
 if(score>best){best=score;try{localStorage.setItem('theme-drop-best',String(best));}catch(e){}}
 for(const [id,value] of Object.entries({score,lines,level,best})) $(id).textContent=value;
}
function overlay(title,body){$('overlay').innerHTML='<div><h2>'+title+'</h2><p>'+body+'</p></div>';$('overlay').classList.remove('hidden');}
function start(){
 if(running && !over && !confirm('Start a new game? Your current run will end.'))return;
 board=emptyBoard();queue=[];held=null;score=0;lines=0;particles=[];canHold=true;
 running=true;paused=false;over=false;updateStats();spawn();
 $('overlay').classList.add('hidden');$('start').textContent='New game';$('pause').textContent='Pause';
 $('message').textContent='A fresh start. You’ve got this.';canvas.focus();
}
function endGame(){running=false;over=true;updateStats();overlay('A lovely run.', 'Score: '+score+'<br>Press New game to try again.');tone(110,.25);}
function togglePause(){
 if(!running)return;paused=!paused;
 $('pause').textContent=paused?'Resume':'Pause';
 if(paused)overlay('Take a breath.', 'Press P or Resume to continue.');else $('overlay').classList.add('hidden');
 canvas.focus();
}
// =====================================================================
// 3. MOVEMENT, ROTATION, HOLD, AND LOCKING.
// 500 ms lock delay gives you time to slide after touching the floor.
// At most 15 successful grounded moves can reset this delay per piece.
// =====================================================================
function resetLock(){if(lockResets<15){lockTime=0;lockResets++;}}
function move(dx,dy){
 if(collides(active.m,active.x+dx,active.y+dy))return false;
 const grounded=collides(active.m,active.x,active.y+1);
 active.x+=dx;active.y+=dy;
 if(grounded && dx)resetLock();
 return true;
}
function rotate(direction){
 if(active.id===3)return; // O already occupies the same square.
 const old=active.m, n=old.length;
 const rotated=Array.from({length:n},(_,y)=>Array.from({length:n},(_,x)=>direction===1?old[n-1-x][y]:old[x][n-1-y]));
 // Simple wall/floor kicks, intentionally easier to read than official SRS.
 const grounded=collides(active.m,active.x,active.y+1);
 for(const [dx,dy] of [[0,0],[-1,0],[1,0],[-2,0],[2,0],[0,-1],[0,-2]]){
  if(!collides(rotated,active.x+dx,active.y+dy)){
   active.m=rotated;active.x+=dx;active.y+=dy;if(grounded)resetLock();tone(theme.base,.035);return;
  }
 }
}
function hold(){
 if(!canHold)return;
 const old=held;held=active.id;spawn(old===null?undefined:old);canHold=false;previews();tone(theme.base*.75,.06);
}
function lock(){
 // A piece that locks above the visible board ends the game safely.
 if(active.m.some((row,y)=>row.some(v=>v && active.y+y<0))){endGame();return;}
 active.m.forEach((row,y)=>row.forEach((v,x)=>{if(v)board[active.y+y][active.x+x]=v;}));
 const full=[];
 board.forEach((row,y)=>{if(row.every(Boolean))full.push(y);});
 if(full.length){
  full.forEach(y=>burst(y));
  board=board.filter((_,y)=>!full.includes(y));
  while(board.length<ROWS)board.unshift(Array(COLS).fill(0));
  // Classic-style line points. Drop points are handled separately below.
  score+=[0,100,300,500,800][full.length]*level;lines+=full.length;
  $('message').textContent=theme.cheer+' +'+full.length+' line'+(full.length>1?'s':'');
  tone(theme.base*1.5,.18);
 }else tone(theme.base*.5,.045);
 updateStats();canHold=true;spawn();
}
function act(action){
 if(!running||paused||over)return;
 if(action==='left')move(-1,0);
 if(action==='right')move(1,0);
 if(action==='down' && move(0,1)){score++;gravity=0;updateStats();}
 if(action==='rotate')rotate(1);
 if(action==='rotateBack')rotate(-1);
 if(action==='hold')hold();
 if(action==='drop'){while(move(0,1))score+=2;lock();}
 draw();
}
// =====================================================================
// 4. DRAWING. Canvas coordinates are pixels; board coordinates are cells.
// The same block painter draws the board, held piece, and next previews.
// =====================================================================
function block(c,x,y,size,value,ghost=false){
 const color=theme.palette[value-1];c.save();
 if(ghost){c.strokeStyle=color;c.globalAlpha=.65;c.lineWidth=2;c.strokeRect(x+3,y+3,size-6,size-6);c.restore();return;}
 c.fillStyle=color;
 if(theme.style==='neon'){c.shadowColor=color;c.shadowBlur=8;}
 c.fillRect(x+1,y+1,size-2,size-2);c.shadowBlur=0;
 c.fillStyle='#ffffff45';c.fillRect(x+3,y+3,size-6,3);
 c.fillStyle='#00000028';c.fillRect(x+3,y+size-6,size-6,3);
 c.strokeStyle='#ffffff75';c.lineWidth=1;
 if(theme.style==='bubble'){c.beginPath();c.arc(x+size/2,y+size/2,size*.23,0,Math.PI*2);c.stroke();}
 if(theme.style==='gloss'){c.fillStyle='#ffffff50';c.fillRect(x+3,y+3,size-6,size*.35);}
 if(theme.style==='stripe'){c.beginPath();c.moveTo(x+3,y+size*.65);c.lineTo(x+size*.65,y+3);c.stroke();}
 if(theme.style==='pixel'){c.strokeRect(x+5,y+5,size-10,size-10);}
 if(theme.style==='leaf'||theme.style==='star'){
  c.fillStyle='#ffffffa0';c.font=(size*.55)+'px Georgia';c.textAlign='center';c.fillText(theme.style==='leaf'?'❧':'✦',x+size/2,y+size*.7);
 }
 c.restore();
}
function paintPiece(c,p,size,ghost=false){p.m.forEach((row,y)=>row.forEach((v,x)=>{if(v)block(c,(p.x+x)*size,(p.y+y)*size,size,v,ghost);}));}
function draw(){
 ctx.fillStyle=theme.bg;ctx.fillRect(0,0,300,600);
 // Subtle themed decorations keep empty space from feeling flat.
 ctx.save();ctx.globalAlpha=.12;ctx.fillStyle=theme.accent;ctx.font='24px serif';
 for(let i=0;i<12;i++)ctx.fillText(theme.glyph,(i*73)%280+5,(i*137)%570+25);ctx.restore();
 ctx.strokeStyle=theme.line;ctx.globalAlpha=.3;ctx.lineWidth=.5;
 for(let x=0;x<=COLS;x++){ctx.beginPath();ctx.moveTo(x*CELL,0);ctx.lineTo(x*CELL,600);ctx.stroke();}
 for(let y=0;y<=ROWS;y++){ctx.beginPath();ctx.moveTo(0,y*CELL);ctx.lineTo(300,y*CELL);ctx.stroke();}ctx.globalAlpha=1;
 board.forEach((row,y)=>row.forEach((v,x)=>{if(v)block(ctx,x*CELL,y*CELL,CELL,v);}));
 if(active && !over){
  let landing=active.y;while(!collides(active.m,active.x,landing+1))landing++;
  paintPiece(ctx,{...active,y:landing},CELL,true);paintPiece(ctx,active,CELL);
 }
 for(const p of particles){ctx.save();ctx.globalAlpha=Math.max(0,p.life);ctx.fillStyle=p.color;ctx.font='20px serif';ctx.fillText(theme.glyph,p.x,p.y);ctx.restore();}
}
function previews(){
 for(const [id,items] of [['hold',held===null?[]:[held]],['next',queue.slice(0,3)]]){
  const c=$(id).getContext('2d');c.clearRect(0,0,c.canvas.width,c.canvas.height);
  items.forEach((type,index)=>{
   const m=SHAPES[type],size=23;
   // Find the occupied bounds, so I and O are visually centered too.
   const cells=[];m.forEach((row,y)=>row.forEach((v,x)=>{if(v)cells.push([x,y,v]);}));
   const minX=Math.min(...cells.map(a=>a[0])),maxX=Math.max(...cells.map(a=>a[0]));
   const minY=Math.min(...cells.map(a=>a[1])),maxY=Math.max(...cells.map(a=>a[1]));
   const ox=(130-(maxX-minX+1)*size)/2,oy=index*100+(100-(maxY-minY+1)*size)/2;
   cells.forEach(([x,y,v])=>block(c,ox+(x-minX)*size,oy+(y-minY)*size,size,v));
  });
 }
}
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
$('effects').checked=!reducedMotion;
function burst(row){
 if(!$('effects').checked)return;
 for(let i=0;i<24;i++)particles.push({x:Math.random()*300,y:row*CELL+15,vx:(Math.random()-.5)*120,vy:-40-Math.random()*120,life:1,color:theme.palette[i%7]});
}
// =====================================================================
// 5. SOUND. Browser-generated notes avoid downloading any audio files.
// It stays OFF by default and is created only after a user's interaction.
// =====================================================================
let audio=null;
function tone(frequency,duration){
 if(!$('sound').checked)return;
 try{
  audio=audio||new (window.AudioContext||window.webkitAudioContext)();audio.resume();
  const oscillator=audio.createOscillator(),gain=audio.createGain();
  oscillator.type=theme.wave;oscillator.frequency.value=frequency;
  gain.gain.setValueAtTime(.035,audio.currentTime);
  gain.gain.exponentialRampToValueAtTime(.001,audio.currentTime+duration);
  oscillator.connect(gain);gain.connect(audio.destination);oscillator.start();oscillator.stop(audio.currentTime+duration);
 }catch(e){/* Unsupported audio should never stop gameplay. */}
}
// =====================================================================
// 6. INPUT. Keyboard events stay inside this iframe, not Streamlit itself.
// Default page scrolling is suppressed only for our game keys.
// =====================================================================
const mapping={ArrowLeft:'left',a:'left',ArrowRight:'right',d:'right',ArrowDown:'down',s:'down',ArrowUp:'rotate',w:'rotate',x:'rotate',z:'rotateBack',' ':'drop',c:'hold',Shift:'hold'};
document.addEventListener('keydown',e=>{
 if(['SELECT','INPUT','BUTTON'].includes(e.target.tagName))return;
 const key=e.key.length===1?e.key.toLowerCase():e.key;
 if(key==='p'||key==='Escape'){e.preventDefault();if(!e.repeat)togglePause();return;}
 const action=mapping[key];if(!action)return;e.preventDefault();
 // Holding Space must not accidentally hard-drop multiple new pieces.
 if(e.repeat && !['left','right','down'].includes(action))return;
 act(action);
});
document.querySelectorAll('[data-action]').forEach(button=>button.addEventListener('click',()=>{act(button.dataset.action);canvas.focus();}));
$('start').onclick=start;$('pause').onclick=togglePause;
$('theme').onchange=()=>{applyTheme();canvas.focus();};
$('sound').onchange=()=>{tone(theme.base,.1);canvas.focus();};
$('effects').onchange=()=>{particles=[];canvas.focus();};
// Losing focus pauses the game, so an accidental click outside won't cost it.
window.addEventListener('blur',()=>{if(running&&!paused)togglePause();});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&running&&!paused)togglePause();});
// =====================================================================
// 7. ANIMATION LOOP. requestAnimationFrame follows the display refresh rate.
// Delta time is milliseconds since the previous frame, capped after stalls.
// Gravity accelerates by level, down to a minimum 80 ms per row.
// =====================================================================
function frame(now){
 const dt=Math.min(now-previous,50);previous=now;
 if(running&&!paused){
  gravity+=dt;const interval=Math.max(80,850*Math.pow(.8,level-1));
  if(gravity>=interval){move(0,1);gravity=0;}
  if(collides(active.m,active.x,active.y+1)){lockTime+=dt;if(lockTime>=500)lock();}else lockTime=0;
  particles.forEach(p=>{p.life-=dt/850;p.x+=p.vx*dt/1000;p.y+=p.vy*dt/1000;p.vy+=100*dt/1000;});
  particles=particles.filter(p=>p.life>0);
 }
 draw();requestAnimationFrame(frame);
}
applyTheme();requestAnimationFrame(frame);
</script></body></html>"""

# Current Streamlit supports st.iframe; older versions use components.html.
# Both execute the JavaScript inside an isolated embedded page.
# Keeping all game controls inside that page avoids Streamlit rerun resets.
if hasattr(st, "iframe"):
    st.iframe(GAME_HTML, height=1100)
else:
    components.html(GAME_HTML, height=1100, scrolling=True)
