
<script setup lang="ts">
import { ref } from 'vue'

const selectedStrategy = ref('')
const autoMonitor = ref(false)

const strategies = ref([
  { value: 'strategy1', label: 'Simple Moving Average' },
  { value: 'strategy2', label: 'RSI Reversal' }
])

const runScreener = () => {
  console.log('Running screener for:', selectedStrategy.value)
}
</script>

<template>
  <div class="screener-view">
    <h3>Unified Screener & Monitor</h3>

    <div class="controls">
      <el-select v-model="selectedStrategy" placeholder="Select Strategy" style="width: 240px">
        <el-option
          v-for="item in strategies"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>

      <el-button type="primary" @click="runScreener" :disabled="!selectedStrategy">
        Run Once
      </el-button>

      <div class="monitor-switch">
        <span>Auto-Monitor</span>
        <el-switch v-model="autoMonitor" />
      </div>
    </div>

    <div class="results-area">
      <!-- Placeholder for results -->
      <el-empty description="No signals generated" />
    </div>
  </div>
</template>

<style scoped>
.screener-view {
  padding: 20px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.monitor-switch {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}
</style>
