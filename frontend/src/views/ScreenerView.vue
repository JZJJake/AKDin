
<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const code = ref(`import pandas as pd
from app.engine.base import BaseStrategy

class SMACrossStrategy(BaseStrategy):
    def init(self):
        self.sma_period = 20

    def next(self):
        if len(self.data) < self.sma_period + 1: return

        # Calculate SMA
        sma = self.data['close'].rolling(window=self.sma_period).mean()
        current_ma = sma.iloc[-1]
        prev_ma = sma.iloc[-2]

        current_price = self.data['close'].iloc[-1]
        prev_price = self.data['close'].iloc[-2]

        # Golden Cross Condition: Price crosses above MA
        if prev_price < prev_ma and current_price > current_ma:
            if self.position.quantity == 0:
                self.buy(100)
`)

const autoMonitor = ref(false)
const isLoading = ref(false)
const results = ref<any[]>([])

const runScreener = async () => {
  isLoading.value = true
  try {
    const payload = {
      strategy_code: code.value
    }

    ElMessage.info('Screening market... this may take a moment.')

    // Assuming backend is running on 8000
    const response = await axios.post('http://localhost:8000/api/v1/screen', payload)
    results.value = response.data.hits

    if (results.value.length > 0) {
      ElMessage.success(`Found ${results.value.length} signals!`)
    } else {
      ElMessage.info('No signals found with current strategy.')
    }
  } catch (e: any) {
    console.error(e)
    const msg = e.response?.data?.detail || e.message
    ElMessage.error('Screener failed: ' + msg)
  } finally {
    isLoading.value = false
  }
}

const toggleMonitor = (val: boolean) => {
  if (val) {
    ElMessage.success("Auto-Monitor activated. Signals will be pushed via WeChat.")
  } else {
    ElMessage.info("Auto-Monitor deactivated.")
  }
}
</script>

<template>
  <div class="screener-view">
    <div class="top-section">
      <div class="section-header">
        <h3>Strategy Scanner</h3>
      </div>
      <div class="editor-wrapper">
        <vue-monaco-editor
          v-model:value="code"
          theme="vs-dark"
          language="python"
          :options="{
            minimap: { enabled: false },
            automaticLayout: true,
            scrollBeyondLastLine: false,
            fontSize: 13
          }"
          height="300px"
        />
      </div>
    </div>

    <div class="action-bar">
      <el-button type="primary" :loading="isLoading" @click="runScreener">
        Run Screener (扫描股票)
      </el-button>

      <div class="monitor-switch">
        <span>Auto-Monitor (自动盯盘)</span>
        <el-switch v-model="autoMonitor" @change="toggleMonitor" />
      </div>
    </div>

    <div class="results-section">
      <h3>Screening Results</h3>
      <el-table :data="results" style="width: 100%" stripe border>
        <el-table-column prop="symbol" label="Symbol" width="120" />
        <el-table-column prop="name" label="Name" width="150" />
        <el-table-column prop="price" label="Signal Price">
          <template #default="scope">
            ¥{{ scope.row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="signal_date" label="Signal Date" width="180" />
        <el-table-column prop="signal_type" label="Type" width="100">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.signal_type }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.screener-view {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  box-sizing: border-box;
  overflow-y: auto;
}

.top-section {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.section-header {
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.monitor-switch {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
}

.results-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}
</style>
