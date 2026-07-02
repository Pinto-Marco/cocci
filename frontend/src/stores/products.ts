import { defineStore } from "pinia";
import axios from "axios";
import type { Product, ProductSearchResult } from "../types";

export const useProductStore = defineStore("products", {
  state: () => ({
    products: [] as Product[],
    tags: [] as string[],
    count: 0,
    loading: false,
    searchLoading: false,
    searchResults: [] as ProductSearchResult[],
    nextPage: null as string | null,
    previousPage: null as string | null,
    currentPage: 1,
    totalPages: 1,
  }),
  actions: {
    async fetchTags() {
      try {
        const response = await axios.get("/products/tags/");
        this.tags = response.data;
      } catch (error) {
        console.error("Failed to fetch tags", error);
      }
    },
    async fetchProducts(params: any = {}) {
      this.loading = true;
      try {
        const response = await axios.get("/products/", { params });
        this.products = response.data.results;
        this.count = response.data.count;
        this.nextPage = response.data.next;
        this.previousPage = response.data.previous;
        this.currentPage = response.data.current_page || 1;
        this.totalPages = response.data.total_pages || 1;
      } catch (error) {
        console.error("Failed to fetch products", error);
      } finally {
        this.loading = false;
      }
    },
    async searchProducts(query: string, limit = 8) {
      const normalizedQuery = query.trim();

      if (!normalizedQuery) {
        this.searchResults = [];
        return;
      }

      this.searchLoading = true;
      try {
        const response = await axios.get("/products/search/", {
          params: {
            q: normalizedQuery,
            limit,
          },
        });
        this.searchResults = response.data.results || [];
      } catch (error) {
        this.searchResults = [];
        console.error("Failed to search products", error);
      } finally {
        this.searchLoading = false;
      }
    },
    clearSearchResults() {
      this.searchResults = [];
      this.searchLoading = false;
    },
  },
});
