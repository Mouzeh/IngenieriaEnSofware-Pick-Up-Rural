// ============================================
// SISTEMA DE NOTIFICACIONES EN TIEMPO REAL
// Pick Up Rural - v1.0
// ============================================

class NotificacionesManager {
    constructor() {
        this.pollingInterval = null;
        this.pollingTime = 10000; // 10 segundos
        this.notificacionesVistas = new Set();
        this.init();
    }

    init() {
        console.log('🔔 Sistema de notificaciones iniciado');
        this.cargarNotificaciones();
        this.cargarListaCompleta();
        this.iniciarPolling();
        this.configurarEventListeners();
    }

    // ============================================
    // CARGA DE NOTIFICACIONES
    // ============================================

    async cargarNotificaciones() {
        try {
            const response = await fetch('/api/notificaciones/no-leidas/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.actualizarBadge(data.count);
                this.mostrarNotificacionesNuevas(data.notificaciones);
            }
        } catch (error) {
            console.error('Error al cargar notificaciones:', error);
        }
    }

    async cargarListaCompleta() {
        try {
            const response = await fetch('/api/notificaciones/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.actualizarListaDropdown(data.notificaciones);
            }
        } catch (error) {
            console.error('Error al cargar lista completa:', error);
        }
    }

    // ============================================
    // POLLING AUTOMÁTICO
    // ============================================

    iniciarPolling() {
        this.pollingInterval = setInterval(() => {
            this.cargarNotificaciones();
        }, this.pollingTime);
    }

    detenerPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }

    // ============================================
    // ACTUALIZAR UI
    // ============================================

    actualizarBadge(count) {
        const badge = document.getElementById('notificaciones-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline-flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    actualizarListaDropdown(notificaciones) {
        const lista = document.getElementById('notificaciones-lista');
        if (!lista) return;

        if (notificaciones.length === 0) {
            lista.innerHTML = `
                <div class="notificaciones-empty">
                    <div class="notificaciones-empty-icon">🔕</div>
                    <p>No hay notificaciones</p>
                </div>
            `;
            return;
        }

        lista.innerHTML = notificaciones.map(notif => `
            <div class="notificacion-item ${!notif.leida ? 'no-leida' : ''}" 
                 data-id="${notif.id}"
                 onclick="notificacionesManager.marcarComoLeida(${notif.id})">
                <div class="notificacion-icon">${this.getIconoPorTipo(notif.tipo)}</div>
                <div class="notificacion-content">
                    <div class="notificacion-titulo">${this.escapeHtml(notif.titulo)}</div>
                    <div class="notificacion-mensaje">${this.escapeHtml(notif.mensaje)}</div>
                    <div class="notificacion-fecha">${this.formatearFecha(notif.fecha_creacion)}</div>
                </div>
            </div>
        `).join('');
    }

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================

    mostrarNotificacionesNuevas(notificaciones) {
        notificaciones.forEach(notif => {
            if (!this.notificacionesVistas.has(notif.id)) {
                this.mostrarToast(notif);
                this.notificacionesVistas.add(notif.id);
            }
        });
    }

    mostrarToast(notif) {
        const toast = document.createElement('div');
        toast.className = `notificacion-toast tipo-${notif.tipo}`;
        toast.innerHTML = `
            <div class="toast-header">
                <span class="toast-icon">${this.getIconoPorTipo(notif.tipo)}</span>
                <strong>${this.escapeHtml(notif.titulo)}</strong>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="toast-body">
                ${this.escapeHtml(notif.mensaje)}
            </div>
        `;

        const container = document.getElementById('toast-container') || this.crearToastContainer();
        container.appendChild(toast);

        // Reproducir sonido
        this.reproducirSonido();

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);

        // Click para marcar como leída y cerrar
        toast.addEventListener('click', (e) => {
            if (!e.target.classList.contains('toast-close')) {
                this.marcarComoLeida(notif.id);
                toast.remove();
            }
        });
    }

    crearToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    // ============================================
    // ICONOS POR TIPO DE NOTIFICACIÓN
    // ============================================

    getIconoPorTipo(tipo) {
        const iconos = {
            'pedido_nuevo': '🛒',
            'pedido_confirmado': '✅',
            'pedido_preparando': '👨‍🍳',
            'pedido_listo': '✅',
            'pedido_en_camino': '🚚',
            'pedido_completado': '🎉',
            'pedido_cancelado': '❌',
            'stock_bajo': '⚠️',
            'sistema': '🔔'
        };
        return iconos[tipo] || '🔔';
    }

    // ============================================
    // SONIDO DE NOTIFICACIÓN
    // ============================================

    reproducirSonido() {
        try {
            // Sonido de notificación simple (beep)
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0O+2YycJC0u07tqDPw==');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('No se pudo reproducir el sonido'));
        } catch (error) {
            console.log('Audio no soportado');
        }
    }

    // ============================================
    // MARCAR COMO LEÍDA
    // ============================================

    async marcarComoLeida(notifId) {
        try {
            const response = await fetch(`/api/notificaciones/${notifId}/leer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                credentials: 'include'
            });

            if (response.ok) {
                // Recargar notificaciones
                this.cargarNotificaciones();
                this.cargarListaCompleta();
            }
        } catch (error) {
            console.error('Error al marcar como leída:', error);
        }
    }

    async marcarTodasLeidas() {
        try {
            const response = await fetch('/api/notificaciones/marcar-todas-leidas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                credentials: 'include'
            });

            if (response.ok) {
                this.cargarNotificaciones();
                this.cargarListaCompleta();
                this.actualizarBadge(0);
            }
        } catch (error) {
            console.error('Error al marcar todas como leídas:', error);
        }
    }

    // ============================================
    // EVENT LISTENERS
    // ============================================

    configurarEventListeners() {
        // Toggle dropdown al hacer click en la campana
        const bellIcon = document.getElementById('notificaciones-bell');
        if (bellIcon) {
            bellIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                const dropdown = document.getElementById('notificaciones-dropdown');
                if (dropdown) {
                    dropdown.classList.toggle('show');
                    if (dropdown.classList.contains('show')) {
                        this.cargarListaCompleta();
                    }
                }
            });
        }

        // Cerrar dropdown al hacer click fuera
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('notificaciones-dropdown');
            const container = document.querySelector('.notificaciones-container');
            
            if (dropdown && !container.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });

        // Evitar que el dropdown se cierre al hacer click dentro
        const dropdown = document.getElementById('notificaciones-dropdown');
        if (dropdown) {
            dropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Botón marcar todas como leídas
        const btnMarcarTodas = document.getElementById('marcar-todas-leidas');
        if (btnMarcarTodas) {
            btnMarcarTodas.addEventListener('click', (e) => {
                e.stopPropagation();
                this.marcarTodasLeidas();
            });
        }
    }

    // ============================================
    // UTILIDADES
    // ============================================

    formatearFecha(fechaStr) {
        const fecha = new Date(fechaStr);
        const ahora = new Date();
        const diff = ahora - fecha;
        const minutos = Math.floor(diff / 60000);
        const horas = Math.floor(diff / 3600000);
        const dias = Math.floor(diff / 86400000);

        if (minutos < 1) return 'Ahora';
        if (minutos < 60) return `Hace ${minutos} min`;
        if (horas < 24) return `Hace ${horas} hora${horas > 1 ? 's' : ''}`;
        if (dias < 7) return `Hace ${dias} día${dias > 1 ? 's' : ''}`;
        
        return fecha.toLocaleDateString('es-ES', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCookie(name) {
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
}

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si el usuario está autenticado y existe el bell icon
    const notifBell = document.getElementById('notificaciones-bell');
    if (notifBell) {
        window.notificacionesManager = new NotificacionesManager();
        console.log('✅ Sistema de notificaciones listo');
    }
});

// Detener polling cuando se cierra la página
window.addEventListener('beforeunload', () => {
    if (window.notificacionesManager) {
        window.notificacionesManager.detenerPolling();
    }
});