import { defineStore } from "pinia";

export const useToastStore = defineStore("toast", {
  state: () => ({
    message: "",
    visible: false,
    timeoutId: null as number | null,
  }),
  actions: {
    show(message: string, duration = 3000) {
      this.message = message;
      this.visible = true;

      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }

      this.timeoutId = setTimeout(() => {
        this.visible = false;
        this.timeoutId = null;
      }, duration);
    },
    hide() {
      this.visible = false;
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
        this.timeoutId = null;
      }
    },
  },
});
