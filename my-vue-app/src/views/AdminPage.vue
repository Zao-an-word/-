<template>
  <div class="admin-dashboard">
    <!-- 粒子背景容器 -->
    <div class="particles-container">
      <canvas id="particlesCanvas"></canvas>
    </div>

    <!-- 顶部导航栏 | Top Navbar -->
    <header class="admin-header">
      <h1 class="glitch-title">管理员控制中心</h1>
      <button class="neon-button" @click="logout">退出登录</button>
    </header>

    <!-- 主体区域 | Main Layout -->
    <div class="dashboard-content">
      <!-- 侧边栏菜单 | Sidebar -->
      <aside class="sidebar">
        <ul>
          <li @click="selectSection('activity')">用户活跃度</li>
          <li @click="selectSection('review')">内容审核</li>
          <li @click="selectSection('settings')">系统设置</li>
        </ul>
      </aside>

      <!-- 内容展示区域 | Main Panel -->
      <main class="main-panel">
        <div v-if="currentSection === 'activity'">
          <h2>📊 用户活跃度</h2>
          <ul class="user-stats">
            <li v-for="user in users" :key="user.id">
              {{ user.name }}：活跃时间 {{ user.activeHours }} 小时
            </li>
          </ul>
        </div>

        <div v-else-if="currentSection === 'review'">
          <h2>📝 内容审核</h2>
          <div v-for="item in uploads" :key="item.id" class="review-item">
            <p><strong>{{ item.username }}</strong> 上传了内容：{{ item.content }}</p>
            <button class="neon-button mini" @click="approve(item.id)">通过</button>
            <button class="neon-button mini danger" @click="reject(item.id)">驳回</button>
          </div>
        </div>

        <div v-else-if="currentSection === 'settings'">
          <h2>⚙️ 系统设置</h2>
          <div class="settings-section">
            <ul class="settings-menu">
              <li v-for="(menu, index) in settingsMenu" :key="menu.title">
                <div class="menu-title" @click="toggleSettingMenu(index)">
                  {{ menu.title }}
                  <span>{{ menu.expanded ? '▲' : '▼' }}</span>
                </div>
                <ul v-show="menu.expanded" class="sub-options">
                  <li
                      v-for="sub in menu.subOptions"
                      :key="sub"
                      @click="selectSettingOption(sub)"
                      :class="{ selected: sub === selectedSettingOption }"
                  >
                    {{ sub }}
                  </li>
                </ul>
              </li>
            </ul>

            <div class="setting-details" v-if="selectedSettingOption">
              <h3>🔧 当前设置项：{{ selectedSettingOption }}</h3>
              <p>这里是 <strong>{{ selectedSettingOption }}</strong> 的详细配置区域。</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentSection: 'activity',
      users: [
        { id: 1, name: "littlewhale", activeHours: 12 },
        { id: 2, name: "JENDEUK", activeHours: 8 },
      ],
      uploads: [
        { id: 101, username: "blue", content: "小说草稿A" },
        { id: 102, username: "rose", content: "图片B" },
      ],
      particles: [],
      canvas: null,
      ctx: null,
      mouse: { x: null, y: null },
      particleCount: 80,
      maxDistance: 150,
      settingsMenu: [
        {
          title: "系统基础设置",
          expanded: false,
          subOptions: ["基本信息配置", "服务器配置", "日志设置"]
        },
        {
          title: "用户管理设置",
          expanded: false,
          subOptions: ["注册登录设置", "用户权限管理", "用户数据管理"]
        },
        {
          title: "LLM设置",
          expanded: false,
          subOptions: ["模型配置", "模型调用设置", "数据微调设置"]
        }
      ],
      selectedSettingOption: null,
    };
  },

  mounted() {
    // 初始化粒子背景
    this.initParticles();

    // 监听窗口大小变化，调整Canvas尺寸
    window.addEventListener('resize', this.resizeCanvas);

    // 监听鼠标移动，实现交互效果
    document.addEventListener('mousemove', this.handleMouseMove);
    document.addEventListener('mouseout', this.handleMouseOut);
  },

  beforeUnmount() {
    // 组件销毁前清理事件监听
    window.removeEventListener('resize', this.resizeCanvas);
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('mouseout', this.handleMouseOut);
  },

  methods: {
    // 初始化粒子背景
    initParticles() {
      this.canvas = document.getElementById('particlesCanvas');
      this.ctx = this.canvas.getContext('2d');

      // 设置Canvas尺寸
      this.resizeCanvas();

      // 创建粒子
      for (let i = 0; i < this.particleCount; i++) {
        this.particles.push({
          x: Math.random() * this.canvas.width,
          y: Math.random() * this.canvas.height,
          vx: (Math.random() - 0.5) * 1,
          vy: (Math.random() - 0.5) * 1,
          radius: Math.random() * 2 + 1,
          color: this.getRandomNeonColor(),
        });
      }

      // 开始动画循环
      this.animateParticles();
    },

    // 调整Canvas尺寸
    resizeCanvas() {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
    },

    // 获取随机霓虹颜色
    getRandomNeonColor() {
      const colors = [
        '#00ffff', '#ff00ff', '#00ff00', '#ffff00', '#ff0066',
        '#9d00ff', '#00ccff', '#ff9900', '#33ff33', '#ff33cc'
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    },

    // 处理鼠标移动
    handleMouseMove(e) {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    },

    // 处理鼠标移出
    handleMouseOut() {
      this.mouse.x = null;
      this.mouse.y = null;
    },

    // 动画循环
    animateParticles() {
      // 清除画布
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      // 更新并绘制所有粒子
      for (let i = 0; i < this.particles.length; i++) {
        const p = this.particles[i];

        // 更新粒子位置
        p.x += p.vx;
        p.y += p.vy;

        // 边界检测
        if (p.x < 0 || p.x > this.canvas.width) p.vx = -p.vx;
        if (p.y < 0 || p.y > this.canvas.height) p.vy = -p.vy;

        // 绘制粒子
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = p.color;
        this.ctx.fill();
        this.ctx.closePath();

        // 绘制粒子间的连线
        for (let j = i + 1; j < this.particles.length; j++) {
          const p2 = this.particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          // 距离越近，线条越明显
          if (distance < this.maxDistance) {
            const opacity = 1 - (distance / this.maxDistance);

            this.ctx.beginPath();
            this.ctx.moveTo(p.x, p.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * 0.5})`;
            this.ctx.lineWidth = 0.8;
            this.ctx.stroke();
            this.ctx.closePath();
          }
        }

        // 鼠标交互效果
        if (this.mouse.x !== null && this.mouse.y !== null) {
          const dxMouse = p.x - this.mouse.x;
          const dyMouse = p.y - this.mouse.y;
          const mouseDist = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);

          // 鼠标附近的粒子会加速
          if (mouseDist < 100) {
            const angle = Math.atan2(dyMouse, dxMouse);
            const pushX = Math.cos(angle) * 0.5;
            const pushY = Math.sin(angle) * 0.5;

            p.x += pushX;
            p.y += pushY;

            // 绘制鼠标与粒子的连线
            const mouseOpacity = 1 - (mouseDist / 100);
            this.ctx.beginPath();
            this.ctx.moveTo(p.x, p.y);
            this.ctx.lineTo(this.mouse.x, this.mouse.y);
            this.ctx.strokeStyle = `rgba(255, 255, 255, ${mouseOpacity * 0.3})`;
            this.ctx.lineWidth = 0.5;
            this.ctx.stroke();
            this.ctx.closePath();
          }
        }
      }

      // 继续下一帧动画
      requestAnimationFrame(() => this.animateParticles());
    },

    // 页面功能方法
    selectSection(section) {
      this.currentSection = section;
    },
    approve(id) {
      alert(`内容 ${id} 已通过审核~`);
    },
    reject(id) {
      alert(`内容 ${id} 已被驳回~`);
    },
    logout() {
      this.$router.push("/login");
    },

    toggleSettingMenu(index) {
      // 折叠/展开菜单
      this.settingsMenu[index].expanded = !this.settingsMenu[index].expanded;
    },
    selectSettingOption(option) {
      this.selectedSettingOption = option;
    }
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

.admin-dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Orbitron', sans-serif;
  background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
  color: #00ffff;
  position: relative;
  overflow: hidden;
}

/* 粒子背景容器 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* 确保Canvas覆盖整个容器 */
#particlesCanvas {
  display: block;
  width: 100%;
  height: 100%;
}

/* 顶部导航栏 | Header */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #050505dd;
  padding: 20px 30px;
  border-bottom: 2px solid #00ffff;
  box-shadow: 0 0 12px #00ffff88;
  position: relative;
  z-index: 1;
}
.glitch-title {
  font-size: 28px;
  letter-spacing: 1px;
  color: #00ffff;
  text-shadow: 0 0 5px #00ffff, 0 0 10px #ff00ff;
}

/* 主体布局 | Layout */
.dashboard-content {
  display: flex;
  flex: 1;
  position: relative;
  z-index: 1;
}

/* 侧边栏 | Sidebar */
.sidebar {
  width: 240px;
  background: #0a0a0a;
  border-right: 2px solid #00ffff88;
  box-shadow: inset 0 0 10px #00ffff44;
  padding: 20px;
}
.sidebar ul {
  list-style: none;
  padding: 0;
}
.sidebar li {
  margin: 18px 0;
  cursor: pointer;
  color: #00ffffcc;
  transition: all 0.3s;
}
.sidebar li:hover {
  color: #fff;
  text-shadow: 0 0 6px #ff00ff;
}

/* 内容区域 | Main Panel */
.main-panel {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

/* 用户活跃度列表 | User stats */
.user-stats li {
  margin: 10px 0;
  font-size: 16px;
}

/* 内容审核卡片 | Review Cards */
.review-item {
  background-color: #141414;
  border: 1px solid #00ffff44;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 0 10px #00ffff22;
}

/* 霓虹按钮 | Neon Button */
.neon-button {
  background: transparent;
  color: #00ffff;
  border: 2px solid #00ffff;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  text-transform: uppercase;
  transition: 0.25s ease-in-out;
  box-shadow: 0 0 5px #00ffff, 0 0 15px #00ffff33;
}
.neon-button:hover {
  background: #00ffff22;
  box-shadow: 0 0 10px #00ffff, 0 0 20px #ff00ff;
  color: #fff;
}

/* 小型按钮 | Mini Button */
.neon-button.mini {
  font-size: 12px;
  padding: 6px 10px;
  margin-right: 8px;
}

/* 危险按钮样式 | Reject button style */
.neon-button.danger {
  border-color: #ff0066;
  color: #ff0066;
}
.neon-button.danger:hover {
  background: #ff006622;
  box-shadow: 0 0 10px #ff0066, 0 0 20px #ff00ff;
  color: #fff;
}

.settings-section {
  display: flex;
  gap: 40px;
}

.settings-menu {
  width: 240px;
  list-style: none;
  padding: 0;
}

.settings-menu .menu-title {
  font-weight: bold;
  margin-bottom: 10px;
  cursor: pointer;
  padding: 10px;
  background: #0a0a0a;
  border: 1px solid #00ffff44;
  box-shadow: 0 0 8px #00ffff22;
  transition: 0.3s;
}

.settings-menu .menu-title:hover {
  color: #fff;
  text-shadow: 0 0 6px #ff00ff;
}

.sub-options {
  margin-left: 15px;
  list-style: none;
  padding-left: 10px;
}

.sub-options li {
  margin: 8px 0;
  cursor: pointer;
  color: #00ffffaa;
  transition: 0.3s;
}

.sub-options li:hover,
.sub-options li.selected {
  color: #fff;
  font-weight: bold;
  text-shadow: 0 0 5px #ff00ff;
}

.setting-details {
  flex: 1;
  padding: 20px;
  background: #111;
  border-radius: 10px;
  border: 1px solid #00ffff44;
  box-shadow: 0 0 10px #00ffff33;
}

</style>