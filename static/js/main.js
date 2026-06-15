/* ─── NAVBAR SCROLL ─────────────────────────────── */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

/* ─── HAMBURGER ─────────────────────────────────── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

/* ─── ACTIVE NAV LINK ON SCROLL ─────────────────── */
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-link');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navItems.forEach(link => link.classList.remove('active'));
      const active = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
      if (active) active.classList.add('active');
    }
  });
}, { threshold: 0.4, rootMargin: '-80px 0px 0px 0px' });

sections.forEach(s => observer.observe(s));

/* ─── TYPED ROLE EFFECT ─────────────────────────── */
const roles = [
  'Software Developer',
  'Full Stack Learner',
  'SMMA Founder',
  'Startup Enthusiast',
  'Problem Solver'
];

let roleIndex = 0, charIndex = 0, isDeleting = false;
const typedEl = document.getElementById('typed-role');

function typeEffect() {
  const current = roles[roleIndex];
  if (isDeleting) {
    typedEl.textContent = current.substring(0, charIndex - 1);
    charIndex--;
  } else {
    typedEl.textContent = current.substring(0, charIndex + 1);
    charIndex++;
  }

  let speed = isDeleting ? 60 : 110;

  if (!isDeleting && charIndex === current.length) {
    speed = 2000;
    isDeleting = true;
  } else if (isDeleting && charIndex === 0) {
    isDeleting = false;
    roleIndex = (roleIndex + 1) % roles.length;
    speed = 400;
  }

  setTimeout(typeEffect, speed);
}

typeEffect();

/* ─── FADE IN ON SCROLL ─────────────────────────── */
const fadeEls = document.querySelectorAll(
  '.skill-card, .project-card, .achievement-card, .exp-card, .timeline-item, .lesson-item, .building-item, .fact-item, .contact-link, .venture-main, .venture-lessons'
);

fadeEls.forEach(el => el.classList.add('fade-in'));

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.12 });

fadeEls.forEach(el => fadeObserver.observe(el));

/* ─── CONTACT FORM (AJAX → Flask) ───────────────── */
const form      = document.getElementById('contact-form');
const submitBtn = document.getElementById('submit-btn');
const btnText   = document.getElementById('btn-text');
const btnIcon   = document.getElementById('btn-icon');
const status    = document.getElementById('form-status');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Loading state
  submitBtn.disabled = true;
  btnText.textContent = 'Sending…';
  btnIcon.className = 'fas fa-spinner fa-spin';
  status.className = 'form-status';
  status.style.display = 'none';

  const payload = {
    name:    document.getElementById('name').value,
    email:   document.getElementById('email').value,
    subject: document.getElementById('subject').value,
    message: document.getElementById('message').value
  };

  try {
    const res  = await fetch('/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      status.className = 'form-status success';
      status.textContent = data.message;
      form.reset();
    } else {
      status.className = 'form-status error';
      status.textContent = data.error || 'Something went wrong. Please try again.';
    }
  } catch {
    status.className = 'form-status error';
    status.textContent = 'Network error. Please check your connection.';
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = 'Send Message';
    btnIcon.className = 'fas fa-paper-plane';
  }
});
