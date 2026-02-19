
<script setup lang="ts">
import { ref } from 'vue'

const code = ref(`import pandas as pd
from app.engine.base import BaseStrategy

class MultiTimeframeKDJStrategy(BaseStrategy):
    def init(self):
        self.n = 9
        self.m1 = 3
        self.m2 = 3
        self.m20_period = 20

    def next(self):
        df = self.data
        if len(df) < self.m20_period + 5: return
        symbol = str(df['symbol'].iloc[-1])
        current_close = df['close'].iloc[-1]

        if symbol.startswith('68'): return # Exclude STAR Market
        if df['amount'].iloc[-1] < 10000000: return # Liquidity filter

        # Daily Indicators
        ma20 = df['close'].rolling(window=self.m20_period).mean()
        low_min = df['low'].rolling(window=self.n).min()
        high_max = df['high'].rolling(window=self.n).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(alpha=1/self.m1, adjust=False).mean()
        d = k.ewm(alpha=1/self.m2, adjust=False).mean()
        j = 3 * k - 2 * d

        # Daily Conditions
        A3 = (current_close > df['open'].iloc[-1]) and (ma20.iloc[-1] > ma20.iloc[-2]) and (current_close > ma20.iloc[-1])
        KDJJ = (j.iloc[-2] <= 30) and (j.iloc[-1] > j.iloc[-2]) and (j.iloc[-2] < j.iloc[-3])
        if not (A3 and KDJJ): return

        # Weekly Indicators (Resampling)
        # Note: self.data index is DatetimeIndex
        df_weekly = df.resample('W-FRI').agg({'high':'max', 'low':'min', 'close':'last'}).dropna()
        if len(df_weekly) < self.n: return

        w_low_min = df_weekly['low'].rolling(window=self.n).min()
        w_high_max = df_weekly['high'].rolling(window=self.n).max()
        w_rsv = (df_weekly['close'] - w_low_min) / (w_high_max - w_low_min) * 100
        w_k = w_rsv.ewm(alpha=1/self.m1, adjust=False).mean()
        w_d = w_k.ewm(alpha=1/self.m2, adjust=False).mean()

        just_crossed = (w_k.iloc[-1] > w_d.iloc[-1]) and (w_k.iloc[-2] <= w_d.iloc[-2])
        about_to_cross = (w_k.iloc[-1] <= w_d.iloc[-1]) and (abs(w_k.iloc[-1] - w_d.iloc[-1]) < 2.0) and (w_k.iloc[-1] > w_k.iloc[-2])

        if not (just_crossed or about_to_cross): return

        # Execution
        if self.position.quantity == 0:
            self.buy(100)
        elif current_close < ma20.iloc[-1]:
            self.sell(self.position.quantity)
`)

const runBacktest = () => {
  console.log('Running backtest with code:', code.value)
  // TODO: Implement backend integration
}
</script>

<template>
  <div class="lab-view">
    <div class="editor-pane">
      <div class="pane-header">
        <h3>Strategy Editor</h3>
      </div>
      <div class="editor-container">
        <vue-monaco-editor
          v-model:value="code"
          theme="vs-dark"
          language="python"
          :options="{
            minimap: { enabled: false },
            automaticLayout: true,
            scrollBeyondLastLine: false,
            fontSize: 14
          }"
          height="100%"
        />
      </div>
    </div>

    <div class="visual-pane">
      <div class="pane-header actions-header">
        <h3>Backtest Result</h3>
        <el-button type="primary" @click="runBacktest">一键回测 (Run Backtest)</el-button>
      </div>
      <div class="chart-container">
        <div class="chart-placeholder-text">
          Backtest visualization will appear here
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lab-view {
  display: flex;
  flex-direction: row; /* Ensure split view */
  height: calc(100vh - 80px); /* Adjust based on header height */
  gap: 10px;
  padding: 10px;
  box-sizing: border-box;
}

.editor-pane, .visual-pane {
  flex: 1; /* Split 50% */
  display: flex;
  flex-direction: column;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.pane-header {
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pane-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.editor-container {
  flex: 1;
  overflow: hidden; /* Important for monaco automaticLayout */
  position: relative; /* Container needs position for monaco to fill */
}

.chart-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
  position: relative;
}

.chart-placeholder-text {
  color: #909399;
  font-size: 14px;
}
</style>
