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
const mouse = { x: null, y: null, radius: 150 }
let isVisible = true
let w, h

// We use a much simpler particle system without n^2 connections for maximum performance.
// Instead of drawing lines between all particles, we let particles react to the mouse
// and draw a soft glow around the mouse itself.

class Particle {
  constructor(x, y) {
    this.x = x
    this.y = y
    this.baseX = x
    this.baseY = y
    this.size = Math.random() * 2 + 0.5
    this.baseSize = this.size
    
    // Assign colors based on depth layer
    const layer = Math.random()
    if (layer < 0.3) {
      this.color = 'rgba(108, 92, 231, 0.4)' // Purple deep
      this.speed = Math.random() * 0.2 + 0.1
    } else if (layer < 0.7) {
      this.color = 'rgba(0, 206, 201, 0.6)' // Cyan mid
      this.speed = Math.random() * 0.4 + 0.2
    } else {
      this.color = 'rgba(162, 155, 254, 0.8)' // Light purple front
      this.speed = Math.random() * 0.6 + 0.3
    }

    this.angle = Math.random() * Math.PI * 2
    this.vx = Math.cos(this.angle) * this.speed
    this.vy = Math.sin(this.angle) * this.speed
    // Random drift factor
    this.drift = Math.random() * 0.05
  }

  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
  }

  update() {
    // Basic movement
    this.x += this.vx
    this.y += this.vy
    
    // Slow drift drift
    this.angle += this.drift
    this.vx = Math.cos(this.angle) * this.speed
    this.vy = Math.sin(this.angle) * this.speed

    // Wrap around screen
    if (this.x < 0) this.x = w
    if (this.x > w) this.x = 0
    if (this.y < 0) this.y = h
    if (this.y > h) this.y = 0

    // Mouse interaction
    if (mouse.x != null && mouse.y != null) {
      const dx = mouse.x - this.x
      const dy = mouse.y - this.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < mouse.radius) {
        // Particles flee from the mouse
        const force = (mouse.radius - distance) / mouse.radius
        const forceDirectionX = dx / distance
        const forceDirectionY = dy / distance

        this.x -= forceDirectionX * force * 3
        this.y -= forceDirectionY * force * 3
        
        // Glow slightly when near mouse
        this.size = this.baseSize + force * 2
      } else {
        // Return to normal size
        this.size += (this.baseSize - this.size) * 0.1
      }
    } else {
      this.size += (this.baseSize - this.size) * 0.1
    }

    this.draw()
  }
}

const init = () => {
  particles = []
  w = canvas.value.width = container.value.offsetWidth
  h = canvas.value.height = container.value.offsetHeight
  
  // Calculate particle count based on screen area, but cap it for performance
  // 1 particle per 10,000 pixels is performant without lines
  const numberOfParticles = Math.min((w * h) / 10000, 300)

  for (let i = 0; i < numberOfParticles; i++) {
    particles.push(new Particle(Math.random() * w, Math.random() * h))
  }
}

const drawAmbientCursor = () => {
  if (mouse.x == null || mouse.y == null) return
  
  const radgrad = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, mouse.radius * 1.5)
  // Brighter glow to match the original style
  radgrad.addColorStop(0, 'rgba(108, 92, 231, 0.15)')
  radgrad.addColorStop(0.5, 'rgba(108, 92, 231, 0.05)')
  radgrad.addColorStop(1, 'rgba(108, 92, 231, 0)')
  
  ctx.fillStyle = radgrad
  ctx.fillRect(mouse.x - mouse.radius * 1.5, mouse.y - mouse.radius * 1.5, mouse.radius * 3, mouse.radius * 3)
}

const animate = () => {
  if (!isVisible || !canvas.value) return
  animationFrameId = requestAnimationFrame(animate)

  // Clear canvas First
  ctx.clearRect(0, 0, w, h)

  drawAmbientCursor()

  for (let i = 0; i < particles.length; i++) {
    particles[i].update()
  }
}

let resizeTimeout = null
const handleResize = () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    if (!canvas.value || !container.value) return
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

let visibilityObserver = null

onMounted(() => {
  ctx = canvas.value.getContext('2d', { alpha: true }) // Optimize for transparent background
  
  window.addEventListener('resize', handleResize, { passive: true })
  canvas.value.addEventListener('mousemove', handleMouseMove, { passive: true })
  canvas.value.addEventListener('mouseleave', handleMouseLeave)

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
  pointer-events: auto; /* Ensure it captures mouse events */
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
