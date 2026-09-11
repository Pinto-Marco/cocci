<template>
  <div class="hero">
    <div style="position: relative; width: 100%">
      <video
        class="hero-media"
        :poster="skip ? LAST : FIRST"
        :autoplay="!skip"
        :preload="skip ? 'none' : 'auto'"
        muted
        playsinline
        disablepictureinpicture
        aria-label="Cocci Archivio logo animation"
      >
        <source :src="WEBM" type="video/webm" />
        <source :src="MP4" type="video/mp4" />
      </video>
      <div
        style="
          width: 100%;
          background-color: var(--color-bg);
          z-index: 10;
          padding: 1rem 2rem;
        "
      >
        <h1 style="border-bottom: 1px solid var(--color-border)">
          Cocci Archivio
        </h1>
        <p style="font-size: 1.4rem">
          Cocci Archivio was launched in 2021 with the goal of researching and
          selecting the finest vintage garments from every corner of the world.
        </p>

        <p style="font-size: 1.4rem">
          Showcasing the history of clothing is perhaps at the core of Cocci's
          attention, in fact every single garment is one of a kind and has a
          story to tell, a past that is sometimes visible on the material itself
          and that tells about its previous uses: the signs of time in this
          sense enrich the garment, giving it a uniqueness that only vintage
          pieces can have. The ethics of vintage is to value time, people and
          quality without embracing the fast-fashion culture.
        </p>

        <p style="font-size: 1.4rem">
          We have digitized over 1,500 garments across a wide range of
          categories, including military, denim, collegiate, workwear, leather,
          and many more. The archive is constantly growing, with new additions
          made daily.
        </p>

        <p style="font-size: 1.4rem">
          Located in the nearby of Bologna (ITA), the showroom direction is
          operated by founder Giulio Marchioni.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Bound (not literal) so Vite treats these as runtime URLs, not build-time imports.
const WEBM = "/static/dist/animation/hero.webm";
const MP4 = "/static/dist/animation/hero.mp4";
const FIRST = "/static/dist/animation/hero-first.webp";
const LAST = "/static/dist/animation/hero-last.webp";

// Plays once per tab session; afterwards (or under reduced-motion) the poster
// alone shows the final frame and `preload="none"` skips the download entirely.
let seen = false;
try {
  seen = sessionStorage.getItem("heroSeen") === "1";
  sessionStorage.setItem("heroSeen", "1");
} catch {
  // ponytail: sessionStorage throws in some privacy modes; animation just replays
}
const skip =
  seen || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
</script>

<style scoped>
/* Scoped styles if needed, otherwise uses global main.css */
</style>
