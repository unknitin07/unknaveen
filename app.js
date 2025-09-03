// Application Data
const applicationData = {
  "developer": {
    "name": "Unk Naveen",
    "title": "Full Stack Developer",
    "tagline": "Creating seamless digital experiences with modern technology",
    "bio": "Passionate developer specializing in mobile applications and modern web technologies. I create efficient, scalable solutions that combine functionality with exceptional user experience.",
    "location": "Anonymous , CA",
    "experience": "3+ years"
  },
  "skills": [
    { "name": "React/Next.js", "level": 95, "category": "Frontend" },
    { "name": "Node.js", "level": 92, "category": "Backend" },
    { "name": "React Native", "level": 90, "category": "Mobile" },
    { "name": "TypeScript", "level": 88, "category": "Language" },
    { "name": "Python", "level": 85, "category": "Language" },
    { "name": "PostgreSQL", "level": 83, "category": "Database" },
    { "name": "AWS/Cloud", "level": 80, "category": "DevOps" },
    { "name": "UI/UX Design", "level": 78, "category": "Design" }
  ],
  "projects": [
    {
      "id": 1,
      "title": "EcoTracker Mobile App",
      "description": "Sustainable living companion app with AI-powered recommendations and community features.",
      "image": "/api/placeholder/400/250",
      "technologies": ["React Native", "Node.js", "MongoDB", "AI/ML"],
      "demo": "https://demo-link.com",
      "downloadApk": "https://download-link.com/ecotracker.apk",
      "category": "Mobile App",
      "featured": true
    },
    {
      "id": 2,
      "title": "FinanceFlow Dashboard",
      "description": "Real-time financial analytics platform with advanced data visualization and automated reporting.",
      "image": "/api/placeholder/400/250",
      "technologies": ["React", "D3.js", "Express.js", "PostgreSQL"],
      "demo": "https://demo-link.com",
      "category": "Web App",
      "featured": true
    },
    {
      "id": 3,
      "title": "MindfulMoments Meditation",
      "description": "Personalized meditation and mindfulness app with progress tracking and community support.",
      "image": "/api/placeholder/400/250",
      "technologies": ["Flutter", "Firebase", "TensorFlow", "WebRTC"],
      "demo": "https://demo-link.com",
      "downloadApk": "https://download-link.com/mindful.apk",
      "category": "Mobile App",
      "featured": false
    },
    {
      "id": 4,
      "title": "CodeReview Assistant",
      "description": "AI-powered code review tool that provides intelligent suggestions and best practice recommendations.",
      "image": "/api/placeholder/400/250",
      "technologies": ["Python", "OpenAI API", "React", "Docker"],
      "demo": "https://demo-link.com",
      "category": "Developer Tool",
      "featured": false
    }
  ],
  "services": [
    {
      "title": "Premium Landing Pages",
      "description": "High-converting landing pages with modern design and optimization",
      "features": ["Responsive Design", "SEO Optimization", "Analytics Integration", "A/B Testing"],
      "price": "$1,299",
      "timeline": "5-7 days",
      "popular": false
    },
    {
      "title": "Mobile App Development",
      "description": "Cross-platform mobile applications with native performance",
      "features": ["iOS & Android", "Cloud Integration", "Push Notifications", "App Store Deployment"],
      "price": "$4,999",
      "timeline": "4-6 weeks",
      "popular": true
    },
    {
      "title": "Full-Stack Web Apps",
      "description": "Complete web applications with backend and database",
      "features": ["Custom Backend", "Database Design", "API Development", "Deployment & Hosting"],
      "price": "$3,499",
      "timeline": "3-4 weeks",
      "popular": false
    }
  ],
  "telegramChannels": [
    {
      "name": "𝐔ɴᴋ 𝐍ᴇᴛᴡᴏʀᴋ",
      "username": "@unknaveen",
      "link": "https://t.me/+QjgMDPoACGZjYjZl",
      "description": "Daily Advance agents, data tutorials, and how to chat",
      "subscribers": "600",
      "category": "Education"
    },
    {
      "name": "ɴᴀᴠᴇᴇɴ ꜱʟᴏᴛꜱ ᴄʜᴀɴɴᴇʟ 🚩",
      "username": "@unknaveen",
      "link": "https://t.me/+2rP9ZBmswR5lMGY1",
      "description": "daily trusted slots, usdt selling & buying, and free rc slots",
      "subscribers": "500",
      "category": "News"
    },
    {
      "name": "𝐓ᴇʟᴇɢʀᴀᴍ 𝐒ᴛᴜᴅʏ 𝐌ᴀᴛᴇʀɪᴀʟꜱ 🚩🚩",
      "username": "@unknaveen",
      "link": "https://t.me/+hXpr2g87_lBlZTY1",
      "description": "daily trusted slots, usdt selling & buying, and free rc slots",
      "subscribers": "1k",
      "category": "Portfolio"
    }
  ],
  "contact": {
    "telegram": "@unknaveen",
    "email": "noemailfornow",
    "phone": "nonumberfornow",
    "timezone": "PST (UTC-8)"
  }
};

// Router Class
class Router {
  constructor() {
    this.routes = {};
    this.currentRoute = null;
    this.init();
  }

  init() {
    // Define routes
    this.routes = {
      '': () => this.showPage('home-page'),
      '/': () => this.showPage('home-page'),
      '/about': () => this.showPage('about-page'),
      '/projects': () => this.showPage('projects-page'),
      '/services': () => this.showPage('services-page'),
      '/telegram': () => this.showPage('telegram-page'),
      '/contact': () => this.showPage('contact-page')
    };

    // Handle initial route
    this.handleRoute();

    // Listen for navigation
    window.addEventListener('popstate', () => this.handleRoute());
  }

  navigate(path, pushState = true) {
    if (pushState && window.location.pathname !== path) {
      window.history.pushState({}, '', path);
    }
    this.handleRoute();
  }

  handleRoute() {
    let path = window.location.pathname;
    if (path === '' || path === '/') path = '/';
    
    const route = this.routes[path] || this.routes['/'];
    
    if (route) {
      route();
      this.updateNavigation(path);
    }
  }

  showPage(pageId) {
    const currentPage = document.querySelector('.page.active');
    const targetPage = document.getElementById(pageId);

    if (!targetPage) return;

    // If same page, do nothing
    if (currentPage === targetPage) return;

    if (currentPage) {
      // Fade out current page
      currentPage.classList.add('transitioning-out');
      
      setTimeout(() => {
        currentPage.classList.remove('active', 'transitioning-out');
        
        // Fade in target page
        targetPage.classList.add('active', 'transitioning-in');
        
        // Trigger page-specific animations
        this.triggerPageAnimations(pageId);
        
        setTimeout(() => {
          targetPage.classList.remove('transitioning-in');
        }, 600);
      }, 300);
    } else {
      targetPage.classList.add('active');
      this.triggerPageAnimations(pageId);
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  updateNavigation(path) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.classList.remove('active');
      const linkPath = link.getAttribute('href');
      if (linkPath === path || (path === '/' && linkPath === '/')) {
        link.classList.add('active');
      }
    });
  }

  triggerPageAnimations(pageId) {
    switch (pageId) {
      case 'home-page':
        this.animateHomePage();
        break;
      case 'about-page':
        this.animateAboutPage();
        break;
      case 'projects-page':
        this.animateProjectsPage();
        break;
      case 'services-page':
        this.animateServicesPage();
        break;
      case 'telegram-page':
        this.animateTelegramPage();
        break;
      case 'contact-page':
        this.animateContactPage();
        break;
    }
  }

  animateHomePage() {
    // Animate counter stats
    setTimeout(() => {
      const statNumbers = document.querySelectorAll('.stat-number');
      statNumbers.forEach(stat => {
        animateCounter(stat, parseInt(stat.dataset.count));
      });
    }, 500);

    // Animate typing effect
    setTimeout(() => {
      animateTyping();
    }, 1000);
  }

  animateAboutPage() {
    // Animate skill bars
    setTimeout(() => {
      const skillBars = document.querySelectorAll('.skill-progress');
      skillBars.forEach((bar, index) => {
        setTimeout(() => {
          bar.style.width = '0%';
          const targetWidth = bar.style.width;
          const level = bar.dataset.level;
          if (level) {
            setTimeout(() => {
              bar.style.width = level + '%';
            }, 100);
          }
        }, index * 200);
      });
    }, 300);
  }

  animateProjectsPage() {
    // Projects are already populated, just trigger animations
    setTimeout(() => {
      const projectCards = document.querySelectorAll('.project-card');
      projectCards.forEach((card, index) => {
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, index * 200);
      });
    }, 300);
  }

  animateServicesPage() {
    // Services are already populated, just trigger animations
    setTimeout(() => {
      const serviceCards = document.querySelectorAll('.service-card');
      serviceCards.forEach((card, index) => {
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, index * 200);
      });
    }, 300);
  }

  animateTelegramPage() {
    // Channels are already populated, just trigger animations
    setTimeout(() => {
      const channelCards = document.querySelectorAll('.channel-card');
      channelCards.forEach((card, index) => {
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, index * 200);
      });
    }, 300);
  }

  animateContactPage() {
    // Contact page is already populated in HTML
  }
}

// Initialize Router
let router;

// App Initialization
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  hideLoadingScreen();
  router = new Router();
  setupNavigation();
  setupScrollEffects();
  setupMobileMenu();
  setupFormHandling();
  setupScrollToTop();
  setupFloatingParticles();
  setupGlowEffects();
  
  // Populate data for all pages immediately
  populateProjects();
  populateServices();
  populateTelegramChannels();
  
  // Setup hero buttons
  setupHeroButtons();
}

// Setup Hero Buttons
function setupHeroButtons() {
  const viewProjectsBtn = document.querySelector('a[data-route="projects"]');
  const getInTouchBtn = document.querySelector('a[data-route="contact"]');
  
  if (viewProjectsBtn) {
    viewProjectsBtn.addEventListener('click', (e) => {
      e.preventDefault();
      router.navigate('/projects');
    });
  }
  
  if (getInTouchBtn) {
    getInTouchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      router.navigate('/contact');
    });
  }
}

// Loading Screen
function hideLoadingScreen() {
  const loadingScreen = document.getElementById('loading-screen');
  
  setTimeout(() => {
    loadingScreen.classList.add('hidden');
    
    // Start initial animations
    setTimeout(() => {
      if (router) {
        router.triggerPageAnimations('home-page');
      }
    }, 600);
  }, 1500);
}

// Navigation Setup
function setupNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const href = link.getAttribute('href');
      router.navigate(href);
    });
  });

  // Navbar scroll effect
  let lastScrollY = window.scrollY;
  const navbar = document.getElementById('navbar');
  
  window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    
    if (currentScrollY > 100) {
      navbar.style.background = 'rgba(255, 255, 253, 0.98)';
      navbar.style.backdropFilter = 'blur(25px)';
      navbar.style.boxShadow = '0 2px 20px rgba(33, 128, 141, 0.15)';
    } else {
      navbar.style.background = 'rgba(255, 255, 253, 0.95)';
      navbar.style.backdropFilter = 'blur(20px)';
      navbar.style.boxShadow = '0 2px 20px rgba(33, 128, 141, 0.1)';
    }

    lastScrollY = currentScrollY;
  });
}

// Mobile Menu
function setupMobileMenu() {
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');
  
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    // Close menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });
  }
}

// Scroll Effects
function setupScrollEffects() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe elements for scroll animations
  setTimeout(() => {
    const animatedElements = document.querySelectorAll('.card, .project-card, .service-card, .channel-card');
    animatedElements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px)';
      el.style.transition = 'all 0.8s ease';
      observer.observe(el);
    });
  }, 1000);
}

// Counter Animation
function animateCounter(element, target) {
  let current = 0;
  const increment = target / 50;
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    element.textContent = Math.floor(current) + '+';
  }, 30);
}

// Typing Animation
function animateTyping() {
  const typingElement = document.getElementById('typing-status');
  if (!typingElement) return;
  
  const states = ["'available'", "'coding'", "'learning'", "'building'"];
  let currentIndex = 0;
  
  function typeText(text, callback) {
    let i = 0;
    typingElement.textContent = '';
    
    const typeTimer = setInterval(() => {
      if (i < text.length) {
        typingElement.textContent += text.charAt(i);
        i++;
      } else {
        clearInterval(typeTimer);
        setTimeout(callback, 1000);
      }
    }, 100);
  }
  
  function eraseText(callback) {
    const text = typingElement.textContent;
    let i = text.length;
    
    const eraseTimer = setInterval(() => {
      if (i > 0) {
        typingElement.textContent = text.substring(0, i - 1);
        i--;
      } else {
        clearInterval(eraseTimer);
        setTimeout(callback, 200);
      }
    }, 50);
  }
  
  function cycle() {
    typeText(states[currentIndex], () => {
      eraseText(() => {
        currentIndex = (currentIndex + 1) % states.length;
        cycle();
      });
    });
  }
  
  setTimeout(() => cycle(), 1000);
}

// Populate Projects
function populateProjects() {
  const projectsGrid = document.getElementById('projects-grid');
  if (!projectsGrid) return;
  
  projectsGrid.innerHTML = '';
  
  applicationData.projects.forEach((project, index) => {
    const projectCard = createProjectCard(project, index);
    projectsGrid.appendChild(projectCard);
  });
  
  setupProjectFilter();
}

function createProjectCard(project, index) {
  const card = document.createElement('div');
  card.className = `project-card ${project.featured ? 'featured' : ''}`;
  card.dataset.category = project.category;
  card.style.animationDelay = `${index * 0.2}s`;
  
  const techStackHTML = project.technologies.map(tech => 
    `<span class="tech-tag">${tech}</span>`
  ).join('');
  
  const linksHTML = `
    <a href="${project.demo}" class="project-link" target="_blank">View Demo</a>
    ${project.downloadApk ? `<a href="${project.downloadApk}" class="project-link" target="_blank">Download APK</a>` : ''}
  `;
  
  const categoryEmoji = {
    'Mobile App': '📱',
    'Web App': '💻',
    'Developer Tool': '🛠️'
  };
  
  card.innerHTML = `
    <div class="project-image">
      <div class="project-emoji">${categoryEmoji[project.category] || '🚀'}</div>
    </div>
    <div class="project-content">
      <div class="project-category">${project.category}</div>
      <h3 class="project-title">${project.title}</h3>
      <p class="project-description">${project.description}</p>
      <div class="tech-stack">${techStackHTML}</div>
      <div class="project-links">${linksHTML}</div>
    </div>
  `;
  
  return card;
}

function setupProjectFilter() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active filter
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const filter = btn.dataset.filter;
      
      // Filter projects
      projectCards.forEach((card, index) => {
        if (filter === 'all' || card.dataset.category === filter) {
          card.style.display = 'block';
          card.style.animation = `slideUp 0.6s ease-out ${index * 0.1}s both`;
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

// Populate Services
function populateServices() {
  const servicesGrid = document.getElementById('services-grid');
  if (!servicesGrid) return;
  
  servicesGrid.innerHTML = '';
  
  applicationData.services.forEach((service, index) => {
    const serviceCard = createServiceCard(service, index);
    servicesGrid.appendChild(serviceCard);
  });
}

function createServiceCard(service, index) {
  const card = document.createElement('div');
  card.className = `service-card ${service.popular ? 'popular' : ''}`;
  card.style.animationDelay = `${index * 0.2}s`;
  
  const featuresHTML = service.features.map(feature => 
    `<li>${feature}</li>`
  ).join('');
  
  card.innerHTML = `
    <h3 class="service-title">${service.title}</h3>
    <p class="service-description">${service.description}</p>
    <ul class="service-features">${featuresHTML}</ul>
    <div class="service-price">${service.price}</div>
    <div class="service-timeline">${service.timeline}</div>
    <button class="btn btn--primary service-contact-btn">Get Started</button>
  `;
  
  // Add navigation for service buttons
  const btn = card.querySelector('.service-contact-btn');
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    router.navigate('/contact');
  });
  
  return card;
}

// Populate Telegram Channels
function populateTelegramChannels() {
  const channelsGrid = document.getElementById('channels-grid');
  if (!channelsGrid) return;
  
  channelsGrid.innerHTML = '';
  
  applicationData.telegramChannels.forEach((channel, index) => {
    const channelCard = createChannelCard(channel, index);
    channelsGrid.appendChild(channelCard);
  });
}

function createChannelCard(channel, index) {
  const card = document.createElement('div');
  card.className = 'channel-card';
  card.style.animationDelay = `${index * 0.2}s`;
  
  const categoryEmoji = {
    'Education': '📚',
    'News': '📰',
    'Portfolio': '🎨'
  };
  
  card.innerHTML = `
    <div class="channel-icon">${categoryEmoji[channel.category] || '📱'}</div>
    <h3 class="channel-name">${channel.name}</h3>
    <p class="channel-description">${channel.description}</p>
    <div class="channel-stats">${channel.subscribers} subscribers</div>
    <a href="${channel.link}" class="btn btn--primary" target="_blank">Join Channel</a>
  `;
  
  return card;
}

// Form Handling
function setupFormHandling() {
  const form = document.getElementById('contact-form');
  if (!form) return;
  
  const inputs = form.querySelectorAll('.form-control');
  const submitBtn = document.getElementById('submit-btn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnLoader = submitBtn.querySelector('.btn-loader');
  
  // Input animations
  inputs.forEach(input => {
    input.addEventListener('focus', () => {
      input.parentElement.classList.add('focused');
      createInputGlow(input);
    });
    
    input.addEventListener('blur', () => {
      if (!input.value) {
        input.parentElement.classList.remove('focused');
      }
    });
    
    // Real-time validation
    input.addEventListener('input', () => {
      validateField(input);
    });
  });
  
  // Form submission
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    if (validateForm(form)) {
      submitForm(form, btnText, btnLoader);
    }
  });
}

function createInputGlow(input) {
  const rect = input.getBoundingClientRect();
  const particles = [];
  
  for (let i = 0; i < 6; i++) {
    const particle = document.createElement('div');
    particle.style.cssText = `
      position: fixed;
      width: 4px;
      height: 4px;
      background: var(--color-primary);
      border-radius: 50%;
      pointer-events: none;
      z-index: 1000;
      box-shadow: 0 0 10px var(--color-primary);
    `;
    
    particle.style.left = (rect.left + Math.random() * rect.width) + 'px';
    particle.style.top = (rect.top + rect.height / 2) + 'px';
    
    document.body.appendChild(particle);
    
    // Animate particle
    const angle = (i / 6) * Math.PI * 2;
    const distance = 20 + Math.random() * 15;
    const endX = Math.cos(angle) * distance;
    const endY = Math.sin(angle) * distance;
    
    particle.animate([
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
      { transform: `translate(${endX}px, ${endY}px) scale(0)`, opacity: 0 }
    ], {
      duration: 800,
      easing: 'ease-out'
    }).onfinish = () => {
      particle.remove();
    };
  }
}

function validateField(field) {
  const value = field.value.trim();
  let isValid = true;
  
  if (field.required && !value) {
    isValid = false;
  } else if (field.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    isValid = emailRegex.test(value);
  }
  
  field.style.borderColor = isValid ? 'var(--color-primary)' : 'var(--color-error)';
  
  return isValid;
}

function validateForm(form) {
  const inputs = form.querySelectorAll('.form-control');
  let isValid = true;
  
  inputs.forEach(input => {
    if (!validateField(input)) {
      isValid = false;
    }
  });
  
  return isValid;
}

function submitForm(form, btnText, btnLoader) {
  // Show loading state
  btnText.style.display = 'none';
  btnLoader.classList.remove('hidden');
  btnLoader.classList.add('visible');
  
  // Simulate form submission
  setTimeout(() => {
    // Hide loading state
    btnText.style.display = 'block';
    btnLoader.classList.add('hidden');
    btnLoader.classList.remove('visible');
    
    // Show success message
    showNotification('Message sent successfully! I\'ll get back to you soon.', 'success');
    
    // Reset form
    form.reset();
    
    // Remove focused states
    const formGroups = form.querySelectorAll('.form-group');
    formGroups.forEach(group => group.classList.remove('focused'));
    
    // Reset input styles
    const inputs = form.querySelectorAll('.form-control');
    inputs.forEach(input => {
      input.style.borderColor = 'var(--color-border)';
    });
  }, 2000);
}

// Scroll to Top
function setupScrollToTop() {
  const scrollTopBtn = document.getElementById('scroll-top');
  
  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  });
  
  scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    
    // Add ripple effect
    createRippleEffect(scrollTopBtn);
  });
}

function createRippleEffect(element) {
  const rect = element.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = rect.width / 2 - size / 2;
  const y = rect.height / 2 - size / 2;
  
  const ripple = document.createElement('div');
  ripple.style.cssText = `
    position: absolute;
    width: ${size}px;
    height: ${size}px;
    left: ${x}px;
    top: ${y}px;
    background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%);
    border-radius: 50%;
    transform: scale(0);
    pointer-events: none;
    z-index: 1000;
  `;
  
  element.style.position = 'relative';
  element.style.overflow = 'hidden';
  element.appendChild(ripple);
  
  ripple.animate([
    { transform: 'scale(0)', opacity: 1 },
    { transform: 'scale(2)', opacity: 0 }
  ], {
    duration: 600,
    easing: 'ease-out'
  }).onfinish = () => {
    ripple.remove();
  };
}

// Floating Particles
function setupFloatingParticles() {
  const particlesContainer = document.getElementById('floating-particles');
  if (!particlesContainer) return;
  
  const particles = particlesContainer.querySelectorAll('.particle');
  
  // Randomize particle positions and animations
  particles.forEach((particle, index) => {
    const randomDelay = Math.random() * 10;
    const randomDuration = 12 + Math.random() * 8;
    const randomLeft = 10 + (index * 20) + Math.random() * 10;
    
    particle.style.left = randomLeft + '%';
    particle.style.animationDelay = `-${randomDelay}s`;
    particle.style.animationDuration = `${randomDuration}s`;
  });
}

// Glow Effects
function setupGlowEffects() {
  const glowElements = document.querySelectorAll('.glow-hover, .btn--primary, .floating-card');
  
  glowElements.forEach(element => {
    element.addEventListener('mouseenter', () => {
      createGlowParticles(element);
    });
  });
}

function createGlowParticles(element) {
  const rect = element.getBoundingClientRect();
  
  for (let i = 0; i < 8; i++) {
    const particle = document.createElement('div');
    particle.style.cssText = `
      position: fixed;
      width: 3px;
      height: 3px;
      background: var(--color-primary);
      border-radius: 50%;
      pointer-events: none;
      z-index: 1000;
      box-shadow: 0 0 8px var(--color-primary);
    `;
    
    particle.style.left = (rect.left + rect.width / 2) + 'px';
    particle.style.top = (rect.top + rect.height / 2) + 'px';
    
    document.body.appendChild(particle);
    
    const angle = (i / 8) * Math.PI * 2;
    const distance = 25 + Math.random() * 15;
    const endX = Math.cos(angle) * distance;
    const endY = Math.sin(angle) * distance;
    
    particle.animate([
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
      { transform: `translate(${endX}px, ${endY}px) scale(0)`, opacity: 0 }
    ], {
      duration: 600 + Math.random() * 400,
      easing: 'ease-out'
    }).onfinish = () => {
      particle.remove();
    };
  }
}

// Notification System
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  
  const colors = {
    success: 'var(--color-success)',
    error: 'var(--color-error)',
    info: 'var(--color-primary)'
  };
  
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--color-surface);
    border: 2px solid ${colors[type]};
    border-radius: var(--radius-base);
    padding: 16px 20px;
    color: var(--color-text);
    font-weight: 500;
    font-size: 14px;
    z-index: 10000;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transform: translateX(100%);
    transition: all 0.4s ease;
    max-width: 300px;
  `;
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Slide in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 10);
  
  // Slide out and remove
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      notification.remove();
    }, 400);
  }, 4000);
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const navMenu = document.getElementById('nav-menu');
    const navToggle = document.getElementById('nav-toggle');
    
    if (navMenu && navMenu.classList.contains('active')) {
      navToggle.click();
    }
  }
});

// Handle visibility change for performance
document.addEventListener('visibilitychange', () => {
  const particles = document.querySelectorAll('.particle');
  particles.forEach(particle => {
    if (document.hidden) {
      particle.style.animationPlayState = 'paused';
    } else {
      particle.style.animationPlayState = 'running';
    }
  });
});

// Add CSS for dynamic animations
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
  .animate {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
  
  .notification {
    animation: slideIn 0.4s ease-out;
  }
  
  .project-emoji {
    font-size: 3rem;
    animation: float 3s ease-in-out infinite;
  }
  
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(dynamicStyles);
