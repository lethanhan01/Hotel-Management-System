// Attach fallback behavior for room images (use data-fallback when src fails)
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.room-img').forEach(function(img) {
        img.addEventListener('error', function() {
            var fb = this.getAttribute('data-fallback');
            if (fb && this.src !== fb) {
                this.src = fb;
            }
        });
    });
});
