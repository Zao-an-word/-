<template>
  <div id="app">
    <router-view /> <!-- 🌐 所有页面组件的出口 -->

    <!-- 全局粒子效果 -->
    <SakuraTail />
  </div>

</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 全局背景、字体等样式可在这里配置 */
body, html, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Segoe UI', sans-serif;
}
</style>
