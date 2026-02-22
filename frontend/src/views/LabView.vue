
<script setup lang="ts">
import { ref, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
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

const chartRef = ref<HTMLElement | null>(null)
const hasResult = ref(false)
const timeframe = ref('daily')
// Default date range: Past year
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setFullYear(new Date().getFullYear() - 1)),
  new Date()
])
let myChart: echarts.ECharts | null = null

const formatDate = (date: Date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}${m}${d}`
}

const runBacktest = async () => {
  try {
    if (!dateRange.value || dateRange.value.length < 2) {
      ElMessage.warning('请选择回测时间范围')
      return
    }

    const payload = {
      strategy_code: code.value,
      symbol: "000001",
      start_date: formatDate(dateRange.value[0]),
      end_date: formatDate(dateRange.value[1]),
      period: timeframe.value
    }

    ElMessage.info(`正在执行回测计算... (${timeframe.value}, ${payload.start_date}-${payload.end_date})`)

    const response = await axios.post('http://localhost:8000/api/v1/backtest', payload)
    const result = response.data

    if (result.equity_curve && result.equity_curve.length > 0 && result.kline_data) {
      // Data Preparation
      const dates = result.kline_data.map((item: any) => item.date)
      const ohlc = result.kline_data.map((item: any) => [item.open, item.close, item.low, item.high])

      const ma20 = result.kline_data.map((item: any) => item.ma20)

      const volume = result.kline_data.map((item: any) => item.volume)
      const vol_ma5 = result.kline_data.map((item: any) => item.vol_ma5)

      const macd_dif = result.kline_data.map((item: any) => item.macd_dif)
      const macd_dea = result.kline_data.map((item: any) => item.macd_dea)
      const macd_bar = result.kline_data.map((item: any) => item.macd_bar)

      const kdj_k = result.kline_data.map((item: any) => item.kdj_k)
      const kdj_d = result.kline_data.map((item: any) => item.kdj_d)
      const kdj_j = result.kline_data.map((item: any) => item.kdj_j)

      const equityValues = result.equity_curve.map((item: any) => item.equity)

      // Markers
      const buyMarkers = result.trades
        .filter((t: any) => t.side === 'buy')
        .map((t: any) => [t.timestamp.substring(0, 10), t.price])

      const sellMarkers = result.trades
        .filter((t: any) => t.side === 'sell')
        .map((t: any) => [t.timestamp.substring(0, 10), t.price])

      hasResult.value = true

      await nextTick()

      if (chartRef.value) {
        if (myChart) {
           myChart.dispose()
        }
        myChart = echarts.init(chartRef.value)

        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' }
            },
            axisPointer: {
                link: { xAxisIndex: 'all' },
                label: { backgroundColor: '#777' }
            },
            grid: [
                { left: '3%', right: '4%', top: '5%', height: '35%' }, // Grid 0: Main (K-Line + MA)
                { left: '3%', right: '4%', top: '45%', height: '12%' }, // Grid 1: Volume
                { left: '3%', right: '4%', top: '60%', height: '12%' }, // Grid 2: MACD
                { left: '3%', right: '4%', top: '75%', height: '12%' }, // Grid 3: KDJ
                { left: '3%', right: '4%', top: '90%', height: '10%' }  // Grid 4: Equity
            ],
            xAxis: [
                { type: 'category', data: dates, gridIndex: 0, axisLine: { onZero: false }, min: 'dataMin', max: 'dataMax' },
                { type: 'category', data: dates, gridIndex: 1, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
                { type: 'category', data: dates, gridIndex: 2, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
                { type: 'category', data: dates, gridIndex: 3, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
                { type: 'category', data: dates, gridIndex: 4, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' }
            ],
            yAxis: [
                { scale: true, gridIndex: 0, splitArea: { show: true } },
                { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
                { scale: true, gridIndex: 2, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
                { scale: true, gridIndex: 3, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
                { scale: true, gridIndex: 4, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
            ],
            dataZoom: [
                { type: 'inside', xAxisIndex: [0, 1, 2, 3, 4], start: 50, end: 100 },
                { type: 'slider', xAxisIndex: [0, 1, 2, 3, 4], top: '96%', start: 50, end: 100 }
            ],
            series: [
                // Grid 0
                {
                    name: 'K-Line', type: 'candlestick', data: ohlc,
                    itemStyle: { color: '#ef232a', color0: '#14b143', borderColor: '#ef232a', borderColor0: '#14b143' }
                },
                { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { opacity: 0.5 } },
                {
                    name: 'Buy', type: 'scatter', symbol: 'triangle', symbolSize: 15,
                    itemStyle: { color: '#ef232a' }, data: buyMarkers, z: 10
                },
                {
                    name: 'Sell', type: 'scatter', symbol: 'triangle', symbolSize: 15,
                    itemStyle: { color: '#14b143' }, symbolRotate: 180, data: sellMarkers, z: 10
                },
                // Grid 1: Volume
                { name: 'Volume', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volume, itemStyle: { color: '#7fbe9e' } },
                { name: 'VOL_MA5', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: vol_ma5, smooth: true },
                // Grid 2: MACD
                { name: 'DIF', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: macd_dif },
                { name: 'DEA', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: macd_dea },
                { name: 'MACD', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: macd_bar, itemStyle: { color: '#5470c6' } },
                // Grid 3: KDJ
                { name: 'K', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_k },
                { name: 'D', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_d },
                { name: 'J', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_j },
                // Grid 4: Equity
                { name: 'Equity', type: 'line', xAxisIndex: 4, yAxisIndex: 4, data: equityValues, showSymbol: false, lineStyle: { width: 2 } }
            ]
        }

        myChart.setOption(option)
        myChart.resize()

        const returnPct = (result.total_return * 100).toFixed(2)
        ElMessage.success(`回测完成！区间收益率：${returnPct}%`)
      }
    } else {
        ElMessage.warning('回测已完成但没有返回数据。')
    }
  } catch (e: any) {
    console.error(e)
    const msg = e.response?.data?.detail || e.message
    ElMessage.error('回测失败: ' + msg)
  }
}
</script>

<template>
  <div class="lab-view">
    <div class="editor-pane">
      <div class="pane-header">
        <h3>策略代码编辑器</h3>
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
        <h3>回测与图表分析</h3>
        <div class="actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
              style="margin-right: 15px; width: 240px;"
            />
            <el-radio-group v-model="timeframe" size="small" style="margin-right: 15px;">
                <el-radio-button label="daily">日线</el-radio-button>
                <el-radio-button label="weekly">周线</el-radio-button>
                <el-radio-button label="monthly">月线</el-radio-button>
            </el-radio-group>
            <el-button type="primary" @click="runBacktest">一键回测</el-button>
        </div>
      </div>
      <div class="chart-container">
        <div v-show="!hasResult" class="chart-placeholder-text">
          回测图表与买卖点标记将在此显示
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

.visual-pane {
    overflow-y: auto; /* Allow scrolling for tall chart */
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
  min-height: 800px; /* Increased height for multi-grid */
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
