<template>
  <div class="book-card" @click="goToDetail">
    <img :src="resolvedCover" alt="封面" class="cover-img" />
    <div class="book-info">
      <h2 class="book-title">{{ book.title }}</h2>
      <p class="book-intro">{{ book.introduction }}</p>

      <!-- 插入标签 -->
      <div class="book-tags" v-if="book.tags">
        <span v-for="tag in parsedTags" :key="tag" class="tag">{{ tag }}</span>
      </div>

      <div class="book-author">作者：{{ book.author_name }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BookCard",
  props: {
    book: Object,
  },
  computed: {
    resolvedCover() {
      return this.book.cover_url || require('@/assets/img/cover1.jpg');
    },
    parsedTags() {
      // 标签用中文逗号/英文逗号/空格/竖线分隔
      return this.book.tags ? this.book.tags.split(/[ ,，、|]+/) : [];
    },
  },
  methods: {
    goToDetail() {
      this.$router.push(`/novels/${this.book.id}`);
    },
  },
};
</script>

<style scoped>
.book-card {
  display: flex;
  width: 100%;
  max-width: 600px;
  background-color: rgba(255, 255, 255, 0.75); /* 半透明白色 */
  border-radius: 16px;
  margin: 16px auto;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  backdrop-filter: blur(4px); /* 毛玻璃效果 */
}

.book-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
}

.cover-img {
  width: 110px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  margin-right: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.book-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 6px;
}

.book-intro {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 10px;
  max-height: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.tag {
  padding: 4px 10px;
  font-size: 12px;
  background-color: #e0f2fe;
  color: #0369a1;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}

.tag:hover {
  background-color: #bae6fd;
}

.book-author {
  font-size: 13px;
  color: #64748b;
  text-align: right;
}
</style>
