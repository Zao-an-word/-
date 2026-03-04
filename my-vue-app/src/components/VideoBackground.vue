<template>
  <div>
    <video id="video-bg" autoplay muted loop playsinline>
      <source src="@/assets/video/whale.mp4" type="video/mp4" />
    </video>
    <div id="video-mask"></div>
  </div>
</template>

<style scoped>
#video-bg {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: -3;
}
#video-mask {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255,255,255,0.4);
  z-index: -2;
}
</style>
