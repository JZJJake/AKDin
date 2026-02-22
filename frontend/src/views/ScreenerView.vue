
<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const code = ref(`# Imports are pre-loaded in the sandbox:
# import pandas as pd
# from app.engine.base import BaseStrategy

class ProfessionalStrategy(BaseStrategy):
    def init(self):
        self.n = 9
        self.m1 = 3
        self.m2 = 3
        self.ma_period = 20

    def next(self):
        df = self.data
        if len(df) < 60: return

        # 0. 基础数据
        symbol = str(df['symbol'].iloc[-1])
        current_close = df['close'].iloc[-1]

        # 1. 基础过滤 (Basic Filter)
        # 过滤科创板 (68开头)
        if symbol.startswith('68'): return
        # 过滤ST股 (假设数据中有name列，或需要在选股器外部过滤)
        if 'name' in df.columns and 'ST' in str(df['name'].iloc[-1]): return
        # 流动性过滤: 成交金额 > 1000万
        if 'amount' in df.columns and df['amount'].iloc[-1] < 10000000: return

        # 2. 日线级别逻辑 (Daily Logic)
        # 计算 MA20
        ma20 = df['close'].rolling(window=self.ma_period).mean()

        # 计算 KDJ
        low_min = df['low'].rolling(window=self.n).min()
        high_max = df['high'].rolling(window=self.n).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(alpha=1/self.m1, adjust=False).mean()
        d = k.ewm(alpha=1/self.m2, adjust=False).mean()
        j = 3 * k - 2 * d

        # A3 条件: 收阳线 & M20向上 & 收盘站上M20
        is_yang = current_close > df['open'].iloc[-1]
        ma20_up = ma20.iloc[-1] > ma20.iloc[-2]
        on_ma20 = current_close > ma20.iloc[-1]
        cond_a3 = is_yang and ma20_up and on_ma20

        # KDJJ 条件: J值触底反弹/金叉 (昨日J<=50, 今日J>昨日J, 昨日J<前日J)
        j_now = j.iloc[-1]
        j_prev1 = j.iloc[-2]
        j_prev2 = j.iloc[-3]
        cond_kdjj = (j_prev1 <= 50) and (j_now > j_prev1) and (j_prev1 < j_prev2)

        buy_signal = cond_a3 and cond_kdjj

        # 3. 周线级别逻辑 (Weekly Filter)
        # 只有当日线满足买入条件时，才去计算周线，节省性能
        if buy_signal:
            # 重采样为周线 (Week ending Friday)
            df_weekly = df.resample('W-FRI').agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
            }).dropna()

            if len(df_weekly) < 5: return # 样本不足

            # 趋势结构: 顶顶高(High)、底底高(Low)
            # 取最近两根完整周线 (不含当前周)
            w_last = df_weekly.iloc[-2]
            w_prev = df_weekly.iloc[-3]
            trend_up = (w_last['high'] > w_prev['high']) and (w_last['low'] > w_prev['low'])

            # 周线 MACD (12, 26, 9)
            w_ema12 = df_weekly['close'].ewm(span=12, adjust=False).mean()
            w_ema26 = df_weekly['close'].ewm(span=26, adjust=False).mean()
            w_dif = w_ema12 - w_ema26
            w_dea = w_dif.ewm(span=9, adjust=False).mean()
            # DEA (EDA) 向上
            dea_up = w_dea.iloc[-2] > w_dea.iloc[-3]

            # 周线 KDJ (9, 3, 3)
            w_low_min = df_weekly['low'].rolling(window=9).min()
            w_high_max = df_weekly['high'].rolling(window=9).max()
            w_rsv = (df_weekly['close'] - w_low_min) / (w_high_max - w_low_min) * 100
            w_k = w_rsv.ewm(alpha=1/3, adjust=False).mean()
            w_d = w_k.ewm(alpha=1/3, adjust=False).mean()
            w_j = 3 * w_k - 2 * w_d

            # KDJ 条件: 前一个J值在50以下且向上
            # 注意: iloc[-1]是当前周(未走完), 判断趋势通常看已完成的周(iloc[-2])
            # 但用户描述 "前一个J值" 可能指相对于当前时刻的上一个周期
            w_j_prev = w_j.iloc[-2]
            w_j_prev2 = w_j.iloc[-3]
            kdj_condition = (w_j_prev < 50) and (w_j_prev > w_j_prev2)

            if trend_up and dea_up and kdj_condition:
                if self.position.quantity == 0:
                    self.buy(100)

        # 4. 卖出条件 (Sell Logic)
        # 日线 J > 80 且拐头向下
        elif self.position.quantity > 0:
            if j_now > 80 and j_now < j_prev1:
                self.sell(self.position.quantity)
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

    ElMessage.info('正在执行全市场选股扫描... 请稍候')

    // Assuming backend is running on 8000
    const response = await axios.post('http://localhost:8000/api/v1/screen', payload)
    results.value = response.data.hits

    if (results.value.length > 0) {
      ElMessage.success(`扫描完成！共发现 ${results.value.length} 个买入信号`)
    } else {
      ElMessage.info('当前策略未扫描到符合条件的股票。')
    }
  } catch (e: any) {
    console.error(e)
    const msg = e.response?.data?.detail || e.message
    ElMessage.error('扫描失败: ' + msg)
  } finally {
    isLoading.value = false
  }
}

const toggleMonitor = (val: boolean) => {
  if (val) {
    ElMessage.success("自动盯盘已开启。买入信号将推送到微信。")
  } else {
    ElMessage.info("自动盯盘已关闭。")
  }
}
</script>

<template>
  <div class="screener-view">
    <div class="top-section">
      <div class="section-header">
        <h3>选股策略代码</h3>
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
        一键扫描全市场
      </el-button>

      <div class="monitor-switch">
        <span>自动盯盘 (开启后推送到微信)</span>
        <el-switch v-model="autoMonitor" @change="toggleMonitor" />
      </div>
    </div>

    <div class="results-section">
      <h3>选股扫描结果</h3>
      <el-table :data="results" style="width: 100%" stripe border>
        <el-table-column prop="symbol" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="price" label="触发价格">
          <template #default="scope">
            ¥{{ scope.row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="signal_date" label="信号日期" width="180" />
        <el-table-column prop="signal_type" label="类型" width="100">
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
