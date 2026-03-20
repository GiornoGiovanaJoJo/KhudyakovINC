<template>
  <div class="interactive-hero" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const container = ref(null)
const canvas = ref(null)
let ctx = null
let animationFrameId = null
let particles = []
const mouse = { x: null, y: null, radius: 120 }
let isVisible = true

// ─── Spatial Grid for O(n) connection lookups ────────
const CELL_SIZE = 120
let grid = {}

function getCellKey(x, y) {
  return `${Math.floor(x / CELL_SIZE)},${Math.floor(y / CELL_SIZE)}`
}

function buildGrid() {
  grid = {}
  for (let i = 0; i < particles.length; i++) {
    const key = getCellKey(particles[i].x, particles[i].y)
    if (!grid[key]) grid[key] = []
    grid[key].push(i)
  }
}

function getNeighborKeys(cx, cy) {
  const keys = []
  for (let dx = -1; dx <= 1; dx++) {
    for (let dy = -1; dy <= 1; dy++) {
      keys.push(`${cx + dx},${cy + dy}`)
    }
  }
  return keys
}

class Particle {
  constructor(x, y, size, baseColor, speedX, speedY, layer) {
    this.x = x
    this.y = y
    this.size = size
    this.baseSize = size
    this.baseColor = baseColor
    this.color = baseColor
    this.speedX = speedX
    this.speedY = speedY
    this.density = (Math.random() * 30) + 1
    this.layer = layer
    this.alpha = layer === 0 ? 0.3 : layer === 1 ? 0.6 : 0.9
    this.baseAlpha = this.alpha
  }

  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.globalAlpha = this.alpha
    ctx.fill()
    ctx.globalAlpha = 1
  }

  update(w, h) {
    this.x += this.speedX * (0.5 + this.layer * 0.3)
    this.y += this.speedY * (0.5 + this.layer * 0.3)

    if (this.x < 0 || this.x > w) this.speedX = -this.speedX
    if (this.y < 0 || this.y > h) this.speedY = -this.speedY

    if (mouse.x != null && mouse.y != null) {
      const dx = mouse.x - this.x
      const dy = mouse.y - this.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < mouse.radius) {
        const force = (mouse.radius - distance) / mouse.radius
        const forceDirectionX = dx / distance
        const forceDirectionY = dy / distance

        this.x -= forceDirectionX * force * this.density * 0.6
        this.y -= forceDirectionY * force * this.density * 0.6

        this.size = this.baseSize + force * 2
        this.alpha = Math.min(1, this.baseAlpha + force * 0.5)
        this.color = `rgba(162, 155, 254, ${0.6 + force * 0.4})`
      } else {
        this.size += (this.baseSize - this.size) * 0.05
        this.alpha += (this.baseAlpha - this.alpha) * 0.05
        this.color = this.baseColor
      }
    } else {
      this.size += (this.baseSize - this.size) * 0.05
      this.alpha += (this.baseAlpha - this.alpha) * 0.05
      this.color = this.baseColor
    }

    this.draw()
  }
}

const init = () => {
  particles = []
  const w = canvas.value.width
  const h = canvas.value.height
  // Reduced density: was /7000, now /12000
  const numberOfParticles = Math.min((w * h) / 12000, 200)

  const colors = [
    'rgba(108, 92, 231, 0.8)',
    'rgba(162, 155, 254, 0.7)',
    'rgba(253, 121, 168, 0.6)',
    'rgba(0, 206, 201, 0.5)',
  ]

  for (let i = 0; i < numberOfParticles; i++) {
    const layer = Math.random() < 0.3 ? 0 : Math.random() < 0.6 ? 1 : 2
    const size = layer === 0 ? Math.random() * 1 + 0.3
              : layer === 1 ? Math.random() * 1.5 + 0.8
              : Math.random() * 2.5 + 1.2

    particles.push(new Particle(
      Math.random() * w,
      Math.random() * h,
      size,
      colors[Math.floor(Math.random() * colors.length)],
      (Math.random() * 0.6) - 0.3,
      (Math.random() * 0.6) - 0.3,
      layer
    ))
  }
}

const drawCursorGlow = () => {
  if (mouse.x == null || mouse.y == null) return
  const gradient = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 180)
  gradient.addColorStop(0, 'rgba(108, 92, 231, 0.12)')
  gradient.addColorStop(0.4, 'rgba(108, 92, 231, 0.05)')
  gradient.addColorStop(1, 'transparent')
  ctx.fillStyle = gradient
  ctx.fillRect(mouse.x - 180, mouse.y - 180, 360, 360)
}

const connect = () => {
  // Build spatial grid once per frame
  buildGrid()

  const maxDistSq = CELL_SIZE * CELL_SIZE
  const checked = new Set()

  for (let i = 0; i < particles.length; i++) {
    const p = particles[i]
    const cx = Math.floor(p.x / CELL_SIZE)
    const cy = Math.floor(p.y / CELL_SIZE)
    const neighborKeys = getNeighborKeys(cx, cy)

    for (const key of neighborKeys) {
      const cell = grid[key]
      if (!cell) continue

      for (const j of cell) {
        if (j <= i) continue
        const pairKey = i * 10000 + j
        if (checked.has(pairKey)) continue
        checked.add(pairKey)

        const dx = p.x - particles[j].x
        const dy = p.y - particles[j].y
        const distSq = dx * dx + dy * dy

        if (distSq < maxDistSq) {
          let opacity = 1 - (distSq / maxDistSq)

          if (mouse.x != null && mouse.y != null) {
            const midX = (p.x + particles[j].x) / 2
            const midY = (p.y + particles[j].y) / 2
            const cursorDist = Math.sqrt((mouse.x - midX) ** 2 + (mouse.y - midY) ** 2)
            if (cursorDist < mouse.radius) {
              opacity *= 1 + (1 - cursorDist / mouse.radius) * 2
            }
          }

          ctx.strokeStyle = `rgba(140, 150, 255, ${opacity * 0.12})`
          ctx.lineWidth = 0.6
          ctx.beginPath()
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.stroke()
        }
      }
    }
  }
}

const animate = () => {
  if (!isVisible || !canvas.value) return
  animationFrameId = requestAnimationFrame(animate)

  const w = canvas.value.width
  const h = canvas.value.height
  ctx.clearRect(0, 0, w, h)

  drawCursorGlow()

  for (let i = 0; i < particles.length; i++) {
    particles[i].update(w, h)
  }
  connect()
}

let resizeTimeout = null
const handleResize = () => {
  // Debounce resize to avoid thrashing
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    if (!canvas.value || !container.value) return
    canvas.value.width = container.value.offsetWidth
    canvas.value.height = container.value.offsetHeight
    init()
  }, 150)
}

let mouseMoveQueued = false
const handleMouseMove = (event) => {
  if (mouseMoveQueued) return
  mouseMoveQueued = true
  requestAnimationFrame(() => {
    if (!canvas.value) return
    const rect = canvas.value.getBoundingClientRect()
    mouse.x = event.clientX - rect.left
    mouse.y = event.clientY - rect.top
    mouseMoveQueued = false
  })
}

const handleMouseLeave = () => {
  mouse.x = null
  mouse.y = null
}

// Pause animation when not in viewport
let visibilityObserver = null

onMounted(() => {
  ctx = canvas.value.getContext('2d')
  canvas.value.width = container.value.offsetWidth
  canvas.value.height = container.value.offsetHeight

  window.addEventListener('resize', handleResize, { passive: true })
  canvas.value.addEventListener('mousemove', handleMouseMove, { passive: true })
  canvas.value.addEventListener('mouseleave', handleMouseLeave)

  // Only animate when hero is visible
  visibilityObserver = new IntersectionObserver((entries) => {
    isVisible = entries[0].isIntersecting
    if (isVisible && !animationFrameId) {
      animate()
    }
  }, { threshold: 0 })
  visibilityObserver.observe(container.value)

  init()
  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (canvas.value) {
    canvas.value.removeEventListener('mousemove', handleMouseMove)
    canvas.value.removeEventListener('mouseleave', handleMouseLeave)
  }
  cancelAnimationFrame(animationFrameId)
  animationFrameId = null
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
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
</style>
