<template>
  <el-card class="practice-card">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="单词跟读练习" name="word">
        <h2>完整听读练习: {{ wordDetail?.filename }}</h2>
        <div v-if="wordDetail">
          <p><strong>原始音频:</strong></p>
          <div class="audio-player-container">
            <audio id="audioPlayer" controls :src="audioUrlA">
            </audio>
          </div>
          <!-- <p><strong>文字:</strong> {{ wordDetail.text_content }}</p> -->

          <div class="reference-text-container">
            <h2>原文:</h2>
            <p class="reference-text" v-if="displayWords.length">
              <span v-for="(word, index) in displayWords" :key="index" :class="getWordClass(word)">
                {{ word.text + ' ' }}
              </span>
            </p>
            <p v-else>{{ wordDetail.text_content }}</p>
            <p>Total words: {{ totalOriginalWords }}</p>
          </div>

          <el-button @click="startRecording" :disabled="isRecording || !canRecord">
            {{ isRecording ? '录音中...' : '开始录音' }}
          </el-button>
          <el-button @click="stopRecording" :disabled="!isRecording">停止录音</el-button>
          <el-button @click="playRecording" :disabled="!audioUrl">播放录音</el-button>

          <div v-if="audioUrl" class="audio-player-container">
            <audio :src="audioUrl" controls></audio>
          </div>

          <!-- <div v-if="evaluationResult" class="evaluation-result">
            <h4>评分结果:</h4>
            <p><strong>得分:</strong> {{ evaluationResult.score }}</p>
            <p><strong>评价:</strong> {{ evaluationResult.feedback }}</p>
          </div> -->

          <div v-if="score !== null" class="evaluation-result">
            <h2>评分结果:</h2>
            <p>正确单词数: {{ correctWordsCount }}</p>
            <p>错误/遗漏单词数: {{ incorrectWordsCount }}</p>
            <p>错误率: {{ (errorRate * 100).toFixed(2) }}%</p>
            <p class="score">得分: {{ score.toFixed(2) }} / 100</p>
          </div>

          <el-button @click="submitRecording" :disabled="!audioUrl || isEvaluating" type="primary"
            style="margin-top: 20px;">
            {{ isEvaluating ? '评分中...' : '提交评分' }}
          </el-button>
        </div>
        <p v-else-if="loading">加载单词信息...</p>
        <p v-if="error">{{ error }}</p>
      </el-tab-pane>
      <el-tab-pane label="句子听读练习" name="sentence">
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
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import  Tokenizer  from 'sentence-tokenizer';
import * as Diff from 'diff';
import apiService from '@/services/apiService'; 

interface WordDetail {
  id: number;
  word: string;
  pronunciation: string;
  meaning: string;
  // Add other properties as needed
}

interface EvaluationResult {
  score: number;
  feedback: string;
}

export default defineComponent({
  name: 'PracticeView',
  setup() {
    const route = useRoute();
    const wordDetail = ref<WordDetail | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const isRecording = ref(false);
    const audioUrl = ref<string | null>(null);
    const audioUrlA = ref<string | null>(null);
    const mediaRecorder = ref<MediaRecorder | null>(null);
    const audioChunks = ref<Blob[]>([]);
    const evaluationResult = ref<EvaluationResult | null>(null);
    const isEvaluating = ref(false);

    const canRecord = computed(() => !!navigator.mediaDevices && !!navigator.mediaDevices.getUserMedia);

    const incorrectWordsCount = ref(0);
    const correctWordsCount = ref(0);
    const totalOriginalWords = ref(0);
    const errorRate = ref(0);
    const score = ref(0);
    const displayWords = ref<{ text: string, status: 'correct' | 'incorrect' | 'none' }[]>([]);

    const activeTab = ref('word');
    const sentences = ref<string[]>([]);
    const currentSentenceIndex = ref(0);
    const isPlayingSentenceAudio = ref(false);
    const isSentenceRecording = ref(false);
    const sentenceAudioUrls = ref<string[]>([]); // 录音url数组
    const sentenceAudioUrl = ref<string | null>(null);
    const sentenceRecorder = ref<MediaRecorder | null>(null);
    const sentenceAudioChunks = ref<Blob[]>([]);

    const fetchWordDetail = async (wordId: string) => {
      loading.value = true;
      error.value = null;
      try {
        const response = await apiService.getResourceById(wordId);
        wordDetail.value = response;
        totalOriginalWords.value = wordDetail.value.text_content.split(' ').length;
        // 拆分句子
        if (wordDetail.value.text_content) {
          // 使用 sentence-splitter 拆分句子
          const tokenizer = new Tokenizer('Chuck');
          tokenizer.setEntry(wordDetail.value.text_content);
          sentences.value = tokenizer.getSentences();
          console.log('Sentences:', sentences.value);
          //const splitted = sentenceSplit(wordDetail.value.text_content).filter(s => s.type === 'Sentence').map(s => s.raw.trim());
          //sentences.value = splitted;
          
          sentences.value.forEach((item, index) => {
            const url = `https://dict.youdao.com/dictvoice?type=1&audio=${item}`;
            console.log('SentenceURL:', url);
            sentenceAudioUrls.value.push(url);
          });
          currentSentenceIndex.value = 0;
          sentenceAudioUrl.value = sentenceAudioUrls.value[0];
          console.log('SentenceAudioUrl:', sentenceAudioUrl.value);
        } else {
          sentences.value = [];
          sentenceAudioUrls.value = [];
        }
        console.log('Word detail:', wordDetail.value);
        // 获取音频文件 response.file_path 7b393faa-33d9-4856-98f6-3c06917c93a5.mp3
        const mp3 = await apiService.getMp3('7b393faa-33d9-4856-98f6-3c06917c93a5.mp3', {
          responseType: 'blob'
        });
        audioUrlA.value = URL.createObjectURL(new Blob([mp3]));
        /** 
        // 模拟数据
        if (wordId === '1') {
          wordDetail.value = { id: 1, word: 'apple', pronunciation: '/ˈæpəl/', meaning: '苹果' };
        } else if (wordId === '2') {
          wordDetail.value = { id: 2, word: 'banana', pronunciation: '/bəˈnɑːnə/', meaning: '香蕉' };
        } else {
          wordDetail.value = { id: parseInt(wordId), word: `Word ${wordId}`, pronunciation: '/pronunciation/', meaning: '释义' };
        }
        ElMessage.info('单词详情加载功能待实现，当前为模拟数据');
        */
      } catch (err) {
        error.value = '加载单词详情失败';
        ElMessage.error(error.value);
        console.error('Failed to fetch word detail', err);
      }
      loading.value = false;
    };

    const startRecording = async () => {
      if (!canRecord.value) {
        ElMessage.error('浏览器不支持录音功能');
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder.value = new MediaRecorder(stream);
        audioChunks.value = [];
        audioUrl.value = null;
        evaluationResult.value = null;

        mediaRecorder.value.ondataavailable = (event) => {
          audioChunks.value.push(event.data);
        };

        mediaRecorder.value.onstop = () => {
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' });
          audioUrl.value = URL.createObjectURL(audioBlob);
          // 自动释放 MediaStream 的轨道
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.value.start();
        isRecording.value = true;
        ElMessage.success('录音已开始');
      } catch (err) {
        ElMessage.error('无法开始录音，请检查麦克风权限');
        console.error('Error starting recording', err);
      }
    };

    const stopRecording = () => {
      if (mediaRecorder.value && isRecording.value) {
        mediaRecorder.value.stop();
        isRecording.value = false;
        ElMessage.success('录音已结束');
      }
    };

    const playRecording = () => {
      if (audioUrl.value) {
        const audio = new Audio(audioUrl.value);
        audio.play();
      }
    };

    const submitRecording = async () => {
      if (!audioUrl.value) {
        ElMessage.error('没有录音可提交');
        return;
      }
      isEvaluating.value = true;
      evaluationResult.value = null;
      try {
        const audioBlob = await fetch(audioUrl.value).then(r => r.blob());
        const formData = new FormData();
        formData.append('file', audioBlob, `${wordDetail.value?.word || 'recording'}.wav`);
        formData.append('word_id', String(wordDetail.value?.id));

        //const response = await apiService.submitRecordingForEvaluation(formData);
        //console.log('Evaluation result:', response);
        
        //evaluationResult.value = response;
        // ElMessage.success('评分成功');
        processResults();
        
        // 模拟评分结果
        setTimeout(() => {
          evaluationResult.value = {
            score: Math.floor(Math.random() * 50) + 50, // 50-99
            feedback: '发音标准，语调自然。'
          };
          ElMessage.info('提交评分功能待实现，当前为模拟结果');
          isEvaluating.value = false;
        }, 1500);

      } catch (err) {
        ElMessage.error('提交评分失败');
        console.error('Error submitting recording', err);
        isEvaluating.value = false;
      }
    };

    const getWordClass = (word) => {
      if (word.status === 'correct') {
        return 'correct-word';
      } else if (word.status === 'incorrect') {
        return 'incorrect-word';
      }
      return 'pending-word';
    };

    const processResults = () => {
      const originalWords = wordDetail.value.text_content;
      const spokenWords = 'My tower, my xoxxwer is g0oing up, my stower is going up and up.No, no, sdown comes my stower, Here is my big rred block.Here is my big blue block. My tower is going up.';

      console.log("Original:", originalWords);
      console.log("Spoken:", spokenWords);

      const diffs = Diff.diffWords(originalWords, spokenWords, {
        comparator: (left, right) => left === right // Simple string comparison
      });

      console.log("Diffs:", diffs);

      let newDisplayWords = [];
      let Sidx = 0; // Spoken words index
      let Oidx = 0; // Original words index (implicit via diff)

      diffs.forEach(part => {
        if (part.added) { // User said extra words - counts as error for overall accuracy
          // These words are not in the original text, so they don't directly map to highlighting.
          // We could count them as errors, but the primary goal is to see how well the *original* text was read.
          // For scoring, each added word can be considered an error against the flow.
          // This example focuses on errors in *reading the given text*.
        } else if (part.removed) { // Words in original, but not spoken (or mispronounced enough to be different)
          part.value.split(' ').forEach(word => {
            newDisplayWords.push({ text: word, status: 'incorrect' });
            //incorrectWordsCount.value++;
          });
        } else { // Common part
          part.value.split(' ').forEach(word => {
            newDisplayWords.push({ text: word, status: 'correct' });
          });
          correctWordsCount.value += part.count;
        }
      });

      // Ensure displayWords covers all original words, even if user spoke less
      // The diff should inherently handle this by showing 'removed' parts for trailing original words if user stopped early.
      displayWords.value = newDisplayWords;

      // If the diff algorithm doesn't fully align with original word count (e.g., if spoken text is much shorter)
      // we might need to adjust `incorrectWordsCount` based on the `totalOriginalWords`.
      // The `diffArrays` method should produce parts that sum up to the length of the longer array if one is a subsequence of another,
      // or a combined length otherwise.
      // For our scoring: an error is a word from the original text that was NOT marked 'correct'.
      incorrectWordsCount.value = totalOriginalWords.value - correctWordsCount.value;


      if (totalOriginalWords.value > 0) {
        errorRate.value = incorrectWordsCount.value / totalOriginalWords.value;
        score.value = (1 - errorRate.value) * 100;
      } else {
        errorRate.value = 0;
        score.value = 100; // Or 0 if empty text is an issue
      }
    };

    onMounted(() => {
      console.log(route.params)
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

    const playSentenceAudio = async () => {
      if (!sentences.value.length) return;
      isPlayingSentenceAudio.value = true;
      try {
       sentenceAudioUrl.value = sentenceAudioUrls.value[currentSentenceIndex.value];
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
          //const audioBlob = new Blob(sentenceAudioChunks.value, { type: 'audio/wav' });
          //sentenceAudioUrls.value[currentSentenceIndex.value] = URL.createObjectURL(audioBlob);
          // 释放资源
          stream.getTracks().forEach(track => track.stop());
          isSentenceRecording.value = false;
        };
        sentenceRecorder.value.start();
      } catch (err) {
        isSentenceRecording.value = false;
        ElMessage.error('录音启动失败');
      }
    };

    const stopSentenceRecording = () => {
      if (sentenceRecorder.value && isSentenceRecording.value) {
        sentenceRecorder.value.stop();
      }
    };

    const playSentenceRecording = () => {
      const url = sentenceAudioUrls.value[currentSentenceIndex.value];
      if (!url) {
        ElMessage.error('当前句子没有录音');
        return;
      }
      sentenceAudioUrl.value = url;
      //const audio = new Audio(url);
      //audio.play();
    };

    const prevSentence = () => {
      if (currentSentenceIndex.value > 0) {
        currentSentenceIndex.value--;
      }
    };

    const nextSentence = () => {
      if (currentSentenceIndex.value < sentences.value.length - 1) {
        currentSentenceIndex.value++;
      }
    };

    return {
      route,
      wordDetail,
      loading,
      error,
      isRecording,
      audioUrl,
      audioUrlA,
      mediaRecorder,
      audioChunks,
      evaluationResult,
      isEvaluating,
      canRecord,
      incorrectWordsCount,
      correctWordsCount,
      totalOriginalWords,
      errorRate,
      score,
      displayWords,
      activeTab,
      sentences,
      currentSentenceIndex,
      isPlayingSentenceAudio,
      isSentenceRecording,
      sentenceAudioUrls,
      sentenceAudioUrl,
      sentenceRecorder,
      sentenceAudioChunks,
      startRecording,
      stopRecording,
      playRecording,
      submitRecording,
      getWordClass,
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
.practice-card {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
}
.audio-player-container {
  margin-top: 20px;
}
.evaluation-result {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.pending-word {
  /* Default style */
}

.correct-word {
  color: #27ae60;
  /* Green */
  font-weight: bold;
}

.incorrect-word {
  color: #c0392b;
  /* Red */
  background-color: #fdd;
  text-decoration: line-through;
  font-weight: bold;
}
</style>