<template>
    <h1>句子听读练习</h1>
    <div v-if="sentences.length">
      <div class="sentence-practice">
        <div>
          <span>第 {{ currentSentenceIndex + 1 }} / {{ sentences.length }} 句</span>
        </div>
        <div class="sentence-content">{{ sentences[currentSentenceIndex] }}</div>
        <audio :src="sentenceAudioUrl" controls></audio>
        <div style="margin: 10px 0;">
          <el-button @click="playSentenceAudio" :disabled="isPlayingSentenceAudio">播放句子读音</el-button>
          <el-button @click="startSentenceRecording" :disabled="isSentenceRecording || !canRecord">
            {{ isSentenceRecording ? '录音中...' : '开始录音' }}
          </el-button>
          <el-button @click="stopSentenceRecording" :disabled="!isSentenceRecording">停止录音</el-button>
          <el-button @click="playSentenceRecording"
            :disabled="!sentenceAudioUrls[currentSentenceIndex]">播放录音</el-button>
        </div>
        <div style="margin: 10px 0;">
          <el-button @click="prevSentence" :disabled="currentSentenceIndex === 0">上一句</el-button>
          <el-button @click="nextSentence" :disabled="currentSentenceIndex === sentences.length - 1">下一句</el-button>
        </div>
      </div>
    </div>
    <div v-else>暂无句子内容</div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
// @ts-ignore
import Tokenizer from 'sentence-tokenizer';
// @ts-ignore
import apiService from '@/services/apiService';

interface WordDetail {
  id: number;
  word: string;
  pronunciation: string;
  meaning: string;
  filename?: string;
  text_content?: string;
  file_path?: string;
}

export default defineComponent({
  name: 'WordPracticeView',
  setup() {
    const route = useRoute();
    const wordDetail = ref<WordDetail | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    
    const canRecord = computed(() => !!navigator.mediaDevices && !!navigator.mediaDevices.getUserMedia);
    
    const sentences = ref<string[]>([]);
    const currentSentenceIndex = ref(0);
    const isPlayingSentenceAudio = ref(false);
    const isSentenceRecording = ref(false);
    const sentenceAudioUrls = ref<string[]>([]); // 录音url数组
    const sentenceAudioUrl = ref<string | undefined>(undefined);
    const sentenceRecorder = ref<MediaRecorder | null>(null);
    const sentenceAudioChunks = ref<Blob[]>([]);

    const fetchWordDetail = async (wordId: string) => {
      loading.value = true;
      error.value = null;
      try {
        const response = await apiService.getResourceById(wordId);
        wordDetail.value = response.data;
        
        // 拆分句子
        if (wordDetail.value?.text_content) {
          // 使用 sentence-tokenizer 拆分句子
          const tokenizer = new Tokenizer('Chuck');
          tokenizer.setEntry(wordDetail.value.text_content);
          sentences.value = tokenizer.getSentences();
          console.log('Sentences:', sentences.value);
          
          sentences.value.forEach((item) => {
            const url = `https://dict.youdao.com/dictvoice?type=1&audio=${encodeURIComponent(item)}`;
            console.log('SentenceURL:', url);
            sentenceAudioUrls.value.push(url);
          });
          currentSentenceIndex.value = 0;
          if (sentenceAudioUrls.value.length > 0) {
            sentenceAudioUrl.value = sentenceAudioUrls.value[0];
          }
          console.log('SentenceAudioUrl:', sentenceAudioUrl.value);
        } else {
          sentences.value = [];
          sentenceAudioUrls.value = [];
        }
        
        console.log('Word detail:', wordDetail.value);
      } catch (err) {
        error.value = '加载单词详情失败';
        ElMessage.error(error.value);
        console.error('Failed to fetch word detail', err);
      }
      loading.value = false;
    };

    const playSentenceAudio = async () => {
      if (!sentences.value.length) return;
      isPlayingSentenceAudio.value = true;
      try {
        sentenceAudioUrl.value = sentenceAudioUrls.value[currentSentenceIndex.value];
        setTimeout(() => {
          isPlayingSentenceAudio.value = false;
        }, 1000);
      } catch (err) {
        isPlayingSentenceAudio.value = false;
        ElMessage.error('获取句子音频失败');
      }
    };

    const startSentenceRecording = async () => {
      if (!canRecord.value) {
        ElMessage.error('浏览器不支持录音功能');
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        sentenceRecorder.value = new MediaRecorder(stream);
        sentenceAudioChunks.value = [];
        isSentenceRecording.value = true;
        
        sentenceRecorder.value.ondataavailable = (event) => {
          sentenceAudioChunks.value.push(event.data);
        };
        
        sentenceRecorder.value.onstop = () => {
          const audioBlob = new Blob(sentenceAudioChunks.value, { type: 'audio/wav' });
          sentenceAudioUrls.value[currentSentenceIndex.value] = URL.createObjectURL(audioBlob);
          // 释放资源
          stream.getTracks().forEach(track => track.stop());
          isSentenceRecording.value = false;
          ElMessage.success('录音已保存');
        };
        
        sentenceRecorder.value.start();
        ElMessage.success('录音已开始');
      } catch (err) {
        isSentenceRecording.value = false;
        ElMessage.error('录音启动失败');
        console.error('Error starting sentence recording', err);
      }
    };

    const stopSentenceRecording = () => {
      if (sentenceRecorder.value && isSentenceRecording.value) {
        sentenceRecorder.value.stop();
        ElMessage.success('录音已结束');
      }
    };

    const playSentenceRecording = () => {
      const url = sentenceAudioUrls.value[currentSentenceIndex.value];
      if (!url) {
        ElMessage.error('当前句子没有录音');
        return;
      }
      const audio = new Audio(url);
      audio.play().catch(err => {
        ElMessage.error('播放录音失败');
        console.error('Error playing recording', err);
      });
    };

    const prevSentence = () => {
      if (currentSentenceIndex.value > 0) {
        currentSentenceIndex.value--;
        sentenceAudioUrl.value = sentenceAudioUrls.value[currentSentenceIndex.value];
      }
    };

    const nextSentence = () => {
      if (currentSentenceIndex.value < sentences.value.length - 1) {
        currentSentenceIndex.value++;
        sentenceAudioUrl.value = sentenceAudioUrls.value[currentSentenceIndex.value];
      }
    };

    onMounted(() => {
      console.log(route.params);
      const wordId = route.params.id as string;
      console.log('Word ID:', wordId);
      if (wordId) {
        fetchWordDetail(wordId);
      } else {
        // 如果没有wordId, 可以显示提示或重定向
        error.value = '未指定练习单词';
        ElMessage.warning(error.value);
      }
    });

    return {
      route,
      wordDetail,
      loading,
      error,
      canRecord,
      sentences,
      currentSentenceIndex,
      isPlayingSentenceAudio,
      isSentenceRecording,
      sentenceAudioUrls,
      sentenceAudioUrl,
      sentenceRecorder,
      sentenceAudioChunks,
      playSentenceAudio,
      startSentenceRecording,
      stopSentenceRecording,
      playSentenceRecording,
      prevSentence,
      nextSentence,
    };
  },
});
</script>

<style scoped>
.word-practice-card {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
}

.word-practice-card h1 {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.sentence-practice {
  text-align: center;
}

.sentence-content {
  font-size: 18px;
  font-weight: bold;
  margin: 20px 0;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 8px;
  line-height: 1.5;
}

.el-button {
  margin: 5px;
  min-height: 40px;
}

audio {
  width: 100%;
  max-width: 400px;
  margin: 15px 0;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .word-practice-card {
    margin: 10px;
    padding: 15px;
  }
  
  .word-practice-card h1 {
    font-size: 26px;
    margin-bottom: 25px;
  }
  
  .sentence-content {
    font-size: 19px;
    margin: 25px 0;
    padding: 20px 15px;
  }
  
  .el-button {
    margin: 8px 4px;
    min-height: 48px;
    font-size: 16px;
    border-radius: 8px;
    padding: 12px 20px;
  }
  
  audio {
    width: 100%;
    height: 50px;
    margin: 20px 0;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .word-practice-card {
    margin: 5px;
    padding: 12px;
  }
  
  .word-practice-card h1 {
    font-size: 24px;
  }
  
  .sentence-content {
    font-size: 17px;
    padding: 15px 12px;
  }
  
  .el-button {
    margin: 6px 2px;
    min-height: 44px;
    font-size: 15px;
    padding: 10px 15px;
  }
}

/* 按钮组布局优化 */
@media (max-width: 768px) {
  .sentence-practice > div {
    margin-bottom: 15px;
  }
  
  .sentence-practice > div:last-child {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .sentence-practice .el-button {
    flex: 1;
    min-width: 120px;
    max-width: 200px;
  }
}
</style>