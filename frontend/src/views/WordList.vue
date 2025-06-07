<template>
    <h2>单词列表</h2>
    <el-table :data="wordList" style="width: 100%">
      <el-table-column prop="word" label="单词"></el-table-column>
      <el-table-column prop="pronunciation" label="发音"></el-table-column>
      <el-table-column prop="meaning" label="中文释义"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="handlePractice(scope.row)">跟读练习</el-button>
        </template>
      </el-table-column>
    </el-table>
    <p v-if="loading">加载中...</p>
    <p v-if="error">{{ error }}</p>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
// 导入API服务
import apiService from '../services/apiService';

interface Word {
  id: number;
  word: string;
  pronunciation: string;
  meaning: string;
  // Add other properties as needed
}

export default defineComponent({
  name: 'WordListView',
  setup() {
    const wordList = ref<Word[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const fetchWords = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await apiService.getWords();
        wordList.value = response.data;
        /**
        // 模拟数据
        wordList.value = [
          { id: 1, word: 'apple', pronunciation: '/ˈæpəl/', meaning: '苹果' },
          { id: 2, word: 'banana', pronunciation: '/bəˈnɑːnə/', meaning: '香蕉' },
          { id: 3, word: 'cherry', pronunciation: '/ˈtʃeri/', meaning: '樱桃' },
        ];
        ElMessage.info('单词列表加载功能待实现，当前为模拟数据');
        */
      } catch (err) {
        error.value = '加载单词列表失败';
        ElMessage.error(error.value);
        console.error('Failed to fetch words', err);
      }
      loading.value = false;
    };

    const handlePractice = (word: Word) => {
      ElMessage.info(`开始练习单词: ${word.word} (功能待实现)`);
      // this.$router.push({ name: 'Practice', params: { wordId: word.id } });
    };

    onMounted(() => {
      fetchWords();
    });

    return {
      wordList,
      loading,
      error,
      handlePractice,
    };
  },
});
</script>

<style scoped>
.word-list {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
}

.word-list h1 {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-bar .el-input {
  flex: 1;
}

.el-table {
  margin-top: 20px;
}

.el-button {
  margin: 2px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .word-list {
    margin: 10px;
    padding: 15px;
  }
  
  .word-list h1 {
    font-size: 26px;
    margin-bottom: 25px;
  }
  
  .search-bar {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 25px;
  }
  
  .search-bar .el-input {
    width: 100%;
  }
  
  .search-bar .el-input__inner {
    height: 48px;
    font-size: 16px;
    padding: 0 15px;
  }
  
  .search-bar .el-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    border-radius: 8px;
  }
  
  .el-table {
    margin-top: 25px;
    font-size: 14px;
  }
  
  .el-table th {
    padding: 12px 8px;
    font-size: 15px;
  }
  
  .el-table td {
    padding: 12px 8px;
  }
  
  .el-table .el-button {
    margin: 3px 1px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 36px;
  }
  
  /* 表格列宽优化 */
  .el-table .el-table__cell:first-child {
    min-width: 100px;
  }
  
  .el-table .el-table__cell:nth-child(2) {
    min-width: 120px;
  }
  
  .el-table .el-table__cell:nth-child(3) {
    min-width: 80px;
  }
  
  .el-table .el-table__cell:last-child {
    min-width: 100px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .word-list {
    margin: 5px;
    padding: 12px;
  }
  
  .word-list h1 {
    font-size: 24px;
  }
  
  .search-bar {
    gap: 12px;
  }
  
  .el-table {
    font-size: 13px;
  }
  
  .el-table th {
    padding: 10px 6px;
    font-size: 14px;
  }
  
  .el-table td {
    padding: 10px 6px;
  }
  
  .el-table .el-button {
    margin: 2px 1px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 32px;
  }
  
  /* 表格水平滚动 */
  .el-table__body-wrapper {
    overflow-x: auto;
  }
  
  /* 单词和翻译列优化 */
  .el-table .el-table__cell:first-child {
    min-width: 80px;
  }
  
  .el-table .el-table__cell:nth-child(2) {
    min-width: 100px;
  }
}

/* 表格响应式优化 */
@media (max-width: 768px) {
  .el-table {
    border: 1px solid #ebeef5;
    border-radius: 8px;
  }
  
  .el-table__header-wrapper {
    border-radius: 8px 8px 0 0;
  }
  
  .el-table__body-wrapper {
    border-radius: 0 0 8px 8px;
  }
}

/* 单词详情显示优化 */
@media (max-width: 480px) {
  .word-detail {
    font-size: 14px;
    line-height: 1.4;
  }
  
  .word-pronunciation {
    font-size: 13px;
    color: #666;
  }
}
</style>