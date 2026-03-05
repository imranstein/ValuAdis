<template>
  <div v-if="show" class="notification-toast" :class="notification.type">
    <div class="notification-content">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
      <button @click="hide" class="close-btn">
        <i class="pi pi-times"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  notification: {
    type: Object,
    required: true
  }
})

const show = ref(false)

// Auto-show when notification changes
watch(() => props.notification, (newNotification) => {
  if (newNotification.message) {
    show.value = true
    // Auto-hide after 5 seconds for success/info, 10 seconds for errors
    const timeout = newNotification.type === 'error' ? 10000 : 5000
    setTimeout(() => {
      hide()
    }, timeout)
  }
}, { immediate: true })

const hide = () => {
  show.value = false
}
</script>

<style scoped>
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  min-width: 300px;
  max-width: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.notification-toast.success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.notification-toast.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.notification-toast.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.notification-toast.info {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.notification-content {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 12px;
}

.notification-content i {
  font-size: 20px;
  flex-shrink: 0;
}

.notification-content span {
  flex: 1;
  font-weight: 500;
  line-height: 1.4;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  color: white;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
