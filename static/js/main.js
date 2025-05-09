// Main JavaScript file for general functionality

document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menu toggle with improved functionality
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event from bubbling up
            this.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navLinks?.contains(event.target);
        const isClickInsideHamburger = hamburgerMenu?.contains(event.target);
        
        if (navLinks?.classList.contains('active') && !isClickInsideNav && !isClickInsideHamburger) {
            hamburgerMenu?.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
    
    // Close menu when clicking a menu item (for mobile)
    if (navLinks) {
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                // Only perform this action on mobile screens
                if (window.innerWidth <= 768) {
                    hamburgerMenu?.classList.remove('active');
                    navLinks.classList.remove('active');
                }
            });
        });
    }
    
    // Auto resize textarea
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            
            // Reset height if empty
            if (this.value === '') {
                this.style.height = 'auto';
            }
        });
    }
    
    // Flash messages auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
});

// Helper function for creating HTML from a template
function createElementFromTemplate(templateId, dataObj = {}) {
    const template = document.getElementById(templateId);
    if (!template) return null;
    
    const element = document.importNode(template.content, true).firstElementChild;
    
    // Set content if provided
    if (dataObj.content) {
        const contentContainer = element.querySelector('p');
        if (contentContainer) {
            // Process line breaks
            const formattedContent = dataObj.content.replace(/\n/g, '<br>');
            contentContainer.innerHTML = formattedContent;
        }
    }
    
    return element;
}
