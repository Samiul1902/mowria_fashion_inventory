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

        showSaleModal: false,
        showReturnModal: false,
        showCameraModal: false,
        cameraTargetInputId: null,
        cameraStream: null,
        cameraFacingMode: 'environment',

        saleFormData: {
            productId: '',
            size: 'm',
            quantity: 1,
            unitPrice: '',
            notes: ''
        },

        returnFormData: {
            productId: '',
            size: 'm',
            quantity: 1,
            refundPrice: '',
            notes: ''
        },

        openAddModal() {
            this.showAddModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openSaleModal(productId = '', defaultPrice = '') {
            this.saleFormData = {
                productId: productId || '',
                size: 'm',
                quantity: 1,
                unitPrice: defaultPrice || '',
                notes: ''
            };
            this.showSaleModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        openReturnModal(productId = '', defaultPrice = '') {
            this.returnFormData = {
                productId: productId || '',
                size: 'm',
                quantity: 1,
                refundPrice: defaultPrice || '',
                notes: ''
            };
            this.showReturnModal = true;
            this.$nextTick(() => lucide.createIcons());
        },

        // Direct Mobile & Webcam Live Camera Capture
        async openCamera(targetInputId) {
            this.cameraTargetInputId = targetInputId;
            this.showCameraModal = true;
            this.$nextTick(async () => {
                lucide.createIcons();
                await this.startCameraStream();
            });
        },

        async startCameraStream() {
            try {
                if (this.cameraStream) {
                    this.cameraStream.getTracks().forEach(t => t.stop());
                }
                const constraints = {
                    video: {
                        facingMode: { ideal: this.cameraFacingMode },
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                };
                this.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
                const videoEl = document.getElementById('camera-stream-video');
                if (videoEl) {
                    videoEl.srcObject = this.cameraStream;
                    videoEl.play();
                }
            } catch (err) {
                console.warn('Camera stream permission or device issue:', err);
                alert('Could not start camera. Please verify camera permissions in your browser, or select a file using the file picker.');
                this.closeCamera();
            }
        },

        switchCameraFacing() {
            this.cameraFacingMode = this.cameraFacingMode === 'environment' ? 'user' : 'environment';
            this.startCameraStream();
        },

        snapPhoto() {
            const videoEl = document.getElementById('camera-stream-video');
            const canvasEl = document.getElementById('camera-stream-canvas');
            if (!videoEl || !canvasEl) return;

            canvasEl.width = videoEl.videoWidth || 640;
            canvasEl.height = videoEl.videoHeight || 480;
            const ctx = canvasEl.getContext('2d');
            ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);

            canvasEl.toBlob((blob) => {
                if (!blob) return;
                const file = new File([blob], `garment_photo_${Date.now()}.jpg`, { type: 'image/jpeg' });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);

                const targetInput = document.getElementById(this.cameraTargetInputId);
                if (targetInput) {
                    targetInput.files = dataTransfer.files;
                    // Trigger preview visual if present
                    const previewText = document.getElementById(this.cameraTargetInputId + '-status');
                    if (previewText) {
                        previewText.innerText = `Captured: ${file.name} (${Math.round(file.size / 1024)} KB)`;
                    }
                }
                this.closeCamera();
            }, 'image/jpeg', 0.92);
        },

        closeCamera() {
            if (this.cameraStream) {
                this.cameraStream.getTracks().forEach(t => t.stop());
                this.cameraStream = null;
            }
            this.showCameraModal = false;
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

