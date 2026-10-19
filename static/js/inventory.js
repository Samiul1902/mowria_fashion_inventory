/**
 * Mowria Fashion (MFB) - External Client-Side Application Core
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function inventoryApp() {
    return {
        darkMode: localStorage.getItem('theme') !== 'light',
        currentView: 'grid',
        showAddModal: false,
        showEditModal: false,
        showPreviewModal: false,
        showDeleteModal: false,
        showScannerModal: false,
        showProfileModal: false,
        html5QrCodeScanner: null,

        editData: {},
        previewData: {},
        deleteData: {},

        init() {
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },

        toggleTheme() {
            this.darkMode = !this.darkMode;
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
            this.$nextTick(() => lucide.createIcons());
        },

        openScannerModal() {
            this.showScannerModal = true;
            this.$nextTick(() => {
                lucide.createIcons();
                try {
                    this.html5QrCodeScanner = new Html5Qrcode("reader");
                    const config = { fps: 10, qrbox: { width: 250, height: 250 } };
                    this.html5QrCodeScanner.start(
                        { facingMode: "environment" },
                        config,
                        (decodedText) => {
                            this.closeScannerModal();
                            const searchInput = document.getElementById('main-search-input');
                            if (searchInput) {
                                searchInput.value = decodedText;
                                document.getElementById('filter-form').submit();
                            }
                        },
                        () => {}
                    ).catch(err => {
                        console.warn("Camera scanner start warning:", err);
                    });
                } catch (e) {
                    console.error("Scanner init error:", e);
                }
            });
        },

        closeScannerModal() {
            if (this.html5QrCodeScanner) {
                try {
                    this.html5QrCodeScanner.stop().then(() => {
                        this.html5QrCodeScanner.clear();
                    });
                } catch (e) {}
            }
            this.showScannerModal = false;
        },

        openAddModal() {
            this.showAddModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openEditModal(data) {
            this.editData = { ...data };
            this.showEditModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openPreviewModal(data) {
            this.previewData = { ...data };
            this.showPreviewModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openDeleteModal(id, code, name) {
            this.deleteData = { id, code, name };
            this.showDeleteModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openProfileModal() {
            this.showProfileModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        async adjustSize(productId, size, delta) {
            const csrftoken = getCookie('csrftoken');
            try {
                const response = await fetch(`/product/${productId}/adjust-size/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({ size, delta })
                });

                const res = await response.json();
                if (response.ok && res.success) {
                    // Update Card View elements
                    const cardValEl = document.getElementById(`stock-val-${productId}-${size}`);
                    if (cardValEl) cardValEl.innerText = res.new_size_qty;

                    const cardTotalEl = document.getElementById(`card-total-${productId}`);
                    if (cardTotalEl) cardTotalEl.innerText = res.total_quantity;

                    const cardStockVal = document.getElementById(`card-val-${productId}`);
                    if (cardStockVal) cardStockVal.innerText = '৳' + Math.round(res.stock_value);

                    // Update Status Badge
                    const badgeEl = document.getElementById(`badge-status-${productId}`);
                    if (badgeEl) {
                        if (res.stock_status === 'In Stock') {
                            badgeEl.innerHTML = `<span class="px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-500/95 text-white shadow-xs flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-white"></span> In Stock</span>`;
                        } else if (res.stock_status === 'Low Stock') {
                            badgeEl.innerHTML = `<span class="px-2.5 py-1 rounded-md text-xs font-bold bg-amber-500/95 text-slate-950 shadow-xs flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-slate-950"></span> Low Stock</span>`;
                        } else {
                            badgeEl.innerHTML = `<span class="px-2.5 py-1 rounded-md text-xs font-bold bg-rose-600/95 text-white shadow-xs flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-white"></span> Out of Stock</span>`;
                        }
                    }

                    // Update List View elements if present
                    const listSizeEl = document.getElementById(`list-${size}-${productId}`);
                    if (listSizeEl) listSizeEl.innerText = res.new_size_qty;

                    const listTotalEl = document.getElementById(`list-total-${productId}`);
                    if (listTotalEl) listTotalEl.innerText = res.total_quantity;

                    const listValEl = document.getElementById(`list-val-${productId}`);
                    if (listValEl) listValEl.innerText = '৳' + Math.round(res.stock_value);

                    // Update Preview data if open for this product
                    if (this.previewData && this.previewData.id == productId) {
                        this.previewData['size_' + size] = res.new_size_qty;
                        this.previewData.total_qty = res.total_quantity;
                        this.previewData.stock_value = res.stock_value;
                        this.previewData.expected_profit = res.expected_profit;
                    }
                } else {
                    alert(res.error || 'Failed to adjust stock');
                }
            } catch (err) {
                console.error('Error updating size stock:', err);
            }
        }
    };
}

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
});
