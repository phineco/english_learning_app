<template>
    <el-card class="resource-library-card">
        <h2>资源库</h2>
        <el-table :data="resourceList" style="width: 100%" @selection-change="handleSelectionChange" ref="resourceTable"
            :row-key="row => row.id" border>
            <el-table-column type="selection" width="55"></el-table-column>
            <el-table-column prop="filename" label="文件名"></el-table-column>
            <el-table-column prop="file_type" label="类型"></el-table-column>
            <el-table-column prop="user_username" label="上传用户"></el-table-column>
            <el-table-column prop="upload_time" label="上传时间"></el-table-column>
        </el-table>
        <div style="margin-top: 16px;">
            <el-button type="primary" :disabled="selectedResources.length !== 1"
                @click="handlePractice">立即跟读</el-button>
            <el-button type="primary" :disabled="selectedResources.length === 0"
                @click="addToTaskPlan">加入跟读计划</el-button>
        </div>
    </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'
import apiService from '@/services/apiService';
import { ElMessage } from 'element-plus';

interface ResourceFile {
  id: number;
  filename: string;
  file_type: string;
  user_username: string;
  upload_time: string;
}

const resourceList = ref<ResourceFile[]>([]);
const selectedResources = ref<ResourceFile[]>([]);
const router = useRouter();
const handleSelectionChange = (selection: ResourceFile[]) => {
    selectedResources.value = selection;
};

const handlePractice = () => {
    const ids = selectedResources.value.map(item => item.id);
    console.log(ids);
    router.push({ name: 'Practice', params: { id: ids[0] } });
};

const addToTaskPlan = () => {
  // 这里应调用后端接口，将选中的资源加入跟读任务计划
  // 示例：apiService.addResourcesToTaskPlan(selectedResources.value)
  ElMessage.success('已加入跟读任务计划（示例，需后端实现）');
};

onMounted(async () => {
  try {
    const res = await apiService.getResourceList();
    //console.log(res);
    resourceList.value = res;
  } catch (e) {
    ElMessage.error('获取资源列表失败');
  }
});
</script>

<style scoped>
.resource-library-card {
  max-width: 900px;
  margin: 32px auto;
  padding: 24px;
}
</style>