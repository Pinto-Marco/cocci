<template>
  <Transition name="toast">
    <div v-if="toastStore.visible" class="toast-notification">
      {{ toastStore.message }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useToastStore } from "../stores/toast";

const toastStore = useToastStore();
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #333;
  color: #fff;
  border-right: 1px solid #000;
  padding: 1rem 2rem;
  border-radius: 4px;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-family: "Inter", sans-serif;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
