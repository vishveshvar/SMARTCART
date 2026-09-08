/**
 * SmartCart - Shopping Cart AJAX Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Single Add-to-Cart Buttons
    document.querySelectorAll('.sc-add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');
            const qtyInput = document.getElementById('productDetailQty');
            const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

            btn.disabled = true;
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Adding...';

            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId, quantity: quantity })
                });

                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    updateNavCartBadge(data.total_items);
                } else {
                    showToast(data.message || 'Could not add to cart', 'danger');
                }
            } catch (err) {
                console.error('Add to cart error:', err);
                showToast('Network error adding to cart', 'danger');
            } finally {
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            }
        });
    });

    // 2. Add Frequently Bought Together Bundle (1-Click Bundle Checkout)
    const bundleBtn = document.getElementById('scAddBundleBtn');
    if (bundleBtn) {
        bundleBtn.addEventListener('click', async () => {
            const pidsAttr = bundleBtn.getAttribute('data-bundle-pids');
            if (!pidsAttr) return;
            const pids = pidsAttr.split(',').filter(Boolean);

            bundleBtn.disabled = true;
            bundleBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Adding Bundle...';

            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bundle_product_ids: pids, quantity: 1 })
                });

                const data = await response.json();
                if (data.success) {
                    showToast('🎉 All items in the bundle added to your cart with discount!', 'success');
                    updateNavCartBadge(data.total_items);
                }
            } catch (err) {
                console.error('Bundle error:', err);
            } finally {
                bundleBtn.disabled = false;
                bundleBtn.innerHTML = '<i class="bi bi-cart-plus me-1"></i> Add All to Cart';
            }
        });
    }

    // 3. Cart Page Quantity Modifiers (+ and -)
    document.querySelectorAll('.sc-cart-qty-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const productId = btn.getAttribute('data-product-id');
            const action = btn.getAttribute('data-action');
            await updateCartItem(productId, action);
        });
    });

    // 4. Cart Page Remove Item
    document.querySelectorAll('.sc-cart-remove-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const productId = btn.getAttribute('data-product-id');
            if (confirm('Remove this product from your cart?')) {
                await removeCartItem(productId);
            }
        });
    });
});

async function updateCartItem(productId, action) {
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, action: action })
        });
        const data = await response.json();
        if (data.success) {
            window.location.reload(); // Reload to refresh totals and line items
        }
    } catch (err) {
        console.error('Update cart error:', err);
    }
}

async function removeCartItem(productId) {
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        const data = await response.json();
        if (data.success) {
            window.location.reload();
        }
    } catch (err) {
        console.error('Remove item error:', err);
    }
}

function updateNavCartBadge(count) {
    const badge = document.getElementById('navCartBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}
