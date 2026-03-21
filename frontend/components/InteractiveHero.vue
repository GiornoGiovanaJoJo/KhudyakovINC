<template>
  <div class="interactive-hero" ref="container" @mousedown="onDown" @mouseup="onUp" @touchstart="onDown" @touchend="onUp">
    <canvas ref="canvas"></canvas>
    <!-- Overlay for text readability -->
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
let w, h

// Palette
const C_BG = '#05020a'
const COLORS = ['#00d2ff', '#7a28cb', '#ff007f', '#a29bfe']

const mouse = { x: null, y: null, isDown: false }
const blackHole = { x: null, y: null, time: 0, shockwave: 0 }

// Environment Arrays
let backgroundStars = []
let nebulas = []
let spiralDust = []
let comets = []
let meteorites = []

// ─── Utility ───
const randomColor = () => COLORS[Math.floor(Math.random() * COLORS.length)]

// ─── Classes ───

class Nebula {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.radius = Math.random() * 400 + 300
    this.color = randomColor()
    this.vx = (Math.random() - 0.5) * 0.2
    this.vy = (Math.random() - 0.5) * 0.2
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    if (this.x < -this.radius) this.x = w + this.radius
    if (this.x > w + this.radius) this.x = -this.radius
    if (this.y < -this.radius) this.y = h + this.radius
    if (this.y > h + this.radius) this.y = -this.radius

    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius)
    grad.addColorStop(0, this.color + '15') // ~8% opacity hex
    grad.addColorStop(1, this.color + '00')
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

class StaticStar {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.size = Math.random() * 1.2 + 0.2
    this.baseAlpha = Math.random() * 0.5 + 0.1
    this.blinkAngle = Math.random() * Math.PI * 2
    this.blinkSpeed = Math.random() * 0.02 + 0.005
    this.color = Math.random() > 0.8 ? randomColor() : '#ffffff'
  }
  update() {
    this.blinkAngle += this.blinkSpeed
    const alpha = this.baseAlpha + Math.sin(this.blinkAngle) * 0.3
    if (alpha > 0) {
      ctx.fillStyle = this.color
      ctx.globalAlpha = Math.min(1, alpha)
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.fill()
      ctx.globalAlpha = 1.0
    }
  }
}

class SpiralDust {
  constructor() {
    this.angle = Math.random() * Math.PI * 2
    this.baseRadius = Math.random() * (window.innerWidth > 768 ? 600 : 300) + 40
    this.radius = this.baseRadius
    // Kepler-like speed: slower further out
    this.speed = (Math.random() * 2 + 1) / Math.sqrt(this.radius) * (Math.random() > 0.2 ? 1 : -1)
    this.size = Math.random() * 1.5 + 0.5
    this.color = randomColor()
    this.zScale = Math.random() * 0.4 + 0.2 // for an elliptical orbit
  }
  update(bhX, bhY) {
    this.angle += this.speed * 0.05
    
    // Attraction logic
    if (mouse.isDown && this.radius > 35) {
      this.radius -= (this.radius - 35) * 0.02
    } else {
      this.radius += (this.baseRadius - this.radius) * 0.01
    }

    const x = bhX + Math.cos(this.angle) * this.radius
    const y = bhY + Math.sin(this.angle) * this.radius * 0.35 // Squish Y for 3D disk effect

    // Fade out based on distance from center to blend seamlessly
    const distRatio = Math.max(0, 1 - (this.radius / this.baseRadius))
    
    ctx.fillStyle = this.color
    ctx.globalAlpha = distRatio * 0.8
    ctx.beginPath()
    ctx.arc(x, y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.globalAlpha = 1.0
  }
}

class Comet {
  constructor() {
    this.reset()
    this.active = false
  }
  reset() {
    this.x = Math.random() * w
    this.y = -50
    this.length = Math.random() * 150 + 60
    this.speed = Math.random() * 12 + 8
    this.angle = (Math.PI / 4) + (Math.random() * 0.4 - 0.2)
    this.active = true
    this.color = randomColor()
  }
  update() {
    if (!this.active) {
      if (Math.random() < 0.003) this.reset()
      return
    }

    this.x += Math.cos(this.angle) * this.speed
    this.y += Math.sin(this.angle) * this.speed

    const tailX = this.x - Math.cos(this.angle) * this.length
    const tailY = this.y - Math.sin(this.angle) * this.length

    const grad = ctx.createLinearGradient(this.x, this.y, tailX, tailY)
    grad.addColorStop(0, '#ffffff')
    grad.addColorStop(0.2, this.color)
    grad.addColorStop(1, this.color + '00')

    ctx.strokeStyle = grad
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(tailX, tailY)
    ctx.stroke()

    if (this.x > w + 200 || this.y > h + 200 || this.x < -200) {
      this.active = false
    }
  }
}

class Meteorite {
  constructor() {
    this.reset()
  }
  reset() {
    this.x = Math.random() > 0.5 ? -50 : w + 50
    this.y = Math.random() * h
    this.vx = (Math.random() * 1 + 0.2) * (this.x < 0 ? 1 : -1)
    this.vy = Math.random() * 1 - 0.5
    this.size = Math.random() * 3 + 1
    this.rotation = 0
    this.rotSpeed = (Math.random() - 0.5) * 0.1
    // Generate a simple irregular polygon
    this.points = []
    const numPoints = Math.floor(Math.random() * 3) + 4
    for(let i=0; i<numPoints; i++){
      const a = (i / numPoints) * Math.PI * 2
      const r = this.size + Math.random() * this.size
      this.points.push({ x: Math.cos(a)*r, y: Math.sin(a)*r })
    }
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    this.rotation += this.rotSpeed

    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.rotation)
    ctx.fillStyle = '#1e1b2e' // Dark rocky color
    ctx.strokeStyle = '#3d345b'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(this.points[0].x, this.points[0].y)
    for(let i=1; i<this.points.length; i++) {
        ctx.lineTo(this.points[i].x, this.points[i].y)
    }
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
    ctx.restore()

    if (this.x < -100 || this.x > w + 100 || this.y < -100 || this.y > h + 100) {
      if(Math.random() < 0.005) this.reset()
    }
  }
}

// ─── Drawing Black Hole ───
const drawBlackHole = (bx, by) => {
  blackHole.time += 0.01
  if (mouse.isDown) blackHole.shockwave = Math.min(blackHole.shockwave + 0.1, 1)
  else blackHole.shockwave = Math.max(blackHole.shockwave - 0.05, 0)

  ctx.save()
  ctx.translate(bx, by)

  // Accretion disk (slanted, rotating)
  ctx.save()
  ctx.scale(1, 0.35)
  ctx.rotate(blackHole.time)
  
  // Outer bright ring
  const diskGrad = ctx.createRadialGradient(0, 0, 30, 0, 0, 150 + (blackHole.shockwave * 50))
  diskGrad.addColorStop(0, 'rgba(255, 0, 127, 0.8)') // Bright Pink
  diskGrad.addColorStop(0.3, 'rgba(122, 40, 203, 0.5)') // Purple
  diskGrad.addColorStop(0.8, 'rgba(0, 210, 255, 0.1)') // Cyan edge
  diskGrad.addColorStop(1, 'rgba(0,0,0,0)')

  ctx.fillStyle = diskGrad
  // Use additive blending for the glow
  ctx.globalCompositeOperation = 'screen'
  ctx.beginPath()
  ctx.arc(0, 0, 150 + (blackHole.shockwave * 50), 0, Math.PI * 2)
  ctx.fill()
  
  // Inner hot ring
  ctx.strokeStyle = `rgba(0, 210, 255, ${0.8 + blackHole.shockwave * 0.2})`
  ctx.lineWidth = 3 + blackHole.shockwave * 2
  ctx.beginPath()
  ctx.arc(0, 0, 42, 0, Math.PI * 2)
  ctx.stroke()
  ctx.restore()

  // The Singularity (True black void)
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = '#020104'
  ctx.beginPath()
  ctx.arc(0, 0, 38, 0, Math.PI * 2)
  ctx.fill()

  // Event horizon glow edge
  ctx.strokeStyle = 'rgba(255, 0, 127, 0.4)'
  ctx.lineWidth = 1.5
  ctx.stroke()

  ctx.restore()
}

// ─── Initialization & Loop ───

const init = () => {
  w = Math.max(container.value?.offsetWidth || window.innerWidth, 500)
  h = Math.max(container.value?.offsetHeight || window.innerHeight, 500)
  if (canvas.value) {
    canvas.value.width = w
    canvas.value.height = h
  }
  
  if (blackHole.x === null) {
    blackHole.x = w / 2
    blackHole.y = h / 2
  }

  backgroundStars = []
  nebulas = []
  spiralDust = []
  comets = []
  meteorites = []

  const isMobile = window.innerWidth <= 768

  for (let i = 0; i < (isMobile ? 100 : 200); i++) backgroundStars.push(new StaticStar())
  for (let i = 0; i < (isMobile ? 3 : 5); i++) nebulas.push(new Nebula())
  for (let i = 0; i < (isMobile ? 200 : 400); i++) spiralDust.push(new SpiralDust())
  for (let i = 0; i < 4; i++) comets.push(new Comet())
  for (let i = 0; i < 5; i++) meteorites.push(new Meteorite())
}

const animate = () => {
  if (!isVisible || !canvas.value || !ctx) return
  animationFrameId = requestAnimationFrame(animate)

  // Clear background
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = C_BG
  ctx.fillRect(0, 0, w, h)

  // Draw Deep Space Entities
  ctx.globalCompositeOperation = 'screen' // Lightens underlying pixels
  nebulas.forEach(n => n.update())
  
  ctx.globalCompositeOperation = 'source-over'
  backgroundStars.forEach(s => s.update())
  meteorites.forEach(m => m.update())
  
  // Update Black Hole position (Eased follow)
  const targetX = mouse.x ?? w / 2
  let targetY = mouse.y ?? h / 2
  
  // On mobile or when mouse left, slowly drift around center
  if (mouse.x == null) {
      targetX = (w/2) + Math.sin(Date.now() * 0.0005) * 100
      targetY = (h/2) + Math.cos(Date.now() * 0.0003) * 50
  }

  blackHole.x += (targetX - blackHole.x) * 0.04
  blackHole.y += (targetY - blackHole.y) * 0.04

  // Draw Galactic Core / Accretion Dust
  ctx.globalCompositeOperation = 'screen'
  spiralDust.forEach(d => d.update(blackHole.x, blackHole.y))

  // Draw Space Objects
  comets.forEach(c => c.update())
  
  // Draw the Singularity overlay
  drawBlackHole(blackHole.x, blackHole.y)
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
  mouse.isDown = false
}

const onDown = () => { mouse.isDown = true }
const onUp = () => { mouse.isDown = false }

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
    if (isVisible && !animationFrameId) {
      animate()
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
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
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
  background-color: #05020a;
  pointer-events: auto;
  cursor: crosshair;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, transparent 0%, rgba(5, 2, 10, 0.6) 100%);
  pointer-events: none;
}
</style>
