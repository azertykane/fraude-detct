// static/main.js
document.addEventListener("DOMContentLoaded", () => {
    // Animation d'entrée pour les cartes
    const animateCards = () => {
        const cards = document.querySelectorAll('.glass-card, .form-card, .content-container');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    };

    // Initialisation des tooltips
    const initTooltips = () => {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    };

    // Gestion des fichiers drag & drop
    const initFileDrop = () => {
        const fileInput = document.querySelector('input[type="file"]');
        const uploadArea = document.querySelector('.upload-area');
        
        if (fileInput && uploadArea) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, unhighlight, false);
            });
            
            function highlight() {
                uploadArea.style.borderColor = '#2c5aa0';
                uploadArea.style.backgroundColor = 'rgba(44, 90, 160, 0.1)';
            }
            
            function unhighlight() {
                uploadArea.style.borderColor = '#ddd';
                uploadArea.style.backgroundColor = 'rgba(248, 249, 250, 0.7)';
            }
            
            uploadArea.addEventListener('drop', handleDrop, false);
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                fileInput.files = files;
                
                // Afficher le nom du fichier
                if (files.length > 0) {
                    const fileNameDisplay = uploadArea.querySelector('.file-name') || document.createElement('div');
                    fileNameDisplay.className = 'file-name mt-2 text-success';
                    fileNameDisplay.innerHTML = `<i class="fas fa-file me-1"></i>Fichier sélectionné: ${files[0].name}`;
                    if (!uploadArea.querySelector('.file-name')) {
                        uploadArea.appendChild(fileNameDisplay);
                    }
                }
            }
        }
    };

    // Confirmation avant soumission
    const initConfirmations = () => {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Traitement...';
                    submitBtn.disabled = true;
                }
            });
        });
    };

    // Effet de particules pour la page d'accueil
    const initParticles = () => {
        if (document.querySelector('.glass-card')) {
            const canvas = document.createElement('canvas');
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            canvas.style.pointerEvents = 'none';
            canvas.style.zIndex = '-1';
            document.body.appendChild(canvas);
            
            const ctx = canvas.getContext('2d');
            let particles = [];
            
            function resizeCanvas() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            
            class Particle {
                constructor() {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.size = Math.random() * 2 + 1;
                    this.speedX = Math.random() * 0.5 - 0.25;
                    this.speedY = Math.random() * 0.5 - 0.25;
                    this.color = `rgba(255, 255, 255, ${Math.random() * 0.3})`;
                }
                
                update() {
                    this.x += this.speedX;
                    this.y += this.speedY;
                    
                    if (this.x > canvas.width) this.x = 0;
                    else if (this.x < 0) this.x = canvas.width;
                    if (this.y > canvas.height) this.y = 0;
                    else if (this.y < 0) this.y = canvas.height;
                }
                
                draw() {
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            function init() {
                resizeCanvas();
                particles = [];
                for (let i = 0; i < 50; i++) {
                    particles.push(new Particle());
                }
            }
            
            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach(particle => {
                    particle.update();
                    particle.draw();
                });
                requestAnimationFrame(animate);
            }
            
            window.addEventListener('resize', resizeCanvas);
            init();
            animate();
        }
    };

    // Initialisation
    animateCards();
    initTooltips();
    initFileDrop();
    initConfirmations();
    initParticles();

    console.log('🚀 Application de détection de fraude initialisée avec succès!');
});

// Fonctions utilitaires globales
const FraudDetectionApp = {
    // Formatage des nombres
    formatNumber: (number) => {
        return new Intl.NumberFormat('fr-FR').format(number);
    },
    
    // Formatage des pourcentages
    formatPercent: (number) => {
        return new Intl.NumberFormat('fr-FR', {
            style: 'percent',
            minimumFractionDigits: 1
        }).format(number);
    },
    
    // Affichage de notifications
    showNotification: (message, type = 'info') => {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
};