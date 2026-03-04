<template>
  <Particles id="tsparticles" :options="options" />
</template>

<script setup>
import Particles from "@tsparticles/vue3";

// 粒子配置项 | Particle config
const options = {
  fullScreen: { enable: true, zIndex: -1 },
  background: {
    color: "#0f0c29"
  },
  fpsLimit: 60,
  interactivity: {
    events: {
      onClick: { enable: true, mode: "push" },
      onHover: { enable: true, mode: "repulse" },
      resize: true
    },
    modes: {
      push: { quantity: 4 },
      repulse: { distance: 100, duration: 0.4 }
    }
  },
  particles: {
    color: { value: ["#00ffff", "#ff00ff"] },
    links: {
      enable: true,
      color: "#00ffff",
      distance: 150,
      opacity: 0.4,
      width: 1
    },
    move: {
      enable: true,
      speed: 1,
      direction: "none",
      outModes: { default: "out" },
      random: false
    },
    number: {
      value: 80,
      density: { enable: true, area: 800 }
    },
    opacity: { value: 0.5 },
    shape: { type: "circle" },
    size: { value: { min: 1, max: 4 } }
  },
  detectRetina: true
};
</script>
