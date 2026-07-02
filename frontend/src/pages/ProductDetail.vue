<template>
  <div class="container mt-5" v-if="product">
    <div v-if="images.length > 0" class="carousel-container">
      <div class="carousel-track">
        <div
          v-for="(image, index) in images"
          :key="index"
          :class="['card', getCardClass(index)]"
          @click="updateCarousel(index)"
        >
          <img :src="image" :alt="'Product image ' + index" />
        </div>
      </div>
    </div>

    <div v-else class="carousel-item active">
      <img
        src="https://via.placeholder.com/500x500.png?text=No+Image+Available"
        class="d-block w-100"
        alt="No image available"
      />
    </div>

    <div
      v-if="images.length > 0"
      style="
        display: flex;
        flex-direction: row;
        width: 100%;
        border-top: 1px solid #000;
        border-bottom: 1px solid #000;
      "
    >
      <div class="controls">
        <button
          class="nav-arrow left checkout-btn"
          style="border-right: none; width: 100%"
          @click="prevSlide"
        >
          Previous
        </button>
        <button
          class="nav-arrow right checkout-btn"
          style="border-right: none"
          @click="nextSlide"
        >
          Next
        </button>
      </div>
    </div>

    <div style="margin: 2rem 3rem">
      <div
        style="
          display: flex;
          direction: ltr;
          justify-content: space-between;
          align-items: end;
        "
      >
        <h1>{{ product.title }}</h1>
        <div style="display: flex; flex-direction: column; align-items: end">
          <p style="font-weight: bold; margin: 0; font-size: 2rem">
            Rental Fee: €{{ product.price }}
          </p>
          <p v-if="product.penalty" style="margin: 0; font-size: small">
            (Penalty Fee: €{{ product.penalty }})
          </p>
        </div>
      </div>
      <p style="font-size: larger">{{ product.description }}</p>
    </div>

    <button
      class="checkout-btn product-details-add-to-cart"
      style="padding: 1rem; border-top: 1px solid #000"
      @click="handleAddToCart"
      :disabled="!product.is_available"
    >
      {{ !product.is_available ? "Out of Stock" : "Add To Cart" }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCartStore } from "../stores/cart";
import axios from "axios";
import type { Product } from "../types";

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();

const product = ref<Product | null>(null);
const images = computed(() => {
  if (product.value?.images) {
    return product.value.images.map((img: any) => img.image);
  }
  return [];
});

const currentIndex = ref(0);
const code = route.params.code as string;

const fetchProduct = async () => {
  try {
    const response = await axios.get(`/products/api/details/${code}/`);
    product.value = response.data;
  } catch (e) {
    console.error("Failed to fetch product", e);
  }
};

const handleAddToCart = async () => {
  if (product.value) {
    await cartStore.addToCart(product.value.code);
    router.push("/cart/summary");
  }
};

// Carousel Logic
const getCardClass = (index: number) => {
  const total = images.value.length;
  const offset = (index - currentIndex.value + total) % total;

  if (offset === 0) return "center";
  if (offset === 1) return "right-1";
  if (offset === total - 1) return "left-1";
  return "hidden";
};

const updateCarousel = (index: number) => {
  const total = images.value.length;
  currentIndex.value = (index + total) % total;
};

const nextSlide = () => {
  updateCarousel(currentIndex.value + 1);
};

const prevSlide = () => {
  updateCarousel(currentIndex.value - 1);
};

onMounted(() => {
  fetchProduct();
});
</script>

<style scoped>
/* Scoped styles logic if needed, currently inheriting from main.css */
.carousel-container {
  height: 400px; /* Approximate based on legacy behavior */
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}
.carousel-track {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.card {
  position: absolute;
  transition: all 0.5s ease;
  opacity: 0;
  /* Add specific dimensions if not in main.css */
}
.card.center {
  opacity: 1;
  z-index: 10;
  transform: translateX(0) scale(1);
}
.card.left-1 {
  opacity: 0.5;
  z-index: 5;
  transform: translateX(-50%) scale(0.8);
}
.card.right-1 {
  opacity: 0.5;
  z-index: 5;
  transform: translateX(50%) scale(0.8);
}
.card.hidden {
  opacity: 0;
  pointer-events: none;
}
</style>
