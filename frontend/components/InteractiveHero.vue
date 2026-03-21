<template>
  <div class="interactive-hero" ref="container" @mousedown="onDown" @mouseup="onUp" @touchstart.passive="onDown" @touchend.passive="onUp">
    <canvas ref="canvas"></canvas>
    <!-- Dark overlay to ensure text remains readable over the bright effects -->
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
const C_BG = '#030108' // Deep dark space
const COLORS = ['#00d2ff', '#7a28cb', '#ff007f', '#a29bfe', '#00cec9', '#fd79a8']

const mouse = { x: null, y: null, isDown: false }
const blackHole = { x: null, y: null, time: 0, gravityActive: false }

// Space Entities
let stars = []
let nebulas = []
let galacticDust = []
let comets = []
let meteorites = []
let shockwaves = []
let explosions = []

// ─── Utility ───
const randomColor = () => COLORS[Math.floor(Math.random() * COLORS.length)]

// ─── Classes ───

class Nebula {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.radius = Math.random() * 600 + 400
    this.color = randomColor()
    this.vx = (Math.random() - 0.5) * 0.1
    this.vy = (Math.random() - 0.5) * 0.1
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    
    // Wrap around screen
    if (this.x < -this.radius) this.x = w + this.radius
    if (this.x > w + this.radius) this.x = -this.radius
    if (this.y < -this.radius) this.y = h + this.radius
    if (this.y > h + this.radius) this.y = -this.radius

    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius)
    // Very subtle, rich deep space clouds
    grad.addColorStop(0, this.color + '0C') // ~5% opacity
    grad.addColorStop(1, this.color + '00')
    
    ctx.globalCompositeOperation = 'screen'
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

class Star {
  constructor() {
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.size = Math.random() * 1.5 + 0.2
    this.baseAlpha = Math.random() * 0.4 + 0.1
    this.blinkAngle = Math.random() * Math.PI * 2
    this.blinkSpeed = Math.random() * 0.02 + 0.005
    this.color = Math.random() > 0.8 ? randomColor() : '#ffffff'
  }
  update() {
    this.blinkAngle += this.blinkSpeed
    const alpha = this.baseAlpha + Math.sin(this.blinkAngle) * 0.3
    if (alpha <= 0) return
    
    ctx.globalCompositeOperation = 'screen'
    ctx.fillStyle = this.color
    ctx.globalAlpha = Math.min(1, alpha)
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.globalAlpha = 1.0
  }
}

class GalacticDust {
  constructor() {
    this.reset()
  }
  reset() {
    // Distribute around screen, occasionally forming clusters
    this.x = Math.random() * window.innerWidth
    this.y = Math.random() * window.innerHeight
    this.size = Math.random() * 2 + 0.5
    this.color = randomColor()
    this.vx = (Math.random() - 0.5) * 0.5
    this.vy = (Math.random() - 0.5) * 0.5
    this.orbitAngle = Math.atan2(this.y - window.innerHeight/2, this.x - window.innerWidth/2)
  }
  update(bhX, bhY) {
    const dx = bhX - this.x
    const dy = bhY - this.y
    const dist = Math.sqrt(dx*dx + dy*dy)
    
    if (mouse.isDown) {
      // SUCKED INTO BLACK HOLE
      const pull = Math.max(0.1, 2000 / (dist * dist))
      this.vx += (dx / dist) * pull * 2
      this.vy += (dy / dist) * pull * 2
      // Add spiral effect
      this.vx += (dy / dist) * 2
      this.vy -= (dx / dist) * 2
    } else if (dist < 500 && mouse.x != null) {
      // Gentle attraction to black hole
      this.vx += (dx / dist) * 0.02
      this.vy += (dy / dist) * 0.02
    } else {
      // Natural slow drift
      const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy)
      if (speed > 1) {
        this.vx *= 0.95
        this.vy *= 0.95
      }
    }

    this.x += this.vx
    this.y += this.vy

    // Draw
    ctx.globalCompositeOperation = 'screen'
    ctx.fillStyle = this.color
    
    // Fade out as it gets super close to singularity to simulate falling past event horizon
    const alpha = dist < 40 ? Math.max(0, dist / 40) : 1
    ctx.globalAlpha = alpha
    
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.globalAlpha = 1.0

    // Respawn if sucked in completely or drifted way off screen
    if (dist < 10 || this.x < -100 || this.x > w + 100 || this.y < -100 || this.y > h + 100) {
      this.reset()
      // If sucked in, spawn at edge to maintain galaxy density
      if (dist < 10) {
        const angle = Math.random() * Math.PI * 2
        this.x = bhX + Math.cos(angle) * (w > h ? w : h) // Spawn far away
        this.y = bhY + Math.sin(angle) * (w > h ? w : h)
      }
    }
  }
}

class Shockwave {
  constructor(x, y) {
    this.x = x
    this.y = y
    this.radius = 10
    this.life = 1.0
    this.speed = 40
  }
  update() {
    this.radius += this.speed
    this.speed *= 0.95 // Exponential slowdown
    this.life -= 0.015

    ctx.globalCompositeOperation = 'screen'
    ctx.save()
    
    // Outer expanding ring (Cyan/White)
    ctx.strokeStyle = `rgba(0, 210, 255, ${Math.max(0, this.life)})`
    ctx.lineWidth = 10 * this.life
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2)
    ctx.stroke()
    
    // Inner secondary ring (Pink)
    ctx.strokeStyle = `rgba(255, 0, 127, ${Math.max(0, this.life * 0.7)})`
    ctx.lineWidth = 5 * this.life
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius * 0.8, 0, Math.PI*2)
    ctx.stroke()

    // Central flash
    const flashGrad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius)
    flashGrad.addColorStop(0, `rgba(255, 255, 255, ${Math.max(0, this.life * 0.8)})`)
    flashGrad.addColorStop(0.3, `rgba(255, 0, 127, ${Math.max(0, this.life * 0.4)})`)
    flashGrad.addColorStop(1, 'rgba(0, 0, 0, 0)')
    ctx.fillStyle = flashGrad
    ctx.fillRect(this.x - this.radius, this.y - this.radius, this.radius * 2, this.radius * 2)

    ctx.restore()
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
    this.length = Math.random() * 200 + 100
    this.speed = Math.random() * 18 + 12
    this.angle = (Math.PI / 4) + (Math.random() * 0.3 - 0.15)
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
    grad.addColorStop(0.1, this.color)
    grad.addColorStop(1, this.color + '00')

    ctx.globalCompositeOperation = 'screen'
    ctx.strokeStyle = grad
    ctx.lineWidth = 3
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(this.x, this.y)
    ctx.lineTo(tailX, tailY)
    ctx.stroke()

    if (this.x > w + 300 || this.y > h + 300 || this.x < -300) {
      this.active = false
    }
  }
}

class Meteorite {
  constructor() {
    this.reset()
  }
  reset() {
    this.x = Math.random() > 0.5 ? -100 : w + 100
    this.y = Math.random() * h
    this.vx = (Math.random() * 2 + 0.5) * (this.x < 0 ? 1 : -1)
    this.vy = Math.random() * 2 - 1
    this.size = Math.random() * 4 + 2
    this.rotation = 0
    this.rotSpeed = (Math.random() - 0.5) * 0.05
    
    this.points = []
    const numPoints = Math.floor(Math.random() * 4) + 5
    for(let i=0; i<numPoints; i++){
      const a = (i / numPoints) * Math.PI * 2
      const r = this.size + Math.random() * this.size
      this.points.push({ x: Math.cos(a)*r, y: Math.sin(a)*r })
    }
  }
  update(bhX, bhY) {
    // Sucked into black hole if mousedown
    if (mouse.isDown) {
      const dx = bhX - this.x
      const dy = bhY - this.y
      const dist = Math.sqrt(dx*dx + dy*dy)
      const pull = Math.max(0, 1000 / (dist * dist))
      this.vx += (dx / dist) * pull
      this.vy += (dy / dist) * pull
    }

    this.x += this.vx
    this.y += this.vy
    this.rotation += this.rotSpeed

    ctx.globalCompositeOperation = 'source-over'
    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.rotation)
    ctx.fillStyle = '#110f1a' // Deep dark rock
    ctx.strokeStyle = '#3d345b' // Purple glowing edge
    ctx.lineWidth = 1.5
    ctx.shadowBlur = 10
    ctx.shadowColor = '#6c5ce7' // Neon purple drop shadow
    
    ctx.beginPath()
    ctx.moveTo(this.points[0].x, this.points[0].y)
    for(let i=1; i<this.points.length; i++) {
        ctx.lineTo(this.points[i].x, this.points[i].y)
    }
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
    ctx.restore()

    if (this.x < -150 || this.x > w + 150 || this.y < -150 || this.y > h + 150) {
      if(Math.random() < 0.005) this.reset()
    }
  }
}

// ─── Drawing Interstellar-style Gargantua Black Hole ───
const drawBlackHole = (x, y) => {
  blackHole.time += 0.015
  const r = window.innerWidth > 768 ? 65 : 45 // Event horizon radius

  ctx.save()
  ctx.translate(x, y)
  
  // Gravitational Lensing Halo (The curved ring behind and over the top)
  ctx.save()
  ctx.scale(1, 0.45)
  ctx.translate(0, -r * 1.6) // Shifted up
  // Slowly wobble the back ring to make it feel alive
  ctx.rotate(Math.sin(blackHole.time) * 0.1)
  
  const backHalo = ctx.createRadialGradient(0, 0, r*0.5, 0, 0, r*4)
  backHalo.addColorStop(0, 'rgba(255, 255, 255, 0.9)') // White hot core
  backHalo.addColorStop(0.15, 'rgba(255, 0, 127, 0.7)') // Pink intense
  backHalo.addColorStop(0.4, 'rgba(122, 40, 203, 0.4)') // Deep purple
  backHalo.addColorStop(1, 'rgba(0, 0, 0, 0)') // Fade to unseen
  
  ctx.globalCompositeOperation = 'screen'
  ctx.fillStyle = backHalo
  ctx.beginPath()
  ctx.arc(0, 0, r*4.5, 0, Math.PI*2)
  ctx.fill()
  ctx.restore()

  // Full Accretion Disk Glow Background
  ctx.save()
  ctx.scale(1, 0.25)
  ctx.rotate(-blackHole.time * 0.5) // Rotate the gas disk
  
  const diskBg = ctx.createRadialGradient(0, 0, r*1.2, 0, 0, r*6)
  diskBg.addColorStop(0, 'rgba(0, 210, 255, 0.8)') // Cyan inner edge
  diskBg.addColorStop(0.3, 'rgba(255, 0, 127, 0.5)') // Pink middle
  diskBg.addColorStop(0.7, 'rgba(122, 40, 203, 0.2)') // Purple outer
  diskBg.addColorStop(1, 'rgba(0,0,0,0)')
  
  ctx.fillStyle = diskBg
  ctx.beginPath()
  ctx.arc(0, 0, r*6, 0, Math.PI*2)
  ctx.fill()
  ctx.restore()

  // Event Horizon (True Pitch Black Void)
  ctx.globalCompositeOperation = 'source-over'
  ctx.beginPath()
  ctx.arc(0, 0, r, 0, Math.PI*2)
  ctx.fillStyle = '#010002' // Absolute dark
  ctx.fill()

  // Photon Sphere (Intense glowing edge around the black hole)
  ctx.lineWidth = 2
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.stroke()
  ctx.lineWidth = 6
  ctx.strokeStyle = 'rgba(0, 210, 255, 0.4)'
  ctx.stroke()
  ctx.lineWidth = 12
  ctx.strokeStyle = 'rgba(255, 0, 127, 0.15)'
  ctx.stroke()

  // Foreground Accretion Disk (Passes IN FRONT of the black hole)
  ctx.save()
  ctx.globalCompositeOperation = 'screen'
  ctx.scale(1, 0.25)
  ctx.rotate(-blackHole.time * 0.5)
  
  const frontDisk = ctx.createRadialGradient(0, 0, r*1.2, 0, 0, r*5.5)
  frontDisk.addColorStop(0, 'rgba(0,0,0,0)')
  frontDisk.addColorStop(0.15, 'rgba(255, 255, 255, 1)')
  frontDisk.addColorStop(0.3, 'rgba(0, 210, 255, 0.8)')
  frontDisk.addColorStop(0.6, 'rgba(122, 40, 203, 0.5)')
  frontDisk.addColorStop(1, 'rgba(0,0,0,0)')
  
  ctx.fillStyle = frontDisk
  ctx.beginPath()
  // Draw only the bottom half of the circle so it overlaps the bottom of the black spherical void
  ctx.arc(0, 0, r*5.5, -0.1, Math.PI + 0.1) 
  ctx.fill()
  ctx.restore()

  // Add a subtle suction distortion field if mouse is held down
  if (mouse.isDown) {
    ctx.save()
    ctx.scale(1, 0.25)
    ctx.rotate(blackHole.time * 2) // Fast spin
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)'
    ctx.lineWidth = 1
    for (let i = 0; i < 5; i++) {
        ctx.beginPath()
        ctx.arc(0, 0, r*2 + (Math.sin(blackHole.time*5 + i) * 20), 0, Math.PI)
        ctx.stroke()
    }
    ctx.restore()
  }

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

  stars = []
  nebulas = []
  galacticDust = []
  comets = []
  meteorites = []
  shockwaves = []

  const isMobile = window.innerWidth <= 768

  for (let i = 0; i < (isMobile ? 120 : 250); i++) stars.push(new Star())
  for (let i = 0; i < (isMobile ? 4 : 7); i++) nebulas.push(new Nebula())
  for (let i = 0; i < (isMobile ? 250 : 500); i++) galacticDust.push(new GalacticDust())
  for (let i = 0; i < 4; i++) comets.push(new Comet())
  for (let i = 0; i < (isMobile ? 4 : 8); i++) meteorites.push(new Meteorite())
}

const animate = () => {
  if (!isVisible || !canvas.value || !ctx) return
  animationFrameId = requestAnimationFrame(animate)

  // Motion blur fading for dark space
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = 'rgba(3, 1, 8, 0.35)' // Deep space smear
  ctx.fillRect(0, 0, w, h)

  // Draw Nebulas
  nebulas.forEach(n => n.update())
  
  // Draw Stars & Meteorites
  stars.forEach(s => s.update())
  meteorites.forEach(m => m.update(blackHole.x, blackHole.y))
  
  // Update Black Hole target position (smooth follow)
  let targetX = mouse.x ?? w / 2
  let targetY = mouse.y ?? h / 2
  
  // If mouse never moved or left bounds, slowly drift center
  if (mouse.x == null) {
      targetX = (w/2) + Math.sin(Date.now() * 0.0004) * 150
      targetY = (h/2) + Math.cos(Date.now() * 0.0002) * 80
  }

  blackHole.x += (targetX - blackHole.x) * (mouse.isDown ? 0.05 : 0.03)
  blackHole.y += (targetY - blackHole.y) * (mouse.isDown ? 0.05 : 0.03)

  // Draw Gargantua Black Hole 
  drawBlackHole(blackHole.x, blackHole.y)

  // Draw dust getting pulled or orbiting
  galacticDust.forEach(d => d.update(blackHole.x, blackHole.y))

  // Draw Comets
  comets.forEach(c => c.update())
  
  // Draw Supernova Shockwaves
  for (let i = shockwaves.length - 1; i >= 0; i--) {
    shockwaves[i].update()
    if (shockwaves[i].life <= 0) {
      shockwaves.splice(i, 1)
    }
  }
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
const onUp = () => { 
  if (mouse.isDown) { // Prevent triggering if just mouseup without mousedown recently
    // Initiate Supernova Shockwave
    shockwaves.push(new Shockwave(blackHole.x, blackHole.y))
    // Scatter the dust violently
    galacticDust.forEach(d => {
      d.vx += (Math.random() - 0.5) * 50
      d.vy += (Math.random() - 0.5) * 50
    })
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
  background-color: #030108;
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
  background: radial-gradient(circle at center, transparent 0%, rgba(3, 1, 8, 0.7) 100%);
  pointer-events: none;
}
</style>
