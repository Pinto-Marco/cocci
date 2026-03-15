<template>
  <div class="cart-summary">
    <div
      class="checkout-tile"
      style="padding: 2rem 2rem 1rem 2rem; font-size: 2rem; font-weight: 900"
    >
      Summary
    </div>
    <div class="checkout-tile">Number of items: {{ cartStore.totalItems }}</div>
    <div
      class="checkout-tile"
      style="border-bottom: 1px solid #000; padding-bottom: 2rem"
    >
      Total price: €{{ cartStore.totalPrice }} EUR
    </div>

    <form @submit.prevent="submitOrder" style="width: 100%">
      <div class="checkout-tile" style="border-bottom: 1px solid #000">
        <input
          type="email"
          v-model="email"
          placeholder="Email..."
          style="
            outline: none;
            border: none;
            background: none;
            font-size: 1.2rem;
            width: 100%;
            padding: 1rem 0;
          "
          required
        />
      </div>
      <div
        class="checkout-tile"
        style="padding: 2rem; border-bottom: 1px solid #000"
      >
        We'll send your order confirmation to this email.
      </div>

      <div style="display: flex; flex-direction: row; width: 100%">
        <router-link
          to="/cart/summary"
          class="checkout-btn"
          style="border-right: none; border-left: none"
        >
          Back to Cart
        </router-link>
        <button
          type="submit"
          class="checkout-btn"
          style="border-right: none"
          :disabled="loading"
        >
          {{ loading ? "Processing..." : "Place Order" }}
        </button>
      </div>
    </form>

    <div v-if="error" style="color: red; padding: 1rem">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCartStore } from "../stores/cart";
import axios from "axios";

const cartStore = useCartStore();
const router = useRouter();

const email = ref("");
const loading = ref(false);
const error = ref("");

const submitOrder = async () => {
  loading.value = true;
  error.value = "";
  try {
    const response = await axios.post("/cart/make-checkout/", {
      email: email.value,
    });
    // Clear cart store locally as backend cleared it
    cartStore.items = [];
    cartStore.totalItems = 0;
    cartStore.totalPrice = 0;

    router.push({
      name: "OrderConfirmation",
      query: {
        id: response.data.order_id,
        total: response.data.total,
      },
    });
  } catch (err: any) {
    console.error("Checkout failed", err);
    error.value = err.response?.data?.error || "Checkout failed";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  cartStore.fetchCart();
});
</script>

<style scoped>
/* Inherit from main.css */
</style>
