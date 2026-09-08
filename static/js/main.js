/**
 * SmartCart - Core Client Interactions & Theme Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark Mode / Light Mode Theme Toggle
    const themeToggleBtn = document.getElementById('scThemeToggle');
    const htmlElement = document.documentElement;
    const currentTheme = localStorage.getItem('smartcart_theme') || 'light';
    
    htmlElement.setAttribute('data-bs-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const activeTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('smartcart_theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Trigger chart theme re-render if on analytics page
            if (window.renderAllAdminCharts) {
                window.renderAllAdminCharts();
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'dark') {
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning"></i>';
        } else {
            themeToggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        }
    }

    // 2. Global Wishlist Toggle Handler
    document.querySelectorAll('.sc-wishlist-toggle-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const productId = btn.getAttribute('data-product-id');
            if (!productId) return;

            try {
                const response = await fetch('/api/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId })
                });

                if (response.status === 401) {
                    window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    const heartIcon = btn.querySelector('i');
                    if (data.in_wishlist) {
                        heartIcon.className = 'bi bi-heart-fill text-danger';
                        showToast(data.message, 'success');
                    } else {
                        heartIcon.className = 'bi bi-heart';
                        showToast(data.message, 'info');
                    }

                    // Update navbar badge
                    const badge = document.getElementById('navWishlistBadge');
                    if (badge) {
                        badge.textContent = data.count;
                        badge.style.display = data.count > 0 ? 'inline-block' : 'none';
                    }
                }
            } catch (err) {
                console.error('Wishlist error:', err);
            }
        });
    });
});

// Toast Notification Helper
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('scToastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'scToastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1090';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast_' + Date.now();
    const bgClass = type === 'success' ? 'bg-success text-white' : 
                    type === 'danger' ? 'bg-danger text-white' : 
                    type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body fw-medium">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElem = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastElem, { delay: 3500 });
    bsToast.show();
    toastElem.addEventListener('hidden.bs.toast', () => toastElem.remove());
}
