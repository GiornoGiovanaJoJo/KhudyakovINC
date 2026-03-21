<template>
  <div class="interactive-hero" ref="container" @mousedown="onDown" @mouseup="onUp" @touchstart.passive="onDown" @touchend.passive="onUp">
    <canvas ref="canvas"></canvas>
    <div class="hero-overlay"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const container = ref(null)
const canvas = ref(null)
let ctx = null
let animationFrameId = null
let isVisible = true
let isMobile = false
let w, h

// Deep Space Palette
const COLORS = ['#00d2ff', '#7a28cb', '#ff007f', '#a29bfe', '#00cec9', '#ffffff', '#fd79a8', '#f1c40f']

const mouse = { x: null, y: null, isDown: false }

const BH_STATE = {
  NORMAL: 0,
  SUCKING: 1,
  EXPLODING: 2,
  COLLAPSING: 3
}

const singularity = { 
  x: null, 
  y: null, 
  time: 0,
  state: BH_STATE.NORMAL,
  explosionProgress: 0,
  shockwaveRadius: 0,
  suckedColors: []
}

// Environment Arrays
let backgroundStars = []
let nebulas = []
let miniGalaxies = []
let galacticDust = []
let accretionClouds = []
let comets = []

// ─── Utility ───
const randomColor = () => COLORS[Math.floor(Math.random() * COLORS.length)]

// ─── Fast Sprite Texture Cache (Replaces expensive ctx.filter blurs) ───
const spriteCache = {}

const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '255, 255, 255';
}

const getGlowTexture = (hexColor) => {
  if (spriteCache[hexColor]) return spriteCache[hexColor]
  const size = 128 // High res for large nebulas
  const cvs = document.createElement('canvas')
  cvs.width = size
  cvs.height = size
  const octx = cvs.getContext('2d')
  
  const rgb = hexToRgb(hexColor)
  const grad = octx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2)
  grad.addColorStop(0, `rgba(${rgb}, 1)`)
  grad.addColorStop(0.1, `rgba(${rgb}, 0.9)`)
  grad.addColorStop(0.35, `rgba(${rgb}, 0.5)`)
  grad.addColorStop(0.65, `rgba(${rgb}, 0.1)`)
  grad.addColorStop(1, `rgba(${rgb}, 0)`)
  
  octx.fillStyle = grad
  octx.fillRect(0, 0, size, size)
  
  spriteCache[hexColor] = cvs
  return cvs
}

// ─── Classes ───

class Nebula {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.radius = Math.random() * 800 + 400
    this.color = randomColor()
    this.vx = (Math.random() - 0.5) * 0.1
    this.vy = (Math.random() - 0.5) * 0.1
    this.pulsePhase = Math.random() * Math.PI * 2
    this.pulseSpeed = Math.random() * 0.005 + 0.002
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    this.pulsePhase += this.pulseSpeed
    
    if (this.x < -this.radius) this.x = w + this.radius
    if (this.x > w + this.radius) this.x = -this.radius
    if (this.y < -this.radius) this.y = h + this.radius
    if (this.y > h + this.radius) this.y = -this.radius

    const alphaBase = 0.05 + Math.sin(this.pulsePhase) * 0.03
    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius)
    const alphaHex = Math.max(0, Math.floor(alphaBase * 255)).toString(16).padStart(2, '0')
    const colorHex = this.color.length === 7 ? this.color : '#ffffff'
    
    grad.addColorStop(0, colorHex + alphaHex) 
    grad.addColorStop(1, colorHex + '00')
    
    ctx.globalCompositeOperation = 'screen'
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

class MiniGalaxy {
  constructor(initial = true) {
    this.reset(initial)
  }
  reset(initial = false) {
    this.x = initial ? Math.random() * window.innerWidth : (Math.random() > 0.5 ? -200 : w + 200)
    this.y = Math.random() * window.innerHeight
    this.radius = Math.random() * 80 + 40
    this.color = randomColor()
    this.coreColor = randomColor()
    
    this.vx = (Math.random() - 0.5) * 0.15
    this.vy = (Math.random() - 0.5) * 0.15
    this.angle = Math.random() * Math.PI * 2
    this.spin = (Math.random() * 0.015 + 0.005) * (Math.random() > 0.5 ? 1 : -1)
    
    this.tilt = Math.random() * 0.5 + 0.2
    this.axisAngle = Math.random() * Math.PI
    
    this.stars = []
    for(let i=0; i < 40; i++) {
        const r = Math.pow(Math.random(), 1.5) * this.radius
        const arm = Math.random() > 0.5 ? 0 : Math.PI
        const theta = r * 0.15 + arm + (Math.random() - 0.5) * 0.5
        this.stars.push({r, theta, s: Math.random() * 1.5 + 0.5})
    }
  }
  update(bhX, bhY) {
    const dx = bhX - this.x
    const dy = bhY - this.y
    const dist = Math.sqrt(dx*dx + dy*dy)

    if (singularity.state === BH_STATE.SUCKING) {
      const pull = Math.max(0, 1500 / (dist * dist))
      this.vx += (dx / dist) * pull
      this.vy += (dy / dist) * pull
      this.spin *= 1.05 
    } else {
      if (Math.abs(this.vx) > 0.3) this.vx *= 0.98
      if (Math.abs(this.vy) > 0.3) this.vy *= 0.98
    }

    this.x += this.vx
    this.y += this.vy
    this.angle += this.spin

    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.axisAngle)
    ctx.scale(1, this.tilt)
    ctx.rotate(this.angle)

    ctx.globalCompositeOperation = 'screen'
    
    const grad = ctx.createRadialGradient(0,0,0, 0,0, this.radius)
    grad.addColorStop(0, '#ffffff')
    grad.addColorStop(0.1, this.coreColor)
    grad.addColorStop(0.4, this.color)
    grad.addColorStop(1, 'rgba(0,0,0,0)')
    
    ctx.fillStyle = grad
    const alpha = dist < 60 ? Math.max(0, (dist - 20) / 40) : 1
    ctx.globalAlpha = alpha

    ctx.beginPath()
    ctx.arc(0, 0, this.radius, 0, Math.PI*2)
    ctx.fill()

    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
    for(const s of this.stars) {
      const sx = Math.cos(s.theta) * s.r
      const sy = Math.sin(s.theta) * s.r
      ctx.beginPath()
      ctx.arc(sx, sy, s.s, 0, Math.PI*2)
      ctx.fill()
    }
    ctx.restore()

    if (dist < 30 && singularity.state === BH_STATE.SUCKING) {
      singularity.suckedColors.push(this.color, this.coreColor)
      this.reset()
    }
    if (this.x < -300 || this.x > w + 300 || this.y < -300 || this.y > h + 300) {
      this.reset()
    }
  }
}

class StaticStar {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.z = Math.random() * 3 + 1.0 
    this.size = Math.random() * 1.5 + 0.2
    this.baseAlpha = Math.random() * 0.5 + 0.1
    this.blinkAngle = Math.random() * Math.PI * 2
    this.blinkSpeed = Math.random() * 0.02 + 0.005
    this.color = Math.random() > 0.85 ? randomColor() : '#ffffff'
  }
  update() {
    this.blinkAngle += this.blinkSpeed
    const alpha = this.baseAlpha + Math.sin(this.blinkAngle) * 0.4
    
    let px = this.x
    let py = this.y
    if (mouse.x !== null) {
      px += (mouse.x - w/2) * 0.005 * this.z
      py += (mouse.y - h/2) * 0.005 * this.z
    }

    if (alpha > 0) {
      ctx.globalCompositeOperation = 'screen'
      ctx.fillStyle = this.color
      ctx.globalAlpha = Math.min(1, alpha)
      ctx.beginPath()
      ctx.arc(px, py, this.size, 0, Math.PI * 2)
      ctx.fill()
      ctx.globalAlpha = 1.0
    }
  }
}

// Massive Volumetric 3D Accretion Plasma Clouds & Nebulas
class AccretionCloud {
  constructor(maxR) {
    this.maxR = maxR
    this.reset()
    this.angle = Math.random() * Math.PI * 2
  }
  reset() {
    const R_EVENT = isMobile ? 45 : 65
    // Dense hugging of the event horizon, exponentially thinning outward
    this.orbitRadius = R_EVENT + Math.pow(Math.random(), 4) * (this.maxR - R_EVENT)
    this.angle = Math.random() * Math.PI * 2
    
    // Kepler speed
    this.speed = (Math.random() * 0.5 + 0.5) * Math.sqrt(200 / this.orbitRadius) * 0.03
    
    const roll = Math.random()
    // 3% giant fluffy nebulas, 27% medium gas clumps, 70% dense hot dust
    if (roll > 0.97) {
      this.size = Math.random() * 50 + 20
      this.alphaBase = Math.random() * 0.1 + 0.05
    } else if (roll > 0.7) {
      this.size = Math.random() * 15 + 5
      this.alphaBase = Math.random() * 0.3 + 0.1
    } else {
      this.size = Math.random() * 3 + 1
      this.alphaBase = Math.random() * 0.5 + 0.3
    }
    
    // Superheated white/cyan core, cooling into pink and deep violet edges
    const colorRoll = Math.random()
    if (this.orbitRadius < R_EVENT + 15) {
      this.color = colorRoll > 0.4 ? '#ffffff' : '#00d2ff'
    } else if (this.orbitRadius < R_EVENT + 80) {
      this.color = colorRoll > 0.5 ? '#00d2ff' : '#ff007f'
    } else {
      this.color = colorRoll > 0.6 ? '#7a28cb' : (colorRoll > 0.8 ? '#ff007f' : '#00d2ff')
    }

    this.pulsePhase = Math.random() * Math.PI * 2
    this.pulseSpeed = Math.random() * 0.03 + 0.01
    
    this.blown = false
    this.vx = 0
    this.vy = 0
  }
  
  update(isSucking) {
    const R_EVENT = isMobile ? 45 : 65
    if (singularity.state === BH_STATE.EXPLODING) {
      if (!this.blown) {
         this.vy = Math.sin(this.angle) * (Math.random() * 40 + 10)
         this.vx = Math.cos(this.angle) * (Math.random() * 40 + 10)
         this.blown = true
      }
      this.orbitRadius += Math.sqrt(this.vx**2 + this.vy**2) * 1.5
      this.angle += 0.05
    } else if (singularity.state === BH_STATE.COLLAPSING) {
      this.orbitRadius -= this.orbitRadius * 0.2
      this.angle += 0.3
      this.blown = false
    } else {
      this.blown = false
      this.angle -= this.speed * (isSucking ? 3 : 1)
      // Slight inward drift if sucking
      if (isSucking && this.orbitRadius > R_EVENT + 2) {
          this.orbitRadius -= (this.orbitRadius - R_EVENT) * 0.015
      }
    }
    this.pulsePhase += this.pulseSpeed
  }
  
  draw(ctx, tilt = 0.16) {
    let a = this.alphaBase + Math.sin(this.pulsePhase) * 0.15
    // Fade softly at absolute outer edges
    if (this.orbitRadius > this.maxR - 50) {
      a *= Math.max(0, (this.maxR - this.orbitRadius) / 50)
    }
    if (a <= 0) return

    // Calculate un-squashed physical flat-plane raw coordinates
    const rawX = Math.cos(this.angle) * this.orbitRadius
    const rawY = Math.sin(this.angle) * this.orbitRadius
    
    // Mathematically project onto 3D camera plane (squash Y directly vs relying on context.scale)
    const x = rawX
    const y = rawY * tilt
    
    // Depth scaling! Particles strictly closer to camera (y>0) enlarge, farther shrink
    const depthScale = 1 + (rawY / this.maxR) * 0.4
    const drawSize = this.size * 2.5 * depthScale 

    const sprite = getGlowTexture(this.color)
    ctx.globalAlpha = Math.min(1, a)
    // Drawing a pure round 1:1 sprite natively without context scaling forces the clouds to stay perfectly fluffy/round
    // while traversing a highly flattened 3D elliptical orbit path.
    ctx.drawImage(sprite, x - drawSize, y - drawSize, drawSize * 2, drawSize * 2)
  }
}

class Comet {
  constructor() {
    this.reset()
    this.active = false
  }
  reset() {
    this.x = Math.random() * w
    this.y = -100
    this.length = Math.random() * 250 + 150
    this.speed = Math.random() * 25 + 15
    this.angle = (Math.PI / 4) + (Math.random() * 0.3 - 0.15)
    this.active = true
    this.color = randomColor()
  }
  update() {
    if (!this.active) {
      if (Math.random() < 0.005) this.reset()
      return
    }
    this.x += Math.cos(this.angle) * this.speed
    this.y += Math.sin(this.angle) * this.speed

    const tailX = this.x - Math.cos(this.angle) * this.length
    const tailY = this.y - Math.sin(this.angle) * this.length

    const grad = ctx.createLinearGradient(this.x, this.y, tailX, tailY)
    grad.addColorStop(0, '#ffffff')
    grad.addColorStop(0.1, this.color)
    grad.addColorStop(1, this.color + '00')

    ctx.globalCompositeOperation = 'screen'
    ctx.strokeStyle = grad
    ctx.lineWidth = 4
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(tailX, tailY)
    ctx.stroke()

    if (singularity.state === BH_STATE.EXPLODING) this.speed *= 1.2
    if (this.x > w + 400 || this.y > h + 400 || this.x < -400) this.active = false
  }
}

// ─── Drawing Interstellar-style Gargantua Volumetric Black Hole ───

const drawGargantuaVolumetric = (x, y, r, isSucking) => {
  ctx.save()
  ctx.translate(x, y)

  const R = r
  const t = singularity.time
  
  // Dramatically slowed down majestic pulsation speed!
  const pulse1 = Math.sin(t * 0.5)
  const pulse2 = Math.sin(t * 1.2)

  accretionClouds.forEach(c => c.update(isSucking))
  
  // Mathematical 3D sort: y < 0 is the upper visual arc (representing the FAR back side of the disk)
  const backClouds = accretionClouds.filter(c => Math.sin(c.angle) < 0)
  // Mathematical 3D sort: y >= 0 is the lower visual arc (representing the CLOSE front side of the disk)
  const frontClouds = accretionClouds.filter(c => Math.sin(c.angle) >= 0)
  
  // 1. FAR BACKGROUND AMBIENT GLOW
  ctx.save()
  ctx.scale(1, 0.25)
  const baseSize = R*14 + pulse1 * R*0.5
  const ambient = ctx.createRadialGradient(0, 0, R*1.5, 0, 0, baseSize)
  ambient.addColorStop(0, 'rgba(0, 210, 255, 0.4)')
  ambient.addColorStop(0.4, 'rgba(122, 40, 203, 0.15)')
  ambient.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = ambient
  ctx.globalCompositeOperation = 'screen'
  ctx.beginPath(); ctx.arc(0, 0, baseSize, 0, Math.PI*2); ctx.fill()
  ctx.restore()

  // 2. GRAVITATIONAL LENSING (Top & Bottom Halos showing lensed back disk)
  ctx.save()
  ctx.translate(0, -R * 0.8) 
  ctx.scale(1, 0.7 + pulse1*0.01) // Majestic subtle breathing
  const topSize = R*4.5 + pulse2*R*0.05
  const topHalo = ctx.createRadialGradient(0, 0, R*0.6, 0, 0, topSize)
  topHalo.addColorStop(0, `rgba(255, 255, 255, ${0.9 + pulse2*0.05})`) 
  topHalo.addColorStop(0.15, 'rgba(0, 210, 255, 0.6)')
  topHalo.addColorStop(0.4, 'rgba(122, 40, 203, 0.2)')
  topHalo.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = topHalo
  ctx.globalCompositeOperation = 'screen'
  ctx.beginPath(); ctx.arc(0, 0, topSize, 0, Math.PI*2); ctx.fill()
  ctx.restore()

  ctx.save()
  ctx.translate(0, R * 0.8) 
  ctx.scale(1, 0.7) 
  const botSize = R*3.5 + pulse1*R*0.05
  const bottomHalo = ctx.createRadialGradient(0, 0, R*0.6, 0, 0, botSize)
  bottomHalo.addColorStop(0, 'rgba(255, 255, 255, 0.4)') 
  bottomHalo.addColorStop(0.2, 'rgba(255, 0, 127, 0.2)')
  bottomHalo.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = bottomHalo
  ctx.globalCompositeOperation = 'screen'
  ctx.beginPath(); ctx.arc(0, 0, botSize, 0, Math.PI*2); ctx.fill()
  ctx.restore()

  const PIXEL_TILT = 0.16

  // 3. BACK CLOUDS (Orbiting behind the event horizon)
  ctx.save()
  ctx.globalCompositeOperation = 'screen' // Pre-cached sprites draw super fast
  for(const c of backClouds) c.draw(ctx, PIXEL_TILT)
  ctx.restore()

  // 4. THE EVENT HORIZON (Pure Black Void flawlessly occludes Back Clouds)
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = '#010002'
  ctx.beginPath() 
  ctx.arc(0, 0, R, 0, Math.PI * 2) 
  ctx.fill()

  // 5. PHOTON RING (Wavers and Boils right on the boundary)
  const ringSize = R*1.3 + pulse2 * R*0.05
  const photonGradient = ctx.createRadialGradient(0, 0, R*0.95, 0, 0, ringSize)
  photonGradient.addColorStop(0, 'rgba(0,0,0,0)')
  photonGradient.addColorStop(0.1, `rgba(255, 255, 255, ${0.8 + pulse1*0.05})`) 
  photonGradient.addColorStop(0.3, 'rgba(0, 210, 255, 0.5)')
  photonGradient.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = photonGradient
  ctx.beginPath(); ctx.arc(0, 0, ringSize, 0, Math.PI*2); ctx.fill()

  // 6. SOFT FRONT AMBIENT OVERLAY (Underglow for the front disk layers)
  ctx.save()
  ctx.scale(1, PIXEL_TILT)
  const frontSoft = ctx.createRadialGradient(0, 0, R, 0, 0, R*8)
  frontSoft.addColorStop(0, 'rgba(255, 255, 255, 0.8)')
  frontSoft.addColorStop(0.15, 'rgba(0, 210, 255, 0.6)')
  frontSoft.addColorStop(0.5, 'rgba(122, 40, 203, 0.3)')
  frontSoft.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = frontSoft
  ctx.globalCompositeOperation = 'screen'
  ctx.beginPath(); ctx.arc(0, 0, R*8, 0, Math.PI*2); ctx.fill()
  ctx.restore()

  // 7. FRONT CLOUDS (Massive, volumetric fluffy gas rendering OVER the void)
  ctx.save()
  ctx.globalCompositeOperation = 'screen'
  for(const c of frontClouds) c.draw(ctx, PIXEL_TILT)
  ctx.restore()

  ctx.restore()
  ctx.globalAlpha = 1.0 
}

// Draws the 5-second cinematic Supernova Phase
const drawSupernova = (x, y) => {
  ctx.save()
  ctx.translate(x, y)
  
  // Tilted towards user plane
  ctx.scale(1, 0.45)
  ctx.rotate(Math.PI / 10) 

  ctx.globalCompositeOperation = 'screen'
  const p = singularity.explosionProgress 
  const maxR = Math.max(w, h) * 1.5 

  // Accretion clouds still update and blow away during supernova
  accretionClouds.forEach(c => c.update(false))
  ctx.save()
  accretionClouds.forEach(c => c.draw(ctx, 45)) // draw with normalized spread
  ctx.restore()

  const baseColors = singularity.suckedColors.length > 0 ? 
                     [...new Set(singularity.suckedColors)] : 
                     ['#ffffff', '#00d2ff', '#ff007f']
  
  const c1 = baseColors[0]
  const c2 = baseColors.length > 1 ? baseColors[1] : baseColors[0]
  const c3 = baseColors.length > 2 ? baseColors[2] : (baseColors[1] || baseColors[0])

  if (p < 0.8) {
    const expandP = Math.min(1, p * 4) 
    const currentR = maxR * (1 - Math.pow(1 - expandP, 4))
    const alpha = p < 0.1 ? Math.min(1, p * 10) : Math.max(0, 1 - ((p - 0.1) / 0.8))

    const flashGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, currentR)
    flashGrad.addColorStop(0, `rgba(255, 255, 255, ${alpha})`)
    
    if(baseColors.length > 3) {
      flashGrad.addColorStop(0.2, c1)
      flashGrad.addColorStop(0.4, c2)
      flashGrad.addColorStop(0.6, c3)
      flashGrad.addColorStop(0.8, baseColors[3])
    } else {
      flashGrad.addColorStop(0.3, c1)
      flashGrad.addColorStop(0.6, c2)
    }
    flashGrad.addColorStop(1, 'rgba(0,0,0,0)')
    
    ctx.globalAlpha = Math.max(0, alpha)
    ctx.fillStyle = flashGrad
    ctx.beginPath()
    ctx.arc(0, 0, currentR, 0, Math.PI*2)
    ctx.fill()

    ctx.globalAlpha = 1.0
    ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`
    ctx.lineWidth = 20 * alpha
    ctx.beginPath()
    ctx.arc(0, 0, currentR, 0, Math.PI*2)
    ctx.stroke()

    ctx.strokeStyle = c3
    ctx.globalAlpha = alpha * 0.8
    ctx.lineWidth = 50 * alpha
    ctx.stroke()
    ctx.globalAlpha = 1.0

    singularity.shockwaveRadius = currentR

  } else {
    const collapseP = (p - 0.8) / 0.2
    const collapseR = singularity.shockwaveRadius * (1 - Math.pow(collapseP, 4))
    
    const flashGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, Math.max(1, collapseR))
    flashGrad.addColorStop(0, '#ffffff')
    flashGrad.addColorStop(0.5, c1)
    flashGrad.addColorStop(1, 'rgba(0,0,0,0)')
    
    ctx.fillStyle = flashGrad
    ctx.beginPath()
    ctx.arc(0, 0, Math.max(1, collapseR), 0, Math.PI*2)
    ctx.fill()

    if (collapseP > 0.4) {
      ctx.globalCompositeOperation = 'source-over'
      ctx.fillStyle = '#010002'
      ctx.beginPath()
      const baseR = window.innerWidth > 768 ? 65 : 45
      ctx.arc(0, 0, Math.min(baseR, baseR * ((collapseP - 0.4) * 2)), 0, Math.PI*2)
      ctx.fill()
    }

    if (p >= 1.0) {
      singularity.state = BH_STATE.NORMAL
      singularity.suckedColors = [] 
      setTimeout(() => {
         accretionClouds.forEach(c => {
           if (c.orbitRadius > 2000) c.reset()
         })
      }, 500)
    }
  }

  ctx.restore()
  singularity.explosionProgress += (1 / (60 * 5))
}


// ─── Initialization & Loop ───

const init = () => {
  w = Math.max(container.value?.offsetWidth || window.innerWidth, 500)
  h = Math.max(container.value?.offsetHeight || window.innerHeight, 500)
  if (canvas.value) {
    canvas.value.width = w
    canvas.value.height = h
  }
  
  if (singularity.x === null) {
    singularity.x = w / 2
    singularity.y = h / 2
  }

  isMobile = window.innerWidth <= 768

  backgroundStars = []
  nebulas = []
  miniGalaxies = []
  galacticDust = []
  accretionClouds = []
  comets = []

  for (let i = 0; i < (isMobile ? 80 : 200); i++) backgroundStars.push(new StaticStar())
  for (let i = 0; i < (isMobile ? 3 : 5); i++) nebulas.push(new Nebula())
  
  const numGalaxies = isMobile ? 3 : Math.floor(Math.random() * 4) + 6
  for (let i = 0; i < numGalaxies; i++) miniGalaxies.push(new MiniGalaxy(true))
  
  // Increase particle density exponentially for flawless high-def volumetric gas volume
  // By pre-rendering the glowing sprite, 1200+ sprites draws in 1ms on a GPU.
  const numClouds = isMobile ? 600 : 1800 
  const maxDiskR = isMobile ? 300 : 600
  for (let i = 0; i < numClouds; i++) accretionClouds.push(new AccretionCloud(maxDiskR))

  for (let i = 0; i < 3; i++) comets.push(new Comet())
}

const animate = () => {
  if (!isVisible || !canvas.value || !ctx) return
  
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = 'rgba(2, 1, 6, 0.6)' 
  ctx.fillRect(0, 0, w, h)

  singularity.time += 0.015

  nebulas.forEach(n => n.update())
  backgroundStars.forEach(s => s.update())
  
  let targetX = mouse.x ?? w / 2
  let targetY = mouse.y ?? h / 2
  
  if (mouse.x == null) {
      targetX = (w/2) + Math.sin(Date.now() * 0.0003) * 100
      targetY = (h/2) + Math.cos(Date.now() * 0.0002) * 60
  }

  const easeSpeed = (singularity.state === BH_STATE.SUCKING) ? 0.05 : 0.03
  singularity.x += (targetX - singularity.x) * easeSpeed
  singularity.y += (targetY - singularity.y) * easeSpeed

  if (singularity.state === BH_STATE.NORMAL || singularity.state === BH_STATE.SUCKING) {
    const isSucking = (singularity.state === BH_STATE.SUCKING)
    drawGargantuaVolumetric(singularity.x, singularity.y, isMobile ? 45 : 65, isSucking)
  } else {
    drawSupernova(singularity.x, singularity.y)
  }

  miniGalaxies.forEach(mg => mg.update(singularity.x, singularity.y))
  comets.forEach(c => c.update())

  animationFrameId = requestAnimationFrame(animate)
}

// ─── Events ───

let resizeTimeout = null
const handleResize = () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    if (!canvas.value || !container.value) return
    init()
  }, 200)
}

let mouseMoveQueued = false
const handleMouseMove = (event) => {
  if (mouseMoveQueued) return
  mouseMoveQueued = true
  requestAnimationFrame(() => {
    if (!canvas.value) return
    const rect = canvas.value.getBoundingClientRect()
    const clientX = event.touches ? event.touches[0].clientX : event.clientX
    const clientY = event.touches ? event.touches[0].clientY : event.clientY
    
    mouse.x = clientX - rect.left
    mouse.y = clientY - rect.top
    mouseMoveQueued = false
  })
}

const handleMouseLeave = () => {
  mouse.x = null
  mouse.y = null
  if (mouse.isDown && singularity.state === BH_STATE.SUCKING) {
    singularity.state = BH_STATE.NORMAL
  }
  mouse.isDown = false
}

const onDown = () => { 
  mouse.isDown = true 
  if (singularity.state === BH_STATE.NORMAL) {
    singularity.state = BH_STATE.SUCKING
  }
}

const onUp = () => { 
  if (mouse.isDown && singularity.state === BH_STATE.SUCKING) {
    singularity.state = BH_STATE.EXPLODING
    singularity.explosionProgress = 0
  }
  mouse.isDown = false 
}

let visibilityObserver = null

onMounted(() => {
  ctx = canvas.value.getContext('2d', { alpha: false })
  
  window.addEventListener('resize', handleResize, { passive: true })
  
  const cvs = canvas.value
  cvs.addEventListener('mousemove', handleMouseMove, { passive: true })
  cvs.addEventListener('touchmove', handleMouseMove, { passive: true })
  cvs.addEventListener('mouseleave', handleMouseLeave)

  visibilityObserver = new IntersectionObserver((entries) => {
    isVisible = entries[0].isIntersecting
    if (isVisible) {
      if (!animationFrameId) {
        animate()
      }
    } else {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
      }
    }
  }, { threshold: 0 })
  if (container.value) {
      visibilityObserver.observe(container.value)
  }

  init()
  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (canvas.value) {
    canvas.value.removeEventListener('mousemove', handleMouseMove)
    canvas.value.removeEventListener('touchmove', handleMouseMove)
    canvas.value.removeEventListener('mouseleave', handleMouseLeave)
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  clearTimeout(resizeTimeout)
  visibilityObserver?.disconnect()
})
</script>

<style scoped>
.interactive-hero {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  background-color: #020106;
  pointer-events: auto;
  cursor: crosshair;
  -webkit-mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
  mask-image: linear-gradient(to bottom, black 70%, transparent 100%);
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, transparent 0%, rgba(2, 1, 6, 0.85) 100%);
  pointer-events: none;
}
</style>
