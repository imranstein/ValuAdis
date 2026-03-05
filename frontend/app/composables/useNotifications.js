import { ref } from 'vue'

const notifications = ref([])

export function useNotifications() {
  const showNotification = (message, type = 'info', options = {}) => {
    const notification = {
      id: Date.now() + Math.random(),
      message,
      type, // success, error, warning, info
      icon: options.icon || getDefaultIcon(type),
      duration: options.duration || getDefaultDuration(type),
      ...options
    }
    
    notifications.value.push(notification)
    
    // Auto-remove after duration
    setTimeout(() => {
      removeNotification(notification.id)
    }, notification.duration)
    
    return notification.id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message, options = {}) => showNotification(message, 'success', options)
  const error = (message, options = {}) => showNotification(message, 'error', options)
  const warning = (message, options = {}) => showNotification(message, 'warning', options)
  const info = (message, options = {}) => showNotification(message, 'info', options)

  return {
    notifications,
    showNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
}

function getDefaultIcon(type) {
  const icons = {
    success: 'pi pi-check-circle',
    error: 'pi pi-exclamation-circle',
    warning: 'pi pi-exclamation-triangle',
    info: 'pi pi-info-circle'
  }
  return icons[type] || icons.info
}

function getDefaultDuration(type) {
  const durations = {
    success: 5000,
    error: 10000,
    warning: 7000,
    info: 5000
  }
  return durations[type] || durations.info
}
