<template>
  <el-card class="word-list-card">
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
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiService from '@/services/apiService'; // 稍后会创建

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
.word-list-card {
  margin: 20px;
}
</style>