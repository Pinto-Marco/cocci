<template>
  <div class="cart-summary">
    <div
      class="checkout-tile"
      style="padding: 2rem 2rem 1rem 2rem; font-size: 2rem; font-weight: 900"
    >
      Order Confirmed
    </div>
    <div class="checkout-tile">
      Order ID: <strong>{{ orderId }}</strong>
    </div>
    <div
      class="checkout-tile"
      style="border-bottom: 1px solid #000; padding-bottom: 2rem"
    >
      Total: <strong>{{ total }} EUR</strong>
    </div>
    <router-link
      to="/archive"
      class="checkout-btn"
      style="border-left: none; border-right: none"
    >
      Shop Again
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const orderId = computed(() => route.query.id);
const total = computed(() => route.query.total);
</script>

<style scoped>
/* Inherit from main.css */
</style>
