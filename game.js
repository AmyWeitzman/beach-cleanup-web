const W = 800;
const H = 600;
const COLLISION_DELTA = 30;
const FRAME_MS = 1000 / 30; // speeds are in px/frame at 30fps; scale by delta

const OBSTACLE_KEYS = ['crab', 'seagull', 'seaweed'];
const TRASH_KEYS    = ['can', 'cigarette', 'paper_wad', 'water_bottle'];
const BOOST_KEYS    = ['seashell1', 'seashell2', 'seashell3'];

function rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function hit(x, y, r) {
  return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h;
}

class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');

    this.images = {};
    this.sounds = {};
    this.keys   = {};
    this.mouse  = { x: 0, y: 0 };

    this.state      = 'loading';
    this.playMusic  = true;
    this.playSounds = true;

    this.player    = null;
    this.obstacles = [];
    this.trash     = [];
    this.boosts    = [];
    this.score     = 0;
    this.startTime = 0;
    this.elapsed   = 0;

    this.nextObstacleAt = 0;
    this.nextTrashAt    = 0;
    this.nextBoostAt    = 0;

    this.lastTime = 0;

    const cx = W / 2;
    this.ui = {
      musicToggle: { x: cx - 175, y: H / 2 - 10,  w: 370, h: 35,  label: 'Background Music', value: true  },
      soundToggle: { x: cx - 175, y: H / 2 + 50,  w: 370, h: 35,  label: 'Sound Effects',    value: true  },
      play:        { x: cx - 80,  y: H / 2 + 120, w: 160, h: 48,  label: 'Play'                           },
      playAgain:   { x: cx - 100, y: H / 2 + 120, w: 200, h: 48,  label: 'Play Again'                     },
    };

    this._setupListeners();
    this._loadAssets().then(() => {
      this.state = 'settings';
      requestAnimationFrame(t => this._loop(t));
    });
  }

  // ── Asset loading ─────────────────────────────────────────────────

  async _loadAssets() {
    const imgMap = {
      player:       'imgs/players/stick_figure.png',
      bg:           'imgs/sand_bg.jpg',
      logo:         'imgs/logo.png',
      crab:         'imgs/obstacles/crab.png',
      seagull:      'imgs/obstacles/seagull.png',
      seaweed:      'imgs/obstacles/seaweed.png',
      can:          'imgs/trash/can.png',
      cigarette:    'imgs/trash/cigarette.png',
      paper_wad:    'imgs/trash/paper_wad.png',
      water_bottle: 'imgs/trash/water_bottle.png',
      seashell1:    'imgs/boosts/seashell1.png',
      seashell2:    'imgs/boosts/seashell2.png',
      seashell3:    'imgs/boosts/seashell3.png',
    };

    await Promise.all(Object.entries(imgMap).map(([key, src]) =>
      new Promise(resolve => {
        const img = new Image();
        img.onload  = () => { this.images[key] = img; resolve(); };
        img.onerror = () => resolve(); // skip missing images gracefully
        img.src = src;
      })
    ));

    const audioMap = {
      waves:         { src: 'audio/waves.ogg',         loop: true,  volume: 1.0 },
      collect_trash: { src: 'audio/collect_trash.ogg', loop: false, volume: 0.8 },
      collect_boost: { src: 'audio/collect_boost.ogg', loop: false, volume: 0.8 },
      game_over:     { src: 'audio/game_over.ogg',     loop: false, volume: 0.2 },
    };

    for (const [key, { src, loop, volume }] of Object.entries(audioMap)) {
      const a = new Audio(src);
      a.loop   = loop;
      a.volume = volume;
      this.sounds[key] = a;
    }
  }

  // ── Input ─────────────────────────────────────────────────────────

  _setupListeners() {
    document.addEventListener('keydown', e => {
      this.keys[e.key] = true;
      if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) {
        e.preventDefault();
      }
    });
    document.addEventListener('keyup', e => { this.keys[e.key] = false; });

    this.canvas.addEventListener('mousemove', e => {
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = (e.clientX - r.left) * (W / r.width);
      this.mouse.y = (e.clientY - r.top)  * (H / r.height);
    });

    this.canvas.addEventListener('click', e => {
      const r = this.canvas.getBoundingClientRect();
      const x = (e.clientX - r.left) * (W / r.width);
      const y = (e.clientY - r.top)  * (H / r.height);
      this._handleClick(x, y);
    });
  }

  _handleClick(x, y) {
    if (this.state === 'settings') {
      const { musicToggle, soundToggle, play } = this.ui;
      if (hit(x, y, musicToggle)) { musicToggle.value = !musicToggle.value; this.playMusic  = musicToggle.value; }
      if (hit(x, y, soundToggle)) { soundToggle.value = !soundToggle.value; this.playSounds = soundToggle.value; }
      if (hit(x, y, play))        this._startGame();
    } else if (this.state === 'gameover') {
      if (hit(x, y, this.ui.playAgain)) {
        this._stopMusic();
        this.state = 'settings';
      }
    }
  }

  // ── Game lifecycle ────────────────────────────────────────────────

  _startGame() {
    this.score     = 0;
    this.startTime = performance.now();
    this.elapsed   = 0;
    this.obstacles = [];
    this.trash     = [];
    this.boosts    = [];

    const pw = W / 8, ph = H / 4;
    this.player = { img: 'player', x: 0, y: H / 2 - ph / 2, w: pw, h: ph };

    const now = performance.now();
    this.nextObstacleAt = now + rand(1000, 3000);
    this.nextTrashAt    = now + rand(1000, 3000);
    this.nextBoostAt    = now + rand(5000, 10000);

    if (this.playMusic) this._playMusic();
    this.state = 'playing';
  }

  _spawnObstacle() {
    const key = OBSTACLE_KEYS[rand(0, OBSTACLE_KEYS.length - 1)];
    return { img: key, x: W + rand(20, 100), y: rand(0, H - H/8), w: W/9, h: H/8, speed: rand(4, 10) };
  }

  _spawnTrash() {
    const key = TRASH_KEYS[rand(0, TRASH_KEYS.length - 1)];
    return { img: key, x: W + rand(20, 100), y: rand(0, H - H/10), w: W/10, h: H/10, speed: rand(4, 8) };
  }

  _spawnBoost() {
    const key = BOOST_KEYS[rand(0, BOOST_KEYS.length - 1)];
    return { img: key, x: W + rand(20, 100), y: rand(0, H - H/10), w: W/10, h: H/10, speed: 3 };
  }

  // ── Collision ─────────────────────────────────────────────────────

  _collides(a, b) {
    const xOverlap = (a.x + a.w) - b.x;
    if (xOverlap < COLLISION_DELTA) return false;

    const topOverlap = (a.y + a.h) - b.y;
    const botOverlap = (b.y + b.h) - a.y;
    const topOk = topOverlap >= COLLISION_DELTA && topOverlap <= a.h - COLLISION_DELTA;
    const botOk = botOverlap >= COLLISION_DELTA && botOverlap <= a.h - COLLISION_DELTA;
    return topOk || botOk;
  }

  // ── Update ────────────────────────────────────────────────────────

  _update(now, delta) {
    const scale = delta / FRAME_MS;
    const p = this.player;

    // Spawn
    if (now >= this.nextObstacleAt) { this.obstacles.push(this._spawnObstacle()); this.nextObstacleAt = now + rand(1000, 3000); }
    if (now >= this.nextTrashAt)    { this.trash.push(this._spawnTrash());         this.nextTrashAt    = now + rand(1000, 3000); }
    if (now >= this.nextBoostAt) {
      if (Math.random() < 0.3) this.boosts.push(this._spawnBoost());
      this.nextBoostAt = now + rand(5000, 10000);
    }

    // Player movement
    if (this.keys['ArrowUp'])    p.y -= 5 * scale;
    if (this.keys['ArrowDown'])  p.y += 5 * scale;
    if (this.keys['ArrowLeft'])  p.x -= 5 * scale;
    if (this.keys['ArrowRight']) p.x += 5 * scale;
    p.x = Math.max(0, Math.min(W - p.w, p.x));
    p.y = Math.max(0, Math.min(H - p.h, p.y));

    // Move sprites and cull off-screen
    for (const s of [...this.obstacles, ...this.trash, ...this.boosts]) s.x -= s.speed * scale;
    this.obstacles = this.obstacles.filter(s => s.x + s.w > 0);
    this.trash     = this.trash.filter(s => s.x + s.w > 0);
    this.boosts    = this.boosts.filter(s => s.x + s.w > 0);

    // Obstacle collision → game over
    for (const obs of this.obstacles) {
      if (this._collides(p, obs)) {
        this.elapsed = Math.floor((now - this.startTime) / 1000);
        if (this.playSounds) this._playSound('game_over');
        this._stopMusic();
        this.state = 'gameover';
        return;
      }
    }

    // Trash collection
    this.trash = this.trash.filter(t => {
      if (this._collides(p, t)) {
        this.score += 20;
        if (this.playSounds) this._playSound('collect_trash');
        return false;
      }
      return true;
    });

    // Boost collection
    this.boosts = this.boosts.filter(b => {
      if (this._collides(p, b)) {
        this.score += 100;
        if (this.playSounds) this._playSound('collect_boost');
        return false;
      }
      return true;
    });

    this.elapsed = Math.floor((now - this.startTime) / 1000);
  }

  // ── Draw ──────────────────────────────────────────────────────────

  _drawBtn(r, label, hoverColor = '#1e9fc7', baseColor = '#1a8db0') {
    const mx = this.mouse.x, my = this.mouse.y;
    const isHover = hit(mx, my, r);
    this.ctx.fillStyle = isHover ? hoverColor : baseColor;
    this.ctx.beginPath();
    this.ctx.roundRect(r.x, r.y, r.w, r.h, 8);
    this.ctx.fill();
    this.ctx.fillStyle = '#fff';
    this.ctx.font = '22px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(label, r.x + r.w / 2, r.y + r.h / 2);
  }

  _drawToggle(t) {
    const ctx = this.ctx;
    ctx.fillStyle = '#000';
    ctx.font = '22px Arial';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(t.label + ':', t.x, t.y + 17);

    const bx = t.x + 285, by = t.y, bw = 70, bh = 32;
    ctx.fillStyle = t.value ? '#32c864' : '#b43c3c';
    ctx.beginPath();
    ctx.roundRect(bx, by, bw, bh, 16);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.font = '17px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(t.value ? 'ON' : 'OFF', bx + bw / 2, by + bh / 2);
  }

  _drawSettings() {
    const ctx = this.ctx, cx = W / 2;

    ctx.fillStyle = '#f0dca0';
    ctx.fillRect(0, 0, W, H);

    if (this.images.logo) {
      const lw = 220, lh = 110;
      ctx.drawImage(this.images.logo, cx - lw / 2, H / 4 - lh / 2, lw, lh);
    }

    ctx.fillStyle = '#000';
    ctx.font = 'bold 36px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Settings', cx, H / 2 - 65);

    this._drawToggle(this.ui.musicToggle);
    this._drawToggle(this.ui.soundToggle);
    this._drawBtn(this.ui.play, 'Play');
  }

  _drawGame() {
    const ctx = this.ctx;

    if (this.images.bg) {
      ctx.drawImage(this.images.bg, 0, 0, W, H);
    } else {
      ctx.fillStyle = '#f0dca0';
      ctx.fillRect(0, 0, W, H);
    }

    // Draw sprites: obstacles, trash, boosts, then player on top
    for (const s of [...this.obstacles, ...this.trash, ...this.boosts, this.player]) {
      const img = this.images[s.img];
      if (img) ctx.drawImage(img, s.x, s.y, s.w, s.h);
    }

    // Score (top right)
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.font = 'bold 36px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    ctx.fillText('Score: ' + this.score, W - 10, 12);

    // Timer (bottom right)
    ctx.textBaseline = 'bottom';
    ctx.fillText('Time: ' + this.elapsed + 's', W - 10, H - 10);
  }

  _drawGameOver() {
    this._drawGame();

    const ctx = this.ctx, cx = W / 2;
    ctx.fillStyle = 'rgba(0,0,0,0.65)';
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';

    ctx.font = 'bold 58px Arial';
    ctx.textBaseline = 'middle';
    ctx.fillText('GAME OVER', cx, H / 2 - 90);

    ctx.font = '34px Arial';
    ctx.fillText('Score: ' + this.score,         cx, H / 2 - 10);
    ctx.fillText('Time: '  + this.elapsed + 's', cx, H / 2 + 45);

    this._drawBtn(this.ui.playAgain, 'Play Again');
  }

  // ── Audio ─────────────────────────────────────────────────────────

  _playMusic() {
    const s = this.sounds.waves;
    if (s) { s.currentTime = 0; s.play().catch(() => {}); }
  }

  _stopMusic() {
    const s = this.sounds.waves;
    if (s) s.pause();
  }

  _playSound(name) {
    const s = this.sounds[name];
    if (s) { s.currentTime = 0; s.play().catch(() => {}); }
  }

  // ── Loop ──────────────────────────────────────────────────────────

  _loop(timestamp) {
    const delta = Math.min(timestamp - this.lastTime, 100); // cap at 100ms to avoid spiral of death
    this.lastTime = timestamp;

    if (this.state === 'playing') this._update(timestamp, delta);

    this.ctx.clearRect(0, 0, W, H);
    if (this.state === 'settings')  this._drawSettings();
    if (this.state === 'playing')   this._drawGame();
    if (this.state === 'gameover')  this._drawGameOver();

    requestAnimationFrame(t => this._loop(t));
  }
}

window.addEventListener('load', () => new Game(document.getElementById('gameCanvas')));
