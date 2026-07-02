<template>
  <div v-if="cartStore.items.length > 0">
    <div class="cart-summary">
      <div v-for="item in cartStore.items" :key="item.code" class="cart-card">
        <img
          :src="item.image"
          alt="product_image"
          style="width: 10rem; object-fit: cover"
        />
        <div class="cart-card-title">
          <span style="font-size: 1.6rem; font-weight: 900">
            {{ item.title }}
          </span>
          <div>
            <div style="margin-bottom: 0.5rem; font-size: 1.2rem">
              {{ item.price }}€
            </div>
            <span v-if="item.penalty" style="opacity: 0.6">
              Penalty fee: {{ item.penalty }}€
            </span>
          </div>
        </div>
        <div class="cart-card-controls">
          <button
            class="qty-button"
            @click="cartStore.removeFromCart(item.code)"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path fill="currentColor" d="M5 13v-2h14v2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <router-link to="/cart/checkout" class="checkout-btn">
      Checkout - {{ cartStore.totalPrice }} EUR
    </router-link>
  </div>

  <div v-else class="checkout-btn" style="padding: 2rem">
    Your cart is empty...
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useCartStore } from "../stores/cart";

const cartStore = useCartStore();

onMounted(() => {
  cartStore.fetchCart();
});
</script>

<style scoped>
/* Inherit from main.css */
</style>
