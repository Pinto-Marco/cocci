<template>
  <router-link
    :to="`/products/details/${product.code}`"
    class="product-card-link"
    style="text-decoration: none"
  >
    <div
      class="product-card"
      @mouseenter="startCarousel"
      @mouseleave="stopCarousel"
    >
      <div class="skeleton-container">
        <div v-if="!isLoaded" class="skeleton"></div>
        <img
          v-if="mainImage"
          :src="currentDisplayImage"
          :alt="product.title"
          class="product-card__image"
          :class="{ 'is-loaded': isLoaded }"
          loading="lazy"
          decoding="async"
          @load="onImageLoad"
        />
        <img
          v-else
          src="https://via.placeholder.com/400?text=No+Image"
          :alt="product.title"
          class="product-card__image is-loaded"
        />
      </div>

      <div class="product-card__meta">
        <div class="product-card__title-wrapper">
          <h3 class="product-card__title" style="color: #000">
            {{ product.title }}
          </h3>
        </div>

        <button
          v-if="isInCart"
          class="add-to-cart-btn-selected"
          @click.prevent="removeFromCart"
        >
          <svg
            width="28"
            height="28"
            viewBox="0 0 24 24"
            style="margin-top: 0.3rem"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="currentColor"
              d="m9.55 18l-5.7-5.7l1.425-1.425L9.55 15.15l9.175-9.175L20.15 7.4z"
            />
          </svg>
        </button>

        <button
          v-else-if="!product.is_available"
          class="add-to-cart-btn-disabled"
          disabled
        >
          \
        </button>

        <button v-else class="add-to-cart-btn" @click.prevent="addToCart">
          +
        </button>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";
import type { Product } from "../types";
import { useCartStore } from "../stores/cart";

const props = defineProps<{
  product: Product;
}>();

const cartStore = useCartStore();

// Image Loading State
const isLoaded = ref(false);
const onImageLoad = () => {
  isLoaded.value = true;
};

// Main Image logic
const mainImage = computed(() => {
  if (props.product.images?.length) {
    return props.product.images[0]?.image;
  }
  return "";
});

// Carousel Logic (Deferred)
const currentImageIndex = ref(0);
let intervalId: number | null = null;
const isHovered = ref(false);

const carouselImages = computed(() => {
  if (!isHovered.value) return []; // Don't even compute if not hovered
  if (props.product.images && props.product.images.length > 0) {
    return props.product.images.map((img) => img.image);
  }
  return [];
});

const currentDisplayImage = computed(() => {
  if (isHovered.value && carouselImages.value.length > 0) {
    return carouselImages.value[currentImageIndex.value];
  }
  return mainImage.value;
});

const startCarousel = () => {
  if (!props.product.images || props.product.images.length <= 1) return;
  isHovered.value = true;

  // Initialize carousel with the first image, then cycle
  currentImageIndex.value = 1;

  intervalId = window.setInterval(() => {
    currentImageIndex.value =
      (currentImageIndex.value + 1) % props.product.images.length;
  }, 1200);
};

const stopCarousel = () => {
  if (intervalId) clearInterval(intervalId);
  intervalId = null;
  currentImageIndex.value = 0;
  isHovered.value = false;
};

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});

// Cart Logic
const isInCart = computed(() => cartStore.isInCart(props.product.code));

const addToCart = async () => {
  await cartStore.addToCart(props.product.code);
};

const removeFromCart = async () => {
  await cartStore.removeFromCart(props.product.code);
};
</script>
