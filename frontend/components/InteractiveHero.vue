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

class Particle {
  constructor(x, y, size, color, speedX, speedY) {
    this.x = x
    this.y = y
    this.baseX = x
    this.baseY = y
    this.size = size
    this.color = color
    this.speedX = speedX
    this.speedY = speedY
    this.density = (Math.random() * 30) + 1
  }

  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
  }

  update() {
    // Normal floating movement
    this.x += this.speedX
    this.y += this.speedY

    // Bounce off edges
    if (this.x < 0 || this.x > canvas.value.width) this.speedX = -this.speedX
    if (this.y < 0 || this.y > canvas.value.height) this.speedY = -this.speedY

    // Mouse interaction
    if (mouse.x != null && mouse.y != null) {
      const dx = mouse.x - this.x
      const dy = mouse.y - this.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      const forceDirectionX = dx / distance
      const forceDirectionY = dy / distance
      
      const maxDistance = mouse.radius
      const force = (maxDistance - distance) / maxDistance

      const directionX = forceDirectionX * force * this.density
      const directionY = forceDirectionY * force * this.density

      if (distance < mouse.radius) {
        this.x -= directionX
        this.y -= directionY
      }
    }

    this.draw()
  }
}

const init = () => {
  particles = []
  const numberOfParticles = (canvas.value.width * canvas.value.height) / 9000
  for (let i = 0; i < numberOfParticles; i++) {
    const size = (Math.random() * 2) + 0.5
    const x = (Math.random() * (canvas.value.width - size * 2) + size)
    const y = (Math.random() * (canvas.value.height - size * 2) + size)
    const speedX = (Math.random() * 0.8) - 0.4
    const speedY = (Math.random() * 0.8) - 0.4
    const color = Math.random() > 0.5 ? 'rgba(99, 102, 241, 0.8)' : 'rgba(236, 72, 153, 0.8)'
    
    particles.push(new Particle(x, y, size, color, speedX, speedY))
  }
}

const connect = () => {
  for (let a = 0; a < particles.length; a++) {
    for (let b = a; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x
      const dy = particles[a].y - particles[b].y
      const distance = dx * dx + dy * dy
      if (distance < (canvas.value.width / 7) * (canvas.value.height / 7)) {
        let opacityValue = 1 - (distance / 10000)
        ctx.strokeStyle = `rgba(140, 150, 255, ${opacityValue * 0.15})`
        ctx.lineWidth = 1
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
}

const handleMouseLeave = () => {
  mouse.x = null
  mouse.y = null
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
