import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 从环境变量或默认 /api
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器，例如添加认证token
apiClient.interceptors.request.use(
  (config) => {
    // 检查token及有效期
    const token = localStorage.getItem('access_token');
    const expire = localStorage.getItem('access_token_expire');
    const now = new Date().getTime();
    if (token && expire && now < Number(expire)) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (config.url !== '/auth/login' && config.url !== '/auth/register') {
      // 非登录注册接口且无效token，跳转登录页
      window.location.href = '/login';
      return Promise.reject(new Error('未登录或登录已过期'));
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器，例如处理全局错误
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error(error);
    // 例如，处理401未授权错误，跳转到登录页
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('access_token_expire');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default {
  // 认证相关
  login(credentials: any) {
    return apiClient.post('/auth/login', credentials).then(res => res);
  },
  register(data: any) {
    return apiClient.post('/auth/register', data);
  },
  logout() {
    // 可能需要后端API支持
    localStorage.removeItem('user-token');
    return Promise.resolve();
  },

  // 单词相关
  getWords() {
    return apiClient.get('/words');
  },
  getWordById(id: string | number) {
    return apiClient.get(`/words/${id}`);
  },

  // 跟读录音相关
  submitRecordingForEvaluation(formData: FormData) {
    return apiClient.post('/records/submitRecords', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getUserRecordings() {
    return apiClient.get('/records/history');
  },
  // 更多API方法...
  // 获取资源库文件列表
  getResourceList() {
    return apiClient.get('/resources');
  },

  getResourceById(id: string | number) {
    return apiClient.get(`/resources/${id}`);
  },
  // 新增：文本转语音
  textToSpeech(formData: FormData) {
    return apiClient.post('/convert/text-to-speech', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // 新增：语音转文本
  speechToText(formData: FormData) {
    return apiClient.post('/convert/speech-to-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getMp3(url: string, config = {}) {
    return apiClient.get(`/mp3/${url}`, { ...config, responseType: 'blob' });
  }
};

  