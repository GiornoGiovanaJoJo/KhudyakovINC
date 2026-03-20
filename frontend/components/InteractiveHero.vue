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
const mouse = { x: null, y: null, radius: 180 }
const trail = []
const MAX_TRAIL = 12

class Particle {
  constructor(x, y, size, baseColor, speedX, speedY, layer) {
    this.x = x
    this.y = y
    this.baseX = x
    this.baseY = y
    this.size = size
    this.baseSize = size
    this.baseColor = baseColor
    this.color = baseColor
    this.speedX = speedX
    this.speedY = speedY
    this.density = (Math.random() * 30) + 1
    this.layer = layer // 0 = far/dim, 1 = mid, 2 = near/bright
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

  update() {
    this.x += this.speedX * (0.5 + this.layer * 0.3)
    this.y += this.speedY * (0.5 + this.layer * 0.3)

    if (this.x < 0 || this.x > canvas.value.width) this.speedX = -this.speedX
    if (this.y < 0 || this.y > canvas.value.height) this.speedY = -this.speedY

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

        // Glow up near cursor
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
  const area = canvas.value.width * canvas.value.height
  const numberOfParticles = area / 7000

  for (let i = 0; i < numberOfParticles; i++) {
    const layer = Math.random() < 0.3 ? 0 : Math.random() < 0.6 ? 1 : 2
    const size = layer === 0 ? Math.random() * 1 + 0.3
              : layer === 1 ? Math.random() * 1.5 + 0.8
              : Math.random() * 2.5 + 1.2

    const x = Math.random() * canvas.value.width
    const y = Math.random() * canvas.value.height
    const speedX = (Math.random() * 0.6) - 0.3
    const speedY = (Math.random() * 0.6) - 0.3

    const colors = [
      'rgba(108, 92, 231, 0.8)',
      'rgba(162, 155, 254, 0.7)',
      'rgba(253, 121, 168, 0.6)',
      'rgba(0, 206, 201, 0.5)',
    ]
    const color = colors[Math.floor(Math.random() * colors.length)]

    particles.push(new Particle(x, y, size, color, speedX, speedY, layer))
  }
}

const drawCursorGlow = () => {
  if (mouse.x == null || mouse.y == null) return

  // Main glow
  const gradient = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 200)
  gradient.addColorStop(0, 'rgba(108, 92, 231, 0.12)')
  gradient.addColorStop(0.4, 'rgba(108, 92, 231, 0.05)')
  gradient.addColorStop(1, 'transparent')
  ctx.fillStyle = gradient
  ctx.fillRect(mouse.x - 200, mouse.y - 200, 400, 400)

  // Trail
  for (let i = 0; i < trail.length; i++) {
    const t = trail[i]
    const age = 1 - (i / trail.length)
    const r = 30 * age
    const tGrad = ctx.createRadialGradient(t.x, t.y, 0, t.x, t.y, r)
    tGrad.addColorStop(0, `rgba(162, 155, 254, ${0.08 * age})`)
    tGrad.addColorStop(1, 'transparent')
    ctx.fillStyle = tGrad
    ctx.fillRect(t.x - r, t.y - r, r * 2, r * 2)
  }
}

const connect = () => {
  for (let a = 0; a < particles.length; a++) {
    for (let b = a + 1; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x
      const dy = particles[a].y - particles[b].y
      const distance = dx * dx + dy * dy
      const maxDist = (canvas.value.width / 8) * (canvas.value.height / 8)
      if (distance < maxDist) {
        let opacity = 1 - (distance / maxDist)

        // Brighter connections near cursor
        if (mouse.x != null && mouse.y != null) {
          const midX = (particles[a].x + particles[b].x) / 2
          const midY = (particles[a].y + particles[b].y) / 2
          const cursorDist = Math.sqrt((mouse.x - midX) ** 2 + (mouse.y - midY) ** 2)
          if (cursorDist < mouse.radius) {
            opacity *= 1 + (1 - cursorDist / mouse.radius) * 2
          }
        }

        ctx.strokeStyle = `rgba(140, 150, 255, ${opacity * 0.12})`
        ctx.lineWidth = 0.6
        ctx.beginPath()
        ctx.moveTo(particles[a].x, particles[a].y)
        ctx.lineTo(particles[b].x, particles[b].y)
        ctx.stroke()
      }
    }
  }
}

const animate = () => {
  animationFrameId = requestAnimationFrame(animate)
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)

  drawCursorGlow()

  for (let i = 0; i < particles.length; i++) {
    particles[i].update()
  }
  connect()
}

const handleResize = () => {
  canvas.value.width = container.value.offsetWidth
  canvas.value.height = container.value.offsetHeight
  init()
}

const handleMouseMove = (event) => {
  const rect = canvas.value.getBoundingClientRect()
  mouse.x = event.clientX - rect.left
  mouse.y = event.clientY - rect.top

  trail.unshift({ x: mouse.x, y: mouse.y })
  if (trail.length > MAX_TRAIL) trail.pop()
}

const handleMouseLeave = () => {
  mouse.x = null
  mouse.y = null
  trail.length = 0
}

onMounted(() => {
  ctx = canvas.value.getContext('2d')
  canvas.value.width = container.value.offsetWidth
  canvas.value.height = container.value.offsetHeight

  window.addEventListener('resize', handleResize)
  canvas.value.addEventListener('mousemove', handleMouseMove)
  canvas.value.addEventListener('mouseleave', handleMouseLeave)

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

