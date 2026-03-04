<template>
  <div class="platform">
    <!-- 白色半透明蒙版 -->
    <div class="background-overlay"></div>
    <!-- 顶部艺术字图片 -->
    <div class="title-image-container">
      <img
          src="@/assets/img/title_wordart.png"
          alt="小说创作平台"
          class="title-wordart"
          @click="goToMainPage"
      >
    </div>

    <!-- 🔍 搜索区域 -->
    <div class="search-container">
      <input
          type="text"
          v-model="searchQuery"
          placeholder="请输入小说标题或作者名称"
          class="search-input"
          @keyup.enter="searchNovels"
      />
      <button @click="searchNovels" class="search-button">搜索</button>
    </div>

    <!-- 🏷️ 标签筛选栏（多选） -->
    <div class="tags-container">
      <span
          v-for="tag in allTags"
          :key="tag"
          class="tag-item"
          :class="{ active: selectedTags.includes(tag) }"
          @click="toggleTag(tag)"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 📚 小说卡片区域 -->
    <div class="novels-container">
      <BookCard
          v-for="book in filteredNovels"
          :key="book.id"
          :book="book"
      />
    </div>
  </div>
</template>

<script>
import BookCard from '@/components/BookCard.vue';
import axios from 'axios';

export default {
  name: 'PlatformPage',
  components: {
    BookCard,
  },
  data() {
    return {
      novels: [],
      searchQuery: '',
      selectedTags: [],
      allTags: [
        '玄幻', '修真', '武侠', '都市', '历史', '科幻', '悬疑',
        '游戏', '言情', '重生', '穿越', '系统', '无敌',
        '甜宠', '搞笑', '热血', '励志', '高智商'
      ],
    };
  },
  computed: {
    filteredNovels() {
      const keyword = this.searchQuery.trim().toLowerCase();

      return this.novels.filter(book => {
        const matchTitleOrAuthor =
            book.title.toLowerCase().includes(keyword) ||
            book.author_name.toLowerCase().includes(keyword);

        const matchTags = this.selectedTags.every(tag =>
            book.tags && book.tags.includes(tag)
        );

        return matchTitleOrAuthor && matchTags;
      });
    },
  },
  methods: {
    async fetchNovels() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/novels');
        this.novels = response.data;
      } catch (error) {
        console.error('获取小说失败:', error);
      }
    },
    searchNovels() {
      // 已由 computed 实现，无需额外逻辑
    },
    toggleTag(tag) {
      const index = this.selectedTags.indexOf(tag);
      if (index > -1) {
        this.selectedTags.splice(index, 1); // 取消选中
      } else {
        this.selectedTags.push(tag); // 添加选中
      }
    },

    goToMainPage() {
      this.$router.push('/main');
    },
  },
  mounted() {
    this.fetchNovels();
  },
};
</script>

<style scoped>
/* 基础样式重置与字体设置 */
.platform {
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-image: url("@/assets/img/platform_bk.jpg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: #334155;
  display: flex;
  flex-direction: column;
}
.background-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5); /* 半透明白色 */
  z-index: 0; /* 放在最底层背景图片上，但在内容下 */
}

/* 搜索框区域 */
.search-container {
  display: flex;
  justify-content: center;
  margin: 15px 0;
  padding: 0 15px;
  z-index: 1;
}

.search-input {
  flex: 1;
  max-width: 600px;
  padding: 12px 16px;
  font-size: 15px;
  background-color: #ffffff;
  border: 1px solid #dbeafe;
  border-right: none;
  color: #334155;
  border-radius: 6px 0 0 6px;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-button {
  padding: 12px 24px;
  font-size: 15px;
  background: linear-gradient(90deg, #bfdbfe, #93c5fd);
  color: #1e40af;
  font-weight: 500;
  border: none;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.search-button:hover {
  background: linear-gradient(90deg, #93c5fd, #60a5fa);
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

/* 标签栏 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 15px 0;
  justify-content: center;
  padding: 10px 15px;
  background-color: rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  z-index: 1;
}

.tag-item {
  padding: 6px 16px;
  font-size: 14px;
  border-radius: 20px;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-item:hover {
  background-color: #e0f2fe;
  border-color: #bae6fd;
  color: #0369a1;
}

.tag-item.active {
  background: linear-gradient(90deg, #dbeafe, #bfdbfe);
  color: #1e40af;
  font-weight: 500;
  border-color: #93c5fd;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

/* 小说卡片区域 */
.novels-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  padding: 15px;
  flex: 1;
  z-index: 1;
}

/* 新增：艺术字图片样式 */
.title-image-container {
  display: flex;
  justify-content: center;
  padding: 10px 0; /* 上下留出一定间距 */
}

.title-wordart {
  max-height: 200px; /* 限制图片最大高度，避免过大 */
  opacity: 0.8; /* 设置透明度（0-1之间，值越小越透明） */
  transition: opacity 0.3s ease; /* 鼠标悬停时的透明度过渡效果 */
}

.title-wordart:hover {
  opacity: 1; /* 鼠标悬停时略微提高透明度，增强交互感 */
  transform: scale(1.1);
}

</style>