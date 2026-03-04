<template>
  <div class="cherry-blossoms-container" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script>
export default {
  name: 'CherryBlossomsEffect',
  props: {
    // 花瓣数量（粒子总数）
    particleCount: {
      type: Number,
      default: 30
    },
    // 拖尾长度（最大记录轨迹点数）
    trailLength: {
      type: Number,
      default: 15
    }
  },
  data() {
    return {
      canvas: null,
      ctx: null,
      particles: [],
      mouse: { x: null, y: null },
      trailPoints: [],
      animationId: null,
      isMouseMoving: false,     // 是否正在移动
      moveTimer: null           // 停止移动的计时器
    };
  },
  mounted() {
    this.initCanvas();
    this.createParticles();
    this.startAnimation();

    window.addEventListener('mousemove', this.handleMouseMove);
    window.addEventListener('resize', this.resizeCanvas);
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.handleMouseMove);
    window.removeEventListener('resize', this.resizeCanvas);
    if (this.animationId) cancelAnimationFrame(this.animationId);
  },
  methods: {
    // 初始化Canvas
    initCanvas() {
      this.canvas = this.$refs.canvas;
      this.ctx = this.canvas.getContext('2d');
      this.resizeCanvas();
    },

    // 调整Canvas大小
    resizeCanvas() {
      const container = this.$refs.container;
      this.canvas.width = container.clientWidth;
      this.canvas.height = container.clientHeight;
    },

    // 创建初始粒子
    createParticles() {
      for (let i = 0; i < this.particleCount; i++) {
        this.particles.push(this.createParticle());
      }
    },

    // 创建一个粒子
    createParticle() {
      return {
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        size: Math.random() * 3 + 1.5,
        opacity: Math.random() * 0.8 + 0.2,
        angle: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.3 + 0.1,
        rotation: (Math.random() - 0.5) * 0.05,
        color: this.getCherryColor()
      };
    },

    // 获取随机樱花颜色
    getCherryColor() {
      const colors = [
        'rgba(255, 192, 203, ',
        'rgba(255, 182, 193, ',
        'rgba(255, 174, 185, ',
        'rgba(255, 158, 172, ',
        'rgba(255, 145, 160, '
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    },

    // 鼠标移动事件
    handleMouseMove(e) {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
      this.isMouseMoving = true;

      this.trailPoints.unshift({ x: this.mouse.x, y: this.mouse.y });

      if (this.trailPoints.length > this.trailLength) {
        this.trailPoints.pop();
      }

      // 设置100ms内没有新移动则认为停止
      if (this.moveTimer) clearTimeout(this.moveTimer);
      this.moveTimer = setTimeout(() => {
        this.isMouseMoving = false;
      }, 100);
    },

    // 更新粒子
    updateParticles() {
      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];
        p.angle += p.rotation;
        p.x += Math.cos(p.angle) * p.speed;
        p.y += Math.sin(p.angle) * p.speed + 0.3;
        p.opacity -= 0.003;

        if (p.y > this.canvas.height || p.opacity <= 0) {
          this.resetParticle(p);
        }
      }

      // 仅在鼠标移动时生成拖尾粒子
      if (this.isMouseMoving && this.mouse.x !== null && this.mouse.y !== null) {
        for (let i = 0; i < this.trailPoints.length; i++) {
          const point = this.trailPoints[i];
          if (i % 3 === 0) {
            const particle = this.createParticle();
            particle.x = point.x + (Math.random() * 10 - 5);
            particle.y = point.y + (Math.random() * 10 - 5);
            particle.opacity = 0.8 - (i * 0.05);
            this.particles.push(particle);
          }
        }

        // 限制总粒子数量
        if (this.particles.length > this.particleCount + this.trailLength) {
          this.particles.splice(0, this.particles.length - (this.particleCount + this.trailLength));
        }
      }
    },

    // 重置粒子
    resetParticle(p) {
      p.x = Math.random() * this.canvas.width;
      p.y = -10;
      p.size = Math.random() * 3 + 1.5;
      p.opacity = Math.random() * 0.8 + 0.2;
      p.angle = Math.random() * Math.PI * 2;
      p.speed = Math.random() * 0.3 + 0.1;
      p.rotation = (Math.random() - 0.5) * 0.05;
      p.color = this.getCherryColor();
    },

    // 绘制所有粒子
    drawParticles() {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];
        this.ctx.beginPath();

        // 绘制花瓣路径
        this.ctx.moveTo(p.x, p.y);
        this.ctx.bezierCurveTo(
            p.x + p.size, p.y - p.size,
            p.x + p.size * 2, p.y + p.size / 2,
            p.x, p.y + p.size
        );
        this.ctx.bezierCurveTo(
            p.x - p.size * 2, p.y + p.size / 2,
            p.x - p.size, p.y - p.size,
            p.x, p.y
        );

        const gradient = this.ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
        gradient.addColorStop(0, p.color + '1)');
        gradient.addColorStop(1, p.color + (p.opacity * 0.5) + ')');

        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.closePath();

        // 添加阴影 glow
        this.ctx.shadowColor = 'rgba(255, 192, 203, 0.4)';
        this.ctx.shadowBlur = 10;
      }
    },

    // 动画循环
    animate() {
      this.updateParticles();
      this.drawParticles();
      this.animationId = requestAnimationFrame(this.animate);
    },

    // 启动动画
    startAnimation() {
      this.animate();
    }
  }
};
</script>

<style scoped>
.cherry-blossoms-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
