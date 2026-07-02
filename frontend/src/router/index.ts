import { createRouter, createWebHistory } from "vue-router";

// We will add routes as we migrate pages
const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../pages/Home.vue"),
  },
  {
    path: "/contacts",
    name: "Contacts",
    component: () => import("../pages/Contacts.vue"),
  },
  {
    path: "/archive",
    name: "Store",
    component: () => import("../pages/Store.vue"),
  },
  {
    path: "/products/details/:code",
    name: "ProductDetail",
    component: () => import("../pages/ProductDetail.vue"),
  },
  {
    path: "/cart/summary",
    name: "Cart",
    component: () => import("../pages/Cart.vue"),
  },
  {
    path: "/cart/checkout",
    name: "Checkout",
    component: () => import("../pages/Checkout.vue"),
  },
  {
    path: "/order-confirmation",
    name: "OrderConfirmation",
    component: () => import("../pages/OrderConfirmation.vue"),
  },
  // Add other routes here
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
