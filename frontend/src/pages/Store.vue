<template>
  <div>
    <!-- Utility Bar -->
    <section class="utility-bar">
      <div class="utility-bar__left" style="display: flex; color: #000">
        <button
          id="filterBtn"
          class="utility-bar__button"
          @click="toggleFilters"
        >
          FILTERS
        </button>
        <div
          v-if="selectedTags.length > 0"
          id="clear-filters"
          @click="clearFilters"
          style="
            color: #000;
            cursor: pointer;
            height: 18px;
            margin-left: 0.5rem;
          "
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="currentColor"
              d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12z"
            />
          </svg>
        </div>
      </div>

      <div class="search-box">
        <input
          v-model="searchQuery"
          type="search"
          class="search-box__input"
          placeholder="Search products..."
          style="text-align: center"
          autocomplete="off"
          @focus="onSearchFocus"
          @input="onSearchInput"
          @keydown.esc="closeSearchDropdown"
          @keydown.enter.prevent="goToFirstSearchResult"
        />

        <div v-if="showSearchDropdown" class="search-box__dropdown">
          <button
            v-for="result in productStore.searchResults"
            :key="result.code"
            class="search-box__item"
            @click="goToProduct(result.code)"
          >
            <span class="search-box__item-title">{{ result.title }}</span>
            <span
              v-if="result.description"
              class="search-box__item-description"
            >
              {{ truncateDescription(result.description) }}
            </span>
          </button>

          <div
            v-if="
              !productStore.searchLoading &&
              productStore.searchResults.length === 0
            "
            class="search-box__empty"
          >
            No matches found.
          </div>
        </div>
      </div>

      <button id="sortBtn" class="utility-bar__button" @click="toggleSort">
        SORT
      </button>
    </section>

    <!-- Filter Panel -->
    <section
      id="filterPanel"
      class="filter-panel"
      :class="{ open: filtersOpen }"
    >
      <button
        v-for="tag in productStore.tags"
        :key="tag"
        :class="[
          'filter-panel__tag',
          { 'is-selected': selectedTags.includes(tag) },
        ]"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
    </section>

    <!-- Sort Menu -->
    <section id="sortMenu" class="sort-menu" :class="{ open: sortOpen }">
      <button
        @click="setSort('price_asc')"
        :class="{ 'is-selected': currentSort === 'price_asc' }"
      >
        Low → High $
      </button>
      <button
        @click="setSort('price_desc')"
        :class="{ 'is-selected': currentSort === 'price_desc' }"
      >
        High → Low $
      </button>
      <button
        @click="setSort('year_desc')"
        :class="{ 'is-selected': currentSort === 'year_desc' }"
      >
        Newest
      </button>
      <button
        @click="setSort('year_asc')"
        :class="{ 'is-selected': currentSort === 'year_asc' }"
      >
        Oldest
      </button>
    </section>

    <!-- Product Grid -->
    <section id="productGrid" class="product-grid">
      <ProductCard
        v-for="product in productStore.products"
        :key="product.id"
        :product="product"
      />

      <p
        v-if="productStore.products.length === 0 && !productStore.loading"
        class="empty-state"
      >
        No products match your criteria.
      </p>
    </section>

    <!-- Pagination -->
    <div class="pagination" v-if="productStore.totalPages > 1">
      <button
        v-if="productStore.currentPage > 1"
        @click="goToPage(1)"
        class="pagination__nav"
      >
        First
      </button>

      <button
        v-if="productStore.previousPage"
        @click="changePage(productStore.previousPage)"
        class="pagination__nav"
      >
        Prev
      </button>

      <div class="pagination__numbers">
        <button
          v-for="page in pageNumbers"
          :key="page"
          :class="[
            'pagination__number',
            { 'is-active': page === productStore.currentPage },
          ]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </div>

      <button
        v-if="productStore.nextPage"
        @click="changePage(productStore.nextPage)"
        class="pagination__nav"
      >
        Next
      </button>

      <button
        v-if="productStore.currentPage < productStore.totalPages"
        @click="goToPage(productStore.totalPages)"
        class="pagination__nav"
      >
        Last
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useProductStore } from "../stores/products";
import { useCartStore } from "../stores/cart";
import ProductCard from "../components/ProductCard.vue";

const productStore = useProductStore();
const cartStore = useCartStore();
const router = useRouter();
const route = useRoute();

const filtersOpen = ref(false);
const sortOpen = ref(false);
const searchQuery = ref("");
const searchDropdownOpen = ref(false);
let searchDebounceTimer: number | null = null;

const selectedTags = ref<string[]>([]);
const currentSort = ref<string | null>(null);

const showSearchDropdown = computed(() => {
  return searchDropdownOpen.value && searchQuery.value.trim().length >= 2;
});

const pageNumbers = computed(() => {
  const current = productStore.currentPage;
  const total = productStore.totalPages;
  if (total <= 1) return [];

  let start = Math.max(1, current - 1);
  let end = Math.min(total, current + 1);

  if (current === 1) {
    end = Math.min(total, 3);
  } else if (current === total) {
    start = Math.max(1, total - 2);
  }

  const pages = [];
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
});

// Initialize from URL
const initFromUrl = () => {
  const tagsParam = route.query.tags as string;
  if (tagsParam) {
    selectedTags.value = tagsParam.split(",").filter((t) => t);
    filtersOpen.value = true;
  } else {
    selectedTags.value = [];
  }

  currentSort.value = (route.query.sort as string) || null;
  console.log(currentSort.value);
};

const fetchData = () => {
  const params: any = {};
  if (selectedTags.value.length > 0) {
    params.tags = selectedTags.value.join(",");
  }
  if (currentSort.value) {
    params.sort = currentSort.value;
  }
  params.page = route.query.page || 1;

  productStore.fetchProducts(params);
};

const updateUrl = (resetPage = false) => {
  const query: any = { ...route.query };
  if (selectedTags.value.length > 0) {
    query.tags = selectedTags.value.join(",");
  } else {
    delete query.tags;
  }

  if (currentSort.value) {
    query.sort = currentSort.value;
  } else {
    delete query.sort;
  }

  if (resetPage) {
    delete query.page;
  }

  router.push({ query });
};

const toggleFilters = () => {
  filtersOpen.value = !filtersOpen.value;
};

const toggleSort = () => {
  sortOpen.value = !sortOpen.value;
};

const closeSearchDropdown = () => {
  searchDropdownOpen.value = false;
};

const onSearchFocus = () => {
  if (searchQuery.value.trim().length >= 2) {
    searchDropdownOpen.value = true;
  }
};

const onSearchInput = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer);
  }

  const query = searchQuery.value.trim();

  if (query.length < 2) {
    productStore.clearSearchResults();
    searchDropdownOpen.value = false;
    return;
  }

  searchDropdownOpen.value = true;

  searchDebounceTimer = window.setTimeout(async () => {
    await productStore.searchProducts(query, 8);
  }, 250);
};

const goToProduct = (code: string) => {
  searchQuery.value = "";
  closeSearchDropdown();
  productStore.clearSearchResults();
  router.push(`/products/details/${code}`);
};

const goToFirstSearchResult = () => {
  const firstResult = productStore.searchResults[0];
  if (!firstResult) {
    return;
  }
  goToProduct(firstResult.code);
};

const truncateDescription = (description: string) => {
  const normalized = description.trim();
  if (normalized.length <= 80) {
    return normalized;
  }
  return `${normalized.slice(0, 80)}...`;
};

const toggleTag = (tag: string) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter((t) => t !== tag);
  } else {
    selectedTags.value.push(tag);
  }
  updateUrl(true);
};

const clearFilters = () => {
  selectedTags.value = [];
  updateUrl(true);
  filtersOpen.value = false;
};

const setSort = (sort: string) => {
  if (currentSort.value === sort) {
    currentSort.value = null; // Toggle off?
  } else {
    currentSort.value = sort;
  }
  sortOpen.value = false;
  updateUrl(true);
};

const changePage = (url: string) => {
  try {
    const urlObj = new URL(url);
    const page = urlObj.searchParams.get("page");
    if (page) {
      router.push({ query: { ...route.query, page } });
    } else {
      // If no page param, it might be the first page
      const query = { ...route.query };
      delete query.page;
      router.push({ query });
    }
  } catch (e) {
    console.error("Invalid pagination URL", url);
  }
};

const goToPage = (page: number) => {
  if (page === 1) {
    const query = { ...route.query };
    delete query.page;
    router.push({ query });
  } else {
    router.push({ query: { ...route.query, page } });
  }
};

watch(
  () => route.query,
  () => {
    initFromUrl();
    fetchData();
  },
);

onMounted(async () => {
  document.addEventListener("click", handleClickOutsideSearch);
  await productStore.fetchTags();
  await cartStore.fetchCart(); // Needed for "selected" state in cards
  initFromUrl();
  fetchData();
});

const handleClickOutsideSearch = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest(".search-box")) {
    closeSearchDropdown();
  }
};

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer);
  }
  document.removeEventListener("click", handleClickOutsideSearch);
  productStore.clearSearchResults();
});
</script>

<style scoped>
/* Inherits main.css but we can add overrides if needed */
.pagination__nav {
  cursor: pointer;
  background: none;
  border: 1px solid var(--color-border);
  padding: 1rem 1.5rem;
  font-family: var(--font-base);
  font-size: 1.3rem;
  letter-spacing: 0.05em;
  transition: all 0.3s ease;
}

.pagination__nav:hover {
  background: var(--color-accent);
  color: #fff;
}

.pagination__numbers {
  display: flex;
  gap: 0.5rem;
}

.pagination__number {
  background: none;
  border: 1px solid var(--color-border);
  padding: 1rem 1.5rem;
  cursor: pointer;
  font-family: var(--font-base);
  font-size: 1.3rem;
  transition: all 0.3s ease;
}

.pagination__number:hover {
  background: #000;
  color: #fff;
}

.pagination__number.is-active {
  background: #000;
  color: #fff;
  cursor: default;
}
</style>
