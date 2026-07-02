<script setup lang="ts">
import { onMounted } from "vue";
import { useCartStore } from "./stores/cart";
import ToastNotification from "./components/ToastNotification.vue";

const cartStore = useCartStore();

onMounted(() => {
  cartStore.fetchCart();
});
</script>

<template>
  <router-view></router-view>
  <ToastNotification />
</template>

<style>
/* Global styles can go here if needed */
</style>
