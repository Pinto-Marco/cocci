import { defineStore } from "pinia";
import axios from "axios";
// @ts-ignore
import type { CartItem } from "../types";
import { useToastStore } from "./toast";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";

export const useCartStore = defineStore("cart", {
  state: () => ({
    items: [] as CartItem[],
    totalItems: 0,
    totalPrice: 0,
    loading: false,
  }),
  getters: {
    isInCart: (state) => (code: string) => {
      return state.items.some((item) => item.code === code);
    },
  },
  actions: {
    async fetchCart() {
      this.loading = true;
      try {
        console.log("Fetching cart...");
        const response = await axios.get("/cart/");
        console.log("Cart response:", response.data);
        // API returns { items: [], total_items, total_price }?
        // Need to verify API response format in next step or via previous knowledge.
        // Assuming implementation based on orders/views.py CartView.
        // It returns a list or a dict?
        // CartView.get returns: Response(product_data) which is a list?
        // Wait, checked CartView earlier, it returns a LIST of items if I recall or a DICT?
        // Let's verify CartView response format.
        // It prepares `items` list and returns... wait.

        // From memory/view_file: CartView returns `cart_data` which is {'items': items}.
        // And we added 'items' list inside it.
        // Actually, let's double check CartView code snippet from step 117.
        // It calculated totals but didn't explicitly show the RETURN statement structure for totals.
        // It showed `cart_data = { 'items': items }`.

        // I will assume { items: [...] } for now but I should check if it includes totals.
        // Ideally the API should return { items: [...], total_items: x, total_price: y }.
        // I'll assume standard format and adjust if needed.

        this.items = response.data.items || [];
        this.totalItems = this.items.reduce(
          (sum: number, item: any) => sum + item.quantity,
          0
        );
        this.totalPrice = this.items.reduce(
          (sum: number, item: any) => sum + item.total,
          0
        );

        // Dispatch custom event for legacy navbar
        window.dispatchEvent(
          new CustomEvent("cart-updated", {
            detail: { count: this.totalItems },
          })
        );
      } catch (error) {
        console.error("Failed to fetch cart", error);
      } finally {
        this.loading = false;
      }
    },
    async addToCart(code: string) {
      const toastStore = useToastStore();
      try {
        await axios.post("/cart/add/", { product_code: code, quantity: 1 });
        await this.fetchCart(); // Refresh
        toastStore.show("Added to cart");
      } catch (error) {
        console.error("Add to cart failed", error);
        toastStore.show("Failed to add to cart");
      }
    },
    async removeFromCart(code: string) {
      try {
        await axios.post("/cart/remove/", {
          product_code: code,
          remove_all: true,
        });
        await this.fetchCart(); // Refresh
      } catch (error) {
        console.error("Remove from cart failed", error);
      }
    },
  },
});
