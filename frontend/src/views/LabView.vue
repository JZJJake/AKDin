
<script setup lang="ts">
import { ref } from 'vue'

const code = ref("print('Hello World')")
const chartOption = ref({
  title: { text: 'Backtest Result' },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  yAxis: { type: 'value' },
  series: [{ data: [150, 230, 224, 218, 135], type: 'line' }]
})
</script>

<template>
  <div class="lab-view">
    <div class="editor-pane">
      <h3>Strategy Editor</h3>
      <!-- Placeholder for Monaco Editor -->
      <div class="editor-placeholder">
        Monaco Editor Area (Code length: {{ code.length }})
      </div>
    </div>
    <div class="visual-pane">
      <h3>Visualization</h3>
      <!-- Placeholder for ECharts -->
      <div class="chart-placeholder">
        ECharts Area ({{ chartOption.title.text }})
      </div>
    </div>
  </div>
</template>

<style scoped>
.lab-view {
  display: flex;
  height: 100%;
  gap: 10px;
}

.editor-pane, .visual-pane {
  flex: 1;
  border: 1px solid #dcdfe6;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.editor-placeholder, .chart-placeholder {
  flex: 1;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>
