
<template>
  <div class="tag-selector">
    <label class="tag-label">选择标签：</label>
    <Multiselect
      v-model="internalValue"
      :options="options"
      :multiple="true"
      :close-on-select="false"
      :searchable="false"
      :allow-empty="true"
      :placeholder="'请选择标签'"
      label="label"
      track-by="value"
    />
  </div>
</template>

<script>
import Multiselect from 'vue-multiselect'

export default {
  name: 'TagSelector',
  components: {
    Multiselect
  },
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    internalValue: {
      get() {
        return this.modelValue
      },
      set(val) {
        this.$emit('update:modelValue', val)
      }
    }
  },
  data() {
    return {
      options: [
        { label: '玄幻', value: '玄幻' },
        { label: '修真', value: '修真' },
        { label: '武侠', value: '武侠' },
        { label: '都市', value: '都市' },
        { label: '历史', value: '历史' },
        { label: '科幻', value: '科幻' },
        { label: '悬疑', value: '悬疑' },
        { label: '游戏', value: '游戏' },
        { label: '言情', value: '言情' },
        { label: '重生', value: '重生' },
        { label: '穿越', value: '穿越' },
        { label: '系统', value: '系统' },
        { label: '无敌', value: '无敌' },
        { label: '甜宠', value: '甜宠' },
        { label: '搞笑', value: '搞笑' },
        { label: '热血', value: '热血' },
        { label: '励志', value: '励志' },
        { label: '高智商', value: '高智商' }
      ]
    }
  }
}
</script>

<style scoped>
.tag-selector {
  display: flex;
  align-items: center;
  margin-left: 16px;
}
.tag-label {
  white-space: nowrap;
  margin-right: 8px;
}
:deep(.multiselect) {
  min-width: 200px; /* 根据需要调整，比如 240px */
}
:deep(.multiselect__input) {
  display: none !important;
}
</style>
