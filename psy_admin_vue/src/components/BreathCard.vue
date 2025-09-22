<template>
  <div class="breath-card">
    <slot />
  </div>
</template>

<style scoped>
.breath-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px;
  transition: transform var(--transition), box-shadow var(--transition);
  animation: subtle-breathe 4s ease-in-out infinite;
}
@keyframes subtle-breathe {
  0%,
  100% {
    box-shadow: 0 8px 16px rgba(125, 185, 212, 0.12);
  }
  50% {
    box-shadow: 0 12px 24px rgba(125, 185, 212, 0.18);
  }
}
.breath-card:hover {
  transform: scale(1.03);
  animation: none;
}
.breath-card:hover {
  transform: scale(1.03);
  box-shadow: 0 12px 24px rgba(125, 185, 212, 0.18);
}
</style>
<script setup>
import { useMotion } from "@vueuse/motion";

useMotion(".breath-card", {
  initial: { opacity: 0, y: 30 },
  enter: { opacity: 1, y: 0, transition: { duration: 400 } },
});
</script>
