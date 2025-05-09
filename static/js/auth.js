// JavaScript for authentication pages

document.addEventListener('DOMContentLoaded', function() {
    // Password confirmation validation
    const registerForm = document.querySelector('form[action="/register"]');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                
                // Create alert message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-error';
                alertDiv.textContent = 'Passwords do not match. Please try again.';
                
                // Insert alert before the form
                registerForm.parentNode.insertBefore(alertDiv, registerForm);
                
                // Scroll to the top of the form
                alertDiv.scrollIntoView({ behavior: 'smooth' });
                
                // Auto-dismiss the alert after 5 seconds
                setTimeout(() => {
                    alertDiv.style.opacity = '0';
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 300);
                }, 5000);
            }
        });
    }
    
    // Form input animations
    const formInputs = document.querySelectorAll('.auth-form input');
    
    formInputs.forEach(input => {
        // Add focus class to parent when input is focused
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('input-focused');
        });
        
        // Remove focus class when input is blurred
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentNode.classList.remove('input-focused');
            }
        });
        
        // Add class if input has value on page load
        if (input.value !== '') {
            input.parentNode.classList.add('input-focused');
        }
    });
});
