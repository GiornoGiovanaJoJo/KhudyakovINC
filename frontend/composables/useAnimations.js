import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

// ─── Scroll Reveal (IntersectionObserver + MutationObserver) ──
export function useScrollReveal() {
  let intersectionObserver = null
  let mutationObserver = null
  const observed = new WeakSet()

  const observeElement = (el) => {
    if (el.classList.contains('reveal--visible')) return
    intersectionObserver.observe(el)
  }

  onMounted(() => {
    intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal--visible')
            intersectionObserver.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -30px 0px' }
    )

    // Observe existing elements
    document.querySelectorAll('.reveal').forEach(observeElement)

    // Watch for new .reveal elements added dynamically by Vue
    mutationObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType !== 1) continue
          if (node.classList?.contains('reveal')) observeElement(node)
          node.querySelectorAll?.('.reveal').forEach(observeElement)
        }
        // Restore attribute checking: when Vue toggles a class (like faq-item--open), 
        // it can overwrite the reveal--visible class. We need to re-add it.
        if (mutation.type === 'attributes' && mutation.target.classList?.contains('reveal')) {
          observeElement(mutation.target)
        }
      }
    })

    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'],
    })
  })

  onBeforeUnmount(() => {
    intersectionObserver?.disconnect()
    mutationObserver?.disconnect()
  })
}

// ─── Count Up Animation ──────────────────────────────────────
export function useCountUp(targetEl, endValue, duration = 2000, suffix = '') {
  const displayValue = ref('0' + suffix)
  let hasAnimated = false

  onMounted(() => {
    if (!targetEl.value) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            hasAnimated = true
            animateCount(0, endValue, duration, (val) => {
              displayValue.value = Math.floor(val) + suffix
            })
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.5 }
    )

    observer.observe(targetEl.value)
  })

  return displayValue
}

function animateCount(start, end, duration, callback) {
  const startTime = performance.now()

  function tick(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // easeOutExpo
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    callback(start + (end - start) * eased)
    if (progress < 1) requestAnimationFrame(tick)
  }

  requestAnimationFrame(tick)
}

// ─── 3D Tilt Effect ──────────────────────────────────────────
export function useTilt(el, maxDeg = 8) {
  const handleMouseMove = (e) => {
    const rect = el.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateX = ((y - centerY) / centerY) * -maxDeg
    const rotateY = ((x - centerX) / centerX) * maxDeg

    el.value.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
    el.value.style.transition = 'transform 0.1s ease'
  }

  const handleMouseLeave = () => {
    el.value.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale3d(1, 1, 1)'
    el.value.style.transition = 'transform 0.5s ease'
  }

  onMounted(() => {
    if (!el.value) return
    el.value.addEventListener('mousemove', handleMouseMove)
    el.value.addEventListener('mouseleave', handleMouseLeave)
  })

  onBeforeUnmount(() => {
    if (!el.value) return
    el.value.removeEventListener('mousemove', handleMouseMove)
    el.value.removeEventListener('mouseleave', handleMouseLeave)
  })
}

// ─── Typewriter Effect ───────────────────────────────────────
export function useTypewriter(words, typingSpeed = 80, deletingSpeed = 50, pauseDuration = 2000) {
  const displayText = ref('')
  const isDeleting = ref(false)
  let wordIndex = 0
  let charIndex = 0
  let timeoutId = null

  const type = () => {
    const currentWord = words[wordIndex]

    if (!isDeleting.value) {
      displayText.value = currentWord.substring(0, charIndex + 1)
      charIndex++

      if (charIndex === currentWord.length) {
        isDeleting.value = true
        timeoutId = setTimeout(type, pauseDuration)
        return
      }
    } else {
      displayText.value = currentWord.substring(0, charIndex - 1)
      charIndex--

      if (charIndex === 0) {
        isDeleting.value = false
        wordIndex = (wordIndex + 1) % words.length
      }
    }

    const speed = isDeleting.value ? deletingSpeed : typingSpeed
    timeoutId = setTimeout(type, speed)
  }

  onMounted(() => {
    timeoutId = setTimeout(type, 500)
  })

  onBeforeUnmount(() => {
    if (timeoutId) clearTimeout(timeoutId)
  })

  return { displayText, isDeleting }
}

// ─── Magnetic Button ─────────────────────────────────────────
export function useMagneticButton(el, strength = 0.3) {
  const handleMouseMove = (e) => {
    const rect = el.value.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2

    el.value.style.transform = `translate(${x * strength}px, ${y * strength}px)`
    el.value.style.transition = 'transform 0.2s ease'
  }

  const handleMouseLeave = () => {
    el.value.style.transform = 'translate(0, 0)'
    el.value.style.transition = 'transform 0.5s var(--ease-spring)'
  }

  onMounted(() => {
    if (!el.value) return
    el.value.addEventListener('mousemove', handleMouseMove)
    el.value.addEventListener('mouseleave', handleMouseLeave)
  })

  onBeforeUnmount(() => {
    if (!el.value) return
    el.value.removeEventListener('mousemove', handleMouseMove)
    el.value.removeEventListener('mouseleave', handleMouseLeave)
  })
}

// ─── Header Shrink on Scroll ─────────────────────────────────
export function useHeaderShrink() {
  const isScrolled = ref(false)

  const handleScroll = () => {
    isScrolled.value = window.scrollY > 50
  }

  onMounted(() => {
    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
  })

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', handleScroll)
  })

  return isScrolled
}

// ─── Scroll-to-top button visibility ─────────────────────────
export function useScrollToTop() {
  const showButton = ref(false)

  const handleScroll = () => {
    showButton.value = window.scrollY > 400
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  onMounted(() => {
    window.addEventListener('scroll', handleScroll, { passive: true })
  })

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', handleScroll)
  })

  return { showButton, scrollToTop }
}
