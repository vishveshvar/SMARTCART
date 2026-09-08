/**
 * SmartCart - Admin Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // Edit Product Modal prefiller
    document.querySelectorAll('.sc-edit-product-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const pid = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name');
            const cat = btn.getAttribute('data-category');
            const subcat = btn.getAttribute('data-subcat');
            const brand = btn.getAttribute('data-brand');
            const price = btn.getAttribute('data-price');
            const discount = btn.getAttribute('data-discount');
            const stock = btn.getAttribute('data-stock');
            const rating = btn.getAttribute('data-rating');
            const status = btn.getAttribute('data-status');

            document.getElementById('editProductId').value = pid;
            document.getElementById('editName').value = name;
            document.getElementById('editCategory').value = cat;
            document.getElementById('editSubcategory').value = subcat;
            document.getElementById('editBrand').value = brand;
            document.getElementById('editPrice').value = price;
            document.getElementById('editDiscount').value = discount;
            document.getElementById('editStock').value = stock;
            document.getElementById('editRating').value = rating;
            document.getElementById('editStatus').value = status;
        });
    });

    // Retrain Model Button Spinner
    const retrainForm = document.getElementById('retrainModelForm');
    if (retrainForm) {
        retrainForm.addEventListener('submit', () => {
            const btn = document.getElementById('retrainBtn');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Retraining Random Forest Model...';
            }
        });
    }
});
