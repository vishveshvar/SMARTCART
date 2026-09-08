/**
 * SmartCart - Recommendation Telemetry & Click Tracker
 */

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.sc-recommendation-card a').forEach(link => {
        link.addEventListener('click', () => {
            const card = link.closest('.sc-recommendation-card');
            if (card) {
                const productId = card.getAttribute('data-product-id');
                const recType = card.getAttribute('data-rec-type') || 'Personalized';
                
                // Track click event asynchronously (beacon or fetch)
                if (productId) {
                    fetch('/api/recommendations/track', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            product_id: productId,
                            event_type: 'click',
                            recommendation_type: recType
                        }),
                        keepalive: true
                    }).catch(err => console.error('Tracking error:', err));
                }
            }
        });
    });
});
