
<script setup lang="ts">
import { ref, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const code = ref(`# Imports are pre-loaded in the sandbox:
# import pandas as pd
# from app.engine.base import BaseStrategy

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

const chartRef = ref<HTMLElement | null>(null)
const hasResult = ref(false)
let myChart: echarts.ECharts | null = null

const runBacktest = async () => {
  try {
    const payload = {
      strategy_code: code.value,
      symbol: "000001",
      start_date: "20230101",
      end_date: "20240101"
    }

    ElMessage.info('Running backtest...')

    // Assuming backend is running on 8000
    const response = await axios.post('http://localhost:8000/api/v1/backtest', payload)
    const result = response.data

    if (result.equity_curve && result.equity_curve.length > 0 && result.kline_data) {
      const dates = result.kline_data.map((item: any) => item.date)
      const ohlc = result.kline_data.map((item: any) => [item.open, item.close, item.low, item.high])
      const equityValues = result.equity_curve.map((item: any) => item.equity)

      // Process Trades for Markers
      const buyMarkers = result.trades
        .filter((t: any) => t.side === 'buy')
        .map((t: any) => [t.timestamp.substring(0, 10), t.price])

      const sellMarkers = result.trades
        .filter((t: any) => t.side === 'sell')
        .map((t: any) => [t.timestamp.substring(0, 10), t.price])

      hasResult.value = true

      // Wait for DOM update
      await nextTick()

      if (chartRef.value) {
        if (myChart) {
           myChart.dispose() // Re-init for clean slate or use clear
        }
        myChart = echarts.init(chartRef.value)

        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' }
            },
            axisPointer: {
                link: { xAxisIndex: 'all' }
            },
            grid: [
                {
                    left: '3%',
                    right: '4%',
                    height: '60%'
                },
                {
                    left: '3%',
                    right: '4%',
                    top: '75%',
                    height: '20%'
                }
            ],
            xAxis: [
                {
                    type: 'category',
                    data: dates,
                    boundaryGap: false,
                    axisLine: { onZero: false },
                    splitLine: { show: false },
                    min: 'dataMin',
                    max: 'dataMax'
                },
                {
                    type: 'category',
                    gridIndex: 1,
                    data: dates,
                    boundaryGap: false,
                    axisLine: { onZero: false },
                    axisTick: { show: false },
                    splitLine: { show: false },
                    axisLabel: { show: false },
                    min: 'dataMin',
                    max: 'dataMax'
                }
            ],
            yAxis: [
                {
                    scale: true,
                    splitArea: { show: true }
                },
                {
                    scale: true,
                    gridIndex: 1,
                    splitNumber: 2,
                    axisLabel: { show: false },
                    axisLine: { show: false },
                    axisTick: { show: false },
                    splitLine: { show: false }
                }
            ],
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0, 1],
                    start: 50,
                    end: 100
                },
                {
                    show: true,
                    type: 'slider',
                    xAxisIndex: [0, 1],
                    top: '95%',
                    start: 50,
                    end: 100
                }
            ],
            series: [
                {
                    name: 'K-Line',
                    type: 'candlestick',
                    data: ohlc,
                    itemStyle: {
                        color: '#ef232a', // Up color (Red)
                        color0: '#14b143', // Down color (Green)
                        borderColor: '#ef232a',
                        borderColor0: '#14b143'
                    }
                },
                {
                    name: 'Buy',
                    type: 'scatter',
                    symbol: 'triangle',
                    symbolSize: 15,
                    itemStyle: { color: '#ef232a' },
                    data: buyMarkers,
                    z: 10
                },
                {
                    name: 'Sell',
                    type: 'scatter',
                    symbol: 'triangle',
                    symbolSize: 15,
                    itemStyle: { color: '#14b143' },
                    symbolRotate: 180,
                    data: sellMarkers,
                    z: 10
                },
                {
                    name: 'Equity',
                    type: 'line',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    data: equityValues,
                    showSymbol: false,
                    lineStyle: { width: 2 }
                }
            ]
        }

        myChart.setOption(option)
        myChart.resize()

        const returnPct = (result.total_return * 100).toFixed(2)
        ElMessage.success(`Backtest Complete! Return: ${returnPct}%`)
      }
    } else {
        ElMessage.warning('Backtest finished but returned no data.')
    }
  } catch (e: any) {
    console.error(e)
    const msg = e.response?.data?.detail || e.message
    ElMessage.error('Backtest failed: ' + msg)
  }
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
        <div v-show="!hasResult" class="chart-placeholder-text">
          Backtest visualization will appear here
        </div>
        <div ref="chartRef" style="width: 100%; height: 100%;" v-show="hasResult"></div>
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
  overflow: hidden;
}

.chart-placeholder-text {
  color: #909399;
  font-size: 14px;
  position: absolute;
}
</style>
