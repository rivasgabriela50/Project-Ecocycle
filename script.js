document.addEventListener('DOMContentLoaded', () => {
  const images = document.querySelectorAll('.carousel img');
  
  console.log('🔍 Verificando imágenes del carrusel...\n');
  
  images.forEach((img, index) => {
    // Crear un canvas para verificar si la imagen cargó correctamente
    const testImg = new Image();
    
    testImg.onload = () => {
      console.log(`✅ Imagen ${index + 1}: CARGADA CORRECTAMENTE`);
      console.log(`   - Src: ${img.src}`);
      console.log(`   - Tamaño: ${testImg.naturalWidth}x${testImg.naturalHeight}`);
    };
    
    testImg.onerror = () => {
      console.log(`❌ Imagen ${index + 1}: FALLO AL CARGAR`);
      console.log(`   - Src: ${img.src}`);
      console.log(`   - Reemplazando con placeholder...\n`);
      
      // Crear un canvas como placeholder
      const canvas = document.createElement('canvas');
      canvas.width = 650;
      canvas.height = 330;
      
      const ctx = canvas.getContext('2d');
      
      // Fondo degradado
      const gradient = ctx.createLinearGradient(0, 0, 650, 330);
      gradient.addColorStop(0, '#002ab6');
      gradient.addColorStop(1, '#00b4d8');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 650, 330);
      
      // Texto
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px Poppins, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`Imagen ${index + 1} no disponible`, 325, 150);
      ctx.font = '16px Poppins, sans-serif';
      ctx.fillText(`Archivo: ${img.src}`, 325, 190);
      ctx.fillText('Por favor, verifica la ruta del archivo', 325, 230);
      
      // Reemplazar src de la imagen con el canvas
      img.src = canvas.toDataURL();
      img.style.filter = 'grayscale(100%)';
    };
    
    testImg.src = img.src;
  });
});

// ===== CARRUSEL AUTOMÁTICO MEJORADO =====
class Carousel {
  constructor() {
    this.track = document.querySelector('.carousel-track');
    this.carousel = document.querySelector('.carousel');
    this.images = document.querySelectorAll('.carousel img');
    
    console.log('\n🎠 INICIANDO CARRUSEL');
    console.log(`📸 Imágenes detectadas: ${this.images.length}`);

    this.currentIndex = 0;
    this.autoPlayInterval = null;
    
    if (this.images.length === 0) {
      console.error('❌ No se encontraron imágenes en el carrusel!');
      return;
    }
    
    this.init();
  }

  init() {
    this.createIndicators();
    this.autoPlay();
    this.addEventListeners();
    console.log('✅ Carrusel inicializado correctamente\n');
  }

  createIndicators() {
    const existingIndicators = document.querySelector('.carousel-indicators');
    if (existingIndicators) {
      existingIndicators.remove();
    }

    const indicatorsContainer = document.createElement('div');
    indicatorsContainer.className = 'carousel-indicators';

    this.images.forEach((_, index) => {
      const dot = document.createElement('div');
      dot.className = 'carousel-dot';
      if (index === 0) dot.classList.add('active');
      
      dot.addEventListener('click', () => {
        this.goToSlide(index);
      });
      
      indicatorsContainer.appendChild(dot);
    });

    this.carousel.appendChild(indicatorsContainer);
  }

  goToSlide(index) {
    this.currentIndex = index;
    this.updateCarousel();
    this.updateIndicators();
    this.resetAutoPlay();
  }

  updateCarousel() {
    const offset = -this.currentIndex * 100;
    this.track.style.transform = `translateX(${offset}%)`;
  }

  updateIndicators() {
    document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
      dot.classList.toggle('active', index === this.currentIndex);
    });
  }

  nextSlide() {
    this.currentIndex = (this.currentIndex + 1) % this.images.length;
    this.updateCarousel();
    this.updateIndicators();
  }

  autoPlay() {
    this.autoPlayInterval = setInterval(() => this.nextSlide(), 6000);
  }

  resetAutoPlay() {
    clearInterval(this.autoPlayInterval);
    this.autoPlay();
  }

  addEventListeners() {
    this.carousel.addEventListener('mouseenter', () => {
      clearInterval(this.autoPlayInterval);
    });

    this.carousel.addEventListener('mouseleave', () => {
      this.autoPlay();
    });

    // Swipe
    let startX = 0;
    this.carousel.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });

    this.carousel.addEventListener('touchend', (e) => {
      const endX = e.changedTouches[0].clientX;
      if (startX - endX > 50) {
        this.nextSlide();
      } else if (endX - startX > 50) {
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.updateCarousel();
        this.updateIndicators();
      }
      this.resetAutoPlay();
    });

    // Teclado
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') this.nextSlide();
      if (e.key === 'ArrowLeft') {
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.updateCarousel();
        this.updateIndicators();
      }
    });
  }
}

// ===== ANIMACIÓN DE NÚMEROS =====
class CounterAnimation {
  constructor() {
    this.metrics = document.querySelectorAll('.metric .number');
    this.hasAnimated = false;
    this.init();
  }

  init() {
    window.addEventListener('scroll', () => this.checkVisibility());
  }

  checkVisibility() {
    if (this.hasAnimated) return;

    const metricsSection = document.querySelector('#metrics');
    if (!metricsSection) return;

    const rect = metricsSection.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.75) {
      this.animateCounters();
      this.hasAnimated = true;
    }
  }

  animateCounters() {
    this.metrics.forEach((metric) => {
      const target = parseInt(metric.getAttribute('data-target'));
      const duration = 2000;
      const increment = target / (duration / 50);
      let current = 0;

      const animate = () => {
        current += increment;
        if (current >= target) {
          metric.textContent = target;
        } else {
          metric.textContent = Math.floor(current);
          requestAnimationFrame(animate);
        }
      };

      animate();
    });
  }
}

// ===== PARALLAX =====
class HeroParallax {
  constructor() {
    this.hero = document.querySelector('.hero');
    this.init();
  }

  init() {
    window.addEventListener('scroll', () => this.updateParallax());
    window.addEventListener('mousemove', (e) => this.updateMouseParallax(e));
  }

  updateParallax() {
    if (!this.hero) return;
    const scrollY = window.scrollY;
    const overlay = this.hero.querySelector('.overlay');
    if (overlay) {
      overlay.style.transform = `translateY(${scrollY * 0.5}px)`;
    }
  }

  updateMouseParallax(e) {
    if (!this.hero || window.scrollY > window.innerHeight * 0.3) return;

    const x = (e.clientX / window.innerWidth) * 20 - 10;
    const y = (e.clientY / window.innerHeight) * 20 - 10;

    const content = this.hero.querySelector('.hero-content');
    if (content) {
      content.style.transform = `perspective(1000px) rotateX(${y * 0.1}deg) rotateY(${x * 0.1}deg)`;
    }
  }
}

// ===== SCROLL ANIMATIONS =====
class ScrollAnimations {
  constructor() {
    this.elements = document.querySelectorAll('.glass, .card, .metric');
    this.init();
  }

  init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'fadeInUp 1s ease-out forwards';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    this.elements.forEach((el) => observer.observe(el));
  }
}

// ===== GLOW EFFECT =====
class GlowEffect {
  constructor() {
    this.cards = document.querySelectorAll('.card, .metric');
    this.init();
  }

  init() {
    this.cards.forEach((card) => {
      card.addEventListener('mousemove', (e) => this.updateGlow(e, card));
      card.addEventListener('mouseleave', () => this.removeGlow(card));
    });
  }

  updateGlow(e, card) {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    card.style.background = `
      radial-gradient(circle at ${x}px ${y}px, 
        rgba(0, 217, 255, 0.15) 0%, 
        rgba(255, 255, 255, 0.8) 100%)
    `;
  }

  removeGlow(card) {
    card.style.background = '';
  }
}

// ===== NAVBAR ANIMATION =====
class NavbarAnimation {
  constructor() {
    this.navbar = document.querySelector('.navbar');
    this.init();
  }

  init() {
    window.addEventListener('scroll', () => this.updateNavbar());
  }

  updateNavbar() {
    if (window.scrollY > 50) {
      this.navbar.style.padding = '0.5rem 3rem';
      this.navbar.style.boxShadow = '0 12px 48px rgba(0, 180, 216, 0.2)';
    } else {
      this.navbar.style.padding = '1rem 3rem';
      this.navbar.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
    }
  }
}

// ===== SMOOTH SCROLL =====
class SmoothScroll {
  constructor() {
    this.links = document.querySelectorAll('a[href^="#"]');
    this.init();
  }

  init() {
    this.links.forEach((link) => {
      link.addEventListener('click', (e) => this.handleClick(e, link));
    });
  }

  handleClick(e, link) {
    const href = link.getAttribute('href');
    if (href === '#') return;

    const target = document.querySelector(href);
    if (!target) return;

    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// ===== INICIALIZAR TODO =====
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Inicializando Ecocycle...\n');

  new Carousel();
  new CounterAnimation();
  new HeroParallax();
  new ScrollAnimations();
  new GlowEffect();
  new NavbarAnimation();
  new SmoothScroll();

  console.log('\n✅ Ecocycle completamente cargado!');
});
// Manejo del botón "Probar prototipo"
document.addEventListener('DOMContentLoaded', () => {
  const btnPrototipo = document.getElementById('btnPrototipo');

  if (btnPrototipo) {
    btnPrototipo.addEventListener('click', () => {
      // Redirige a la página del prototipo
      window.location.href = 'ecostation-summary.html';
    });
  }
});