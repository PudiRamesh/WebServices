// Main JavaScript file for PowerPoint Audit Trail Dashboard

// Utility functions
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function formatFileSize(bytes) {
    if (!bytes) return '-';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function getActionColor(action) {
    const colors = {
        'file_created': 'success',
        'file_modified': 'warning',
        'file_deleted': 'danger',
        'initial_scan': 'info'
    };
    return colors[action] || 'secondary';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Chart configuration
const chartColors = {
    primary: '#007bff',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    secondary: '#6c757d'
};

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        }
    }
};

// Global event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add loading states to buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn') && !e.target.disabled) {
            const originalText = e.target.innerHTML;
            e.target.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
            e.target.disabled = true;
            
            // Re-enable after a delay (can be overridden by specific handlers)
            setTimeout(() => {
                e.target.innerHTML = originalText;
                e.target.disabled = false;
            }, 2000);
        }
    });
    
    // Auto-refresh functionality
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    autoRefreshElements.forEach(element => {
        const interval = parseInt(element.dataset.autoRefresh) || 30000;
        setInterval(() => {
            if (typeof window.refreshData === 'function') {
                window.refreshData();
            }
        }, interval);
    });
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An error occurred. Please check the console for details.', 'danger');
});

// Network status monitoring
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may not work.', 'warning');
});

// Export functions for use in other scripts
window.PPTAuditUtils = {
    formatDateTime,
    formatFileSize,
    getActionColor,
    showNotification,
    debounce,
    apiRequest,
    chartColors,
    chartOptions
};