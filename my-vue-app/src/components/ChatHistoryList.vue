<template>
  
  <div class="history-list">
    <div
        v-for="(item, index) in chatHistory"
        :key="index"
        class="history-item"
        :class="{ active: selectedId === item.id }"
        @mouseenter="hoveredId = item.id"
        @mouseleave="hoveredId = null"
    >
      <!-- 会话按钮区域 -->
      <button class="history-button" @click="selectChat(item.id)">
        {{ item.title }}
      </button>

      <!-- 更多操作按钮，仅在悬浮该行时显示 -->
      <div class="more-wrapper">
        <button
            class="more-button"
            v-if="hoveredId === item.id"
            @click="toggleOptions(item.id, $event)"
        >
          ⋮
        </button>

        <!-- 弹出菜单 -->
        <div
            v-if="menuVisible && currentMenuId === item.id"
            class="options-menu"
        >
          <div class="menu-item" @click="renameChat(item)">重命名</div>
          <div class="menu-item delete" @click="deleteChat(item.id)">删除</div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
export default {
  name: "ChatHistoryList",
  // 声明接收的props
  props: {
    chatHistory: {
      type: Array, // 类型为数组
      required: true, // 要求父组件必须传递
      default: () => [] // 可选：默认值为空数组
    },
    // 第二个参数：选中的 ID
    selectedId: {
      type: Number,
      required: true
    }
  },
  watch: {
    // 监听 props 传递的 chatHistory 变化
    chatHistory: {
      handler() {
      },
      deep: true, // 必须开启深度监听，才能监听到数组内部元素的增删改
      immediate: true // 初始化时立即执行一次（可选）
    }
  },
  data() {
    return {
      hoveredId: null,           // 当前悬浮项的 ID
      currentMenuId: null,       // 当前展开菜单对应的对话 ID
      menuVisible: false         // 是否显示菜单
    };
  },
  methods: {
    async selectChat(id) {
      console.log("选中了对话:", id);
      
      const token = localStorage.getItem('token');
      // 可选：如果需要将选中状态同步到父组件，可以通过$emit触发事件
      const port = await axios.post(`http://localhost:8000/api/to_port?num=${id}`, {},{
              headers: { Authorization: `Bearer ${token}` }
            });
            
      this.$router.push(`/main/${port.data}`);
      
      this.$emit('select-chat', id);
    },
    toggleOptions(id, event) {
      event.stopPropagation(); // 阻止事件冒泡，防止触发其他点击
      if (this.menuVisible && this.currentMenuId === id) {
        this.menuVisible = false;
        this.currentMenuId = null;
      } else {
        this.menuVisible = true;
        this.currentMenuId = id;
      }
    },
    async renameChat(item) {
      const newTitle = prompt("请输入新的标题：", item.title);
      if (newTitle && newTitle !== item.title) {
        // 触发事件，通知父组件修改标题
        const token = localStorage.getItem('token');
        await axios.post(
  `http://localhost:8000/api/update_title?num=${item.id}&title=${encodeURIComponent(newTitle)}`,{},{
              headers: { Authorization: `Bearer ${token}` }
            });
        this.$emit('rename-chat', {
          id: item.id,
          newTitle: newTitle
        });
      }
      this.menuVisible = false;
    },
    async deleteChat(id) {
      // 触发事件，通知父组件删除对话
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:8000/api/delete?num=${id}`, {},{
              headers: { Authorization: `Bearer ${token}` }
            });
      if(this.selectedId ==id){
        const token = localStorage.getItem('token');
        // 可选：如果需要将选中状态同步到父组件，可以通过$emit触发事件
        const port = await axios.post(`http://localhost:8000/api/to_port?num=${id-1}`, {},{
                headers: { Authorization: `Bearer ${token}` }
              });
              
        this.$router.push(`/main/${port.data}`);
      }
      this.$emit('fetch-history');
      this.$emit('delete-chat', id);
      this.menuVisible = false;
    }
  },
  
  mounted() {
    // 点击页面任意地方关闭菜单
    // 打印接收的 props，检查是否有值
    // 监听 props 变化（如果数据是异步获取的）
    
    document.addEventListener("click", () => {
      this.menuVisible = false;
    });
    
  }
};
</script>

<style scoped>
.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 0;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  padding: 4px 6px;
  position: relative;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: rgba(255, 255, 255, 0.85);
}

.history-item.active {
  background-color: rgba(146, 254, 157, 0.6);
}

.history-button {
  flex: 1;
  text-align: left;
  background: transparent;
  border: none;
  padding: 6px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.history-button:hover {
  color: #007acc;
}

.more-wrapper {
  position: relative;
}

.more-button {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #555;
  padding: 0 6px;
}

.more-button:hover {
  color: #000;
}

/* 弹出菜单样式 */
.options-menu {
  position: absolute;
  top: 28px;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  border-radius: 6px;
  z-index: 10;
  width: 100px;
  animation: fadeIn 0.2s ease;
}

.menu-item {
  padding: 8px 12px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.menu-item:hover {
  background: #f3f3f3;
}

.menu-item.delete {
  color: #e74c3c;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
