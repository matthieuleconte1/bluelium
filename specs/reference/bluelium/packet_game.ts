// Copyright 2026 Bluelium. Use of this source code is governed by the
// GPL-3.0 license that can be found in the LICENSE file.

// Bluelium : « Paquet perdu », le jeu de la page hors ligne. Un paquet réseau
// file sur le câble et saute par-dessus les pare-feu et les pigeons
// voyageurs. Une seule touche : Espace (ou ↑, ou un clic) pour sauter,
// maintenue pour sauter plus haut ; ↓ pour redescendre vite.

import {loadTimeData} from 'chrome://resources/js/load_time_data.js';

const HEIGHT = 150;
const MAX_WIDTH = 600;
const GROUND_Y = 124;
const PACKET_X = 44;
const PACKET_W = 22;
const PACKET_H = 16;
const GRAVITY = 0.0022;
const JUMP_VELOCITY = -0.62;
const JUMP_CUT_VELOCITY = -0.3;
const DROP_VELOCITY = 0.7;
const START_SPEED = 0.36;
const MAX_SPEED = 0.8;
const ACCELERATION = 0.0000055;
const BIRD_SCORE = 250;
const RESTART_DELAY_MS = 600;
const MAX_FRAME_MS = 34;
const ACCENT_LIGHT = '#3450d1';
const ACCENT_DARK = '#8b9cff';

enum State {
  IDLE = 0,
  RUNNING = 1,
  PAUSED = 2,
  OVER = 3,
}

interface Obstacle {
  bird: boolean,
  x: number,
  y: number,
  w: number,
  h: number,
}

interface Fragment {
  x: number,
  y: number,
  vx: number,
  vy: number,
}

interface Strings {
  lost: string,
  retryKeyboard: string,
  retryTouch: string,
  label: string,
  best: string,
  announce: string,
}

function getStrings(): Strings {
  const french = (navigator.language || '').toLowerCase().startsWith('fr');
  const strings: Strings = french ?
      {
        lost: 'Paquet perdu',
        retryKeyboard: 'Espace pour renvoyer',
        retryTouch: 'Touchez pour renvoyer',
        label: 'Jeu Paquet perdu. Espace pour sauter.',
        best: 'MAX',
        announce: 'Paquet perdu. Score : ',
      } :
      {
        lost: 'Packet lost',
        retryKeyboard: 'Space to resend',
        retryTouch: 'Tap to resend',
        label: 'Packet lost game. Press space to jump.',
        best: 'HI',
        announce: 'Packet lost. Score: ',
      };
  if (loadTimeData.isInitialized() &&
      loadTimeData.valueExists('dinoGameA11yAriaLabel')) {
    const label = loadTimeData.getValue('dinoGameA11yAriaLabel');
    if (typeof label === 'string' && label) {
      strings.label = label;
    }
  }
  return strings;
}

function random(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

function pick<T>(values: T[]): T {
  return values[Math.floor(Math.random() * values.length)]!;
}

function pad(value: number): string {
  return String(Math.floor(value)).padStart(5, '0');
}

export class PacketGame {
  private container_: HTMLElement;
  private canvas_: HTMLCanvasElement;
  private context_: CanvasRenderingContext2D;
  private liveRegion_: HTMLElement;
  private strings_: Strings = getStrings();
  private state_: State = State.IDLE;
  private width_: number = MAX_WIDTH;
  private ink_: string = '#202124';
  private paper_: string = '#ffffff';
  private accent_: string = ACCENT_LIGHT;
  private reducedMotion_: boolean = false;
  private y_: number = GROUND_Y - PACKET_H;
  private velocity_: number = 0;
  private jumpHeld_: boolean = false;
  private speed_: number = START_SPEED;
  private distance_: number = 0;
  private best_: number = 0;
  private nextGap_: number = 0;
  private obstacles_: Obstacle[] = [];
  private fragments_: Fragment[] = [];
  private lastFrame_: number = 0;
  private overAt_: number = 0;
  private frameId_: number = 0;

  constructor(container: HTMLElement) {
    this.container_ = container;
    this.canvas_ = document.createElement('canvas');
    this.canvas_.className = 'bluelium-packet-canvas';
    this.canvas_.setAttribute('aria-hidden', 'true');
    this.context_ = this.canvas_.getContext('2d')!;
    this.liveRegion_ = document.createElement('span');
    this.liveRegion_.className = 'offline-runner-live-region';
    this.liveRegion_.setAttribute('aria-live', 'polite');
    container.append(this.canvas_, this.liveRegion_);
    container.tabIndex = 0;
    container.setAttribute('role', 'application');
    container.setAttribute('aria-label', this.strings_.label);
    try {
      this.best_ = Number(sessionStorage.getItem('bluelium-packet-best')) || 0;
    } catch {
      this.best_ = 0;
    }
    this.readColors_();
    this.resize_();
    this.bindEvents_();
    this.draw_();
  }

  static initialize(wrapperSelector: string): PacketGame|null {
    const wrapper = document.querySelector<HTMLElement>(wrapperSelector);
    if (!wrapper) {
      return null;
    }
    if (loadTimeData.isInitialized() &&
        loadTimeData.valueExists('disabledEasterEgg')) {
      return null;
    }
    const container = document.createElement('div');
    container.className = 'bluelium-packet';
    wrapper.prepend(container);
    document.documentElement.classList.add('bluelium-packet-game');
    return new PacketGame(container);
  }

  private bindEvents_() {
    document.addEventListener('keydown', e => this.onKeyDown_(e));
    document.addEventListener('keyup', e => this.onKeyUp_(e));
    this.canvas_.addEventListener('pointerdown', e => {
      e.preventDefault();
      this.press_();
    });
    this.canvas_.addEventListener('pointerup', () => this.release_());
    this.canvas_.addEventListener('pointercancel', () => this.release_());
    window.addEventListener('resize', () => {
      this.resize_();
      this.draw_();
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pause_();
      }
    });
    window.addEventListener('blur', () => this.pause_());
    const scheme = window.matchMedia('(prefers-color-scheme: dark)');
    scheme.addEventListener('change', () => {
      this.readColors_();
      this.draw_();
    });
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    this.reducedMotion_ = motion.matches;
    motion.addEventListener('change', () => {
      this.reducedMotion_ = motion.matches;
    });
  }

  private onKeyDown_(e: KeyboardEvent) {
    const target = e.target;
    if (target instanceof Element && target !== this.container_ &&
        target.closest('button, a, input, textarea, select')) {
      return;
    }
    if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') {
      e.preventDefault();
      if (!e.repeat) {
        this.press_();
      }
    } else if (e.code === 'ArrowDown' && this.state_ === State.RUNNING) {
      e.preventDefault();
      if (this.y_ < GROUND_Y - PACKET_H) {
        this.velocity_ = Math.max(this.velocity_, DROP_VELOCITY);
      }
    }
  }

  private onKeyUp_(e: KeyboardEvent) {
    if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') {
      this.release_();
    }
  }

  private press_() {
    switch (this.state_) {
      case State.IDLE:
      case State.PAUSED:
        this.start_();
        this.jump_();
        break;
      case State.RUNNING:
        this.jump_();
        break;
      case State.OVER:
        if (performance.now() - this.overAt_ > RESTART_DELAY_MS) {
          this.reset_();
          this.start_();
          this.jump_();
        }
        break;
    }
  }

  private release_() {
    this.jumpHeld_ = false;
    if (this.velocity_ < JUMP_CUT_VELOCITY) {
      this.velocity_ = JUMP_CUT_VELOCITY;
    }
  }

  private jump_() {
    if (this.y_ >= GROUND_Y - PACKET_H) {
      this.velocity_ = JUMP_VELOCITY;
      this.jumpHeld_ = true;
    }
  }

  private start_() {
    this.state_ = State.RUNNING;
    this.lastFrame_ = performance.now();
    this.container_.focus({preventScroll: true});
    if (!this.frameId_) {
      this.frameId_ = requestAnimationFrame(t => this.frame_(t));
    }
  }

  private pause_() {
    if (this.state_ === State.RUNNING) {
      this.state_ = State.PAUSED;
      this.release_();
    }
  }

  private reset_() {
    this.y_ = GROUND_Y - PACKET_H;
    this.velocity_ = 0;
    this.speed_ = START_SPEED;
    this.distance_ = 0;
    this.obstacles_ = [];
    this.fragments_ = [];
    this.nextGap_ = 0;
  }

  private gameOver_() {
    this.state_ = State.OVER;
    this.overAt_ = performance.now();
    this.jumpHeld_ = false;
    const score = Math.floor(this.distance_ / 40);
    if (score > this.best_) {
      this.best_ = score;
      try {
        sessionStorage.setItem('bluelium-packet-best', String(score));
      } catch {
        // Stockage indisponible : le record reste en mémoire.
      }
    }
    this.liveRegion_.textContent = this.strings_.announce + score;
    if (!this.reducedMotion_) {
      const x = PACKET_X + PACKET_W / 2;
      const y = this.y_ + PACKET_H / 2;
      this.fragments_.push(
          {x, y, vx: -0.12, vy: -0.3}, {x, y, vx: 0.1, vy: -0.34},
          {x, y, vx: -0.06, vy: -0.2}, {x, y, vx: 0.16, vy: -0.18});
    }
  }

  private frame_(now: number) {
    this.frameId_ = 0;
    const dt = Math.min(MAX_FRAME_MS, now - this.lastFrame_);
    this.lastFrame_ = now;
    if (this.state_ === State.RUNNING) {
      this.update_(dt);
    } else if (this.state_ === State.OVER) {
      this.updateFragments_(dt);
    }
    this.draw_();
    const animating = this.state_ === State.RUNNING ||
        (this.state_ === State.OVER && this.fragments_.length > 0);
    if (animating) {
      this.frameId_ = requestAnimationFrame(t => this.frame_(t));
    }
  }

  private update_(dt: number) {
    this.speed_ = Math.min(MAX_SPEED, this.speed_ + ACCELERATION * dt);
    const step = this.speed_ * dt;
    this.distance_ += step;

    // Saut : la gravité est plus faible tant que la touche est tenue.
    const gravity = this.jumpHeld_ && this.velocity_ < 0 ? GRAVITY * 0.62 :
                                                           GRAVITY;
    this.velocity_ += gravity * dt;
    this.y_ += this.velocity_ * dt;
    if (this.y_ >= GROUND_Y - PACKET_H) {
      this.y_ = GROUND_Y - PACKET_H;
      this.velocity_ = 0;
    }

    for (const obstacle of this.obstacles_) {
      obstacle.x -= step * (obstacle.bird ? 1.12 : 1);
    }
    this.obstacles_ = this.obstacles_.filter(o => o.x + o.w > -10);
    this.nextGap_ -= step;
    if (this.nextGap_ <= 0) {
      this.spawn_();
    }

    const inset = 3;
    for (const o of this.obstacles_) {
      if (PACKET_X + inset < o.x + o.w - inset &&
          PACKET_X + PACKET_W - inset > o.x + inset &&
          this.y_ + inset < o.y + o.h - inset &&
          this.y_ + PACKET_H - inset > o.y + inset) {
        this.gameOver_();
        return;
      }
    }
  }

  private spawn_() {
    const score = this.distance_ / 40;
    const bird = score > BIRD_SCORE && Math.random() < 0.3;
    if (bird) {
      const high = Math.random() < 0.5;
      this.obstacles_.push({
        bird: true,
        x: this.width_ + 10,
        y: high ? GROUND_Y - 64 : GROUND_Y - 32,
        w: 26,
        h: 14,
      });
    } else {
      const w = pick([16, 22, 30]);
      const h = pick(score < 100 ? [26, 32] : [26, 36, 46]);
      this.obstacles_.push(
          {bird: false, x: this.width_ + 10, y: GROUND_Y - h, w, h});
    }
    const minGap = this.speed_ * 430 + 150;
    this.nextGap_ = random(minGap, minGap * 1.9);
  }

  private updateFragments_(dt: number) {
    for (const f of this.fragments_) {
      f.vy += GRAVITY * dt;
      f.x += f.vx * dt;
      f.y += f.vy * dt;
    }
    this.fragments_ = this.fragments_.filter(f => f.y < HEIGHT + 10);
  }

  private readColors_() {
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.accent_ = dark ? ACCENT_DARK : ACCENT_LIGHT;
    const color = getComputedStyle(this.container_).color;
    this.ink_ = color || (dark ? '#e8eaed' : '#202124');
    // Fond réel de la page, pour dessiner les joints des briques.
    let paper = '';
    for (const el of [document.body, document.documentElement]) {
      const background = getComputedStyle(el).backgroundColor;
      if (background && background !== 'transparent' &&
          !background.startsWith('rgba(0, 0, 0, 0)')) {
        paper = background;
        break;
      }
    }
    this.paper_ = paper || (dark ? '#202124' : '#ffffff');
  }

  private resize_() {
    const parentWidth = this.container_.parentElement?.clientWidth || MAX_WIDTH;
    this.width_ = Math.max(240, Math.min(MAX_WIDTH, parentWidth));
    const ratio = window.devicePixelRatio || 1;
    this.canvas_.width = Math.round(this.width_ * ratio);
    this.canvas_.height = Math.round(HEIGHT * ratio);
    this.canvas_.style.width = `${this.width_}px`;
    this.canvas_.style.height = `${HEIGHT}px`;
    this.context_.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  private draw_() {
    const ctx = this.context_;
    ctx.clearRect(0, 0, this.width_, HEIGHT);
    this.drawCable_(ctx);
    for (const o of this.obstacles_) {
      if (o.bird) {
        this.drawBird_(ctx, o);
      } else {
        this.drawWall_(ctx, o);
      }
    }
    if (this.state_ === State.OVER) {
      this.drawFragments_(ctx);
      this.drawMessage_(ctx);
    } else {
      this.drawPacket_(ctx);
    }
    this.drawScore_(ctx);
  }

  private drawCable_(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = this.ink_;
    ctx.fillRect(0, GROUND_Y, this.width_, 1);
    // Impulsions de données le long du câble.
    ctx.globalAlpha = 0.18;
    const offset = this.reducedMotion_ ? 0 : this.distance_ % 48;
    for (let x = -offset; x < this.width_; x += 48) {
      ctx.fillRect(x, GROUND_Y + 5, 14, 1);
      ctx.fillRect(x + 26, GROUND_Y + 10, 6, 1);
    }
    ctx.restore();
  }

  private drawPacket_(ctx: CanvasRenderingContext2D) {
    const running = this.state_ === State.RUNNING;
    const x = PACKET_X;
    const y = Math.round(this.y_);

    // Traînée de bits pendant la course.
    if (running && !this.reducedMotion_) {
      ctx.save();
      ctx.fillStyle = this.accent_;
      for (let i = 1; i <= 3; i++) {
        ctx.globalAlpha = 0.45 - i * 0.12;
        const size = 5 - i;
        ctx.fillRect(x - i * 8, y + PACKET_H / 2 - size / 2 +
                         Math.sin((this.distance_ / 20) + i) * 1.5,
                     size, size);
      }
      ctx.restore();
    }

    ctx.save();
    ctx.fillStyle = this.accent_;
    ctx.beginPath();
    ctx.roundRect(x, y, PACKET_W, PACKET_H, 4);
    ctx.fill();
    // Rabat de l'enveloppe.
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(x + 4, y + 4);
    ctx.lineTo(x + PACKET_W / 2, y + 9);
    ctx.lineTo(x + PACKET_W - 4, y + 4);
    ctx.stroke();
    ctx.restore();
  }

  private drawWall_(ctx: CanvasRenderingContext2D, o: Obstacle) {
    ctx.save();
    ctx.fillStyle = this.ink_;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.roundRect(Math.round(o.x), o.y, o.w, o.h, 2);
    ctx.fill();
    // Joints des briques du pare-feu.
    ctx.globalAlpha = 1;
    ctx.strokeStyle = this.paper_;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let row = 1; row * 8 < o.h; row++) {
      const y = o.y + row * 8 + 0.5;
      ctx.moveTo(o.x, y);
      ctx.lineTo(o.x + o.w, y);
      const shift = row % 2 ? 0 : 5;
      for (let x = o.x + 5 + shift; x < o.x + o.w - 2; x += 10) {
        ctx.moveTo(Math.round(x) + 0.5, y - 8);
        ctx.lineTo(Math.round(x) + 0.5, y);
      }
    }
    ctx.stroke();
    ctx.restore();
  }

  private drawBird_(ctx: CanvasRenderingContext2D, o: Obstacle) {
    const flap = this.reducedMotion_ ? 0 :
                                       Math.floor(this.distance_ / 60) % 2;
    const x = Math.round(o.x);
    const y = o.y;
    ctx.save();
    ctx.fillStyle = this.ink_;
    ctx.globalAlpha = 0.85;
    // Corps et tête du pigeon voyageur (RFC 1149).
    ctx.beginPath();
    ctx.ellipse(x + 14, y + 8, 10, 5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(x + 4, y + 5, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y + 5);
    ctx.lineTo(x - 4, y + 6);
    ctx.lineTo(x, y + 7);
    ctx.fill();
    // Aile.
    ctx.beginPath();
    if (flap) {
      ctx.moveTo(x + 10, y + 6);
      ctx.lineTo(x + 20, y - 6);
      ctx.lineTo(x + 22, y + 6);
    } else {
      ctx.moveTo(x + 10, y + 8);
      ctx.lineTo(x + 20, y + 18);
      ctx.lineTo(x + 22, y + 8);
    }
    ctx.fill();
    ctx.restore();
  }

  private drawFragments_(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.fillStyle = this.accent_;
    if (this.fragments_.length === 0 && this.reducedMotion_) {
      ctx.globalAlpha = 0.5;
      ctx.beginPath();
      ctx.roundRect(PACKET_X, this.y_, PACKET_W, PACKET_H, 4);
      ctx.fill();
    }
    for (const f of this.fragments_) {
      ctx.fillRect(f.x - 4, f.y - 4, 8, 8);
    }
    ctx.restore();
  }

  private drawMessage_(ctx: CanvasRenderingContext2D) {
    const touch = navigator.maxTouchPoints > 0 &&
        !window.matchMedia('(hover: hover)').matches;
    ctx.save();
    ctx.textAlign = 'center';
    ctx.fillStyle = this.ink_;
    ctx.font = '600 15px system-ui, sans-serif';
    ctx.fillText(this.strings_.lost, this.width_ / 2, 58);
    ctx.globalAlpha = 0.6;
    ctx.font = '13px system-ui, sans-serif';
    ctx.fillText(
        touch ? this.strings_.retryTouch : this.strings_.retryKeyboard,
        this.width_ / 2, 80);
    ctx.restore();
  }

  private drawScore_(ctx: CanvasRenderingContext2D) {
    if (this.state_ === State.IDLE && this.best_ === 0) {
      return;
    }
    const score = pad(this.distance_ / 40);
    ctx.save();
    ctx.textAlign = 'right';
    ctx.font = '600 12px ui-monospace, Menlo, monospace';
    ctx.fillStyle = this.ink_;
    ctx.fillText(score, this.width_ - 4, 16);
    if (this.best_ > 0) {
      ctx.globalAlpha = 0.5;
      const width = ctx.measureText(score).width;
      ctx.fillText(`${this.strings_.best} ${pad(this.best_)}`,
                   this.width_ - 16 - width, 16);
    }
    ctx.restore();
  }
}
