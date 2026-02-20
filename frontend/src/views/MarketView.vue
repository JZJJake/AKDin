
<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// State
const stockList = ref<any[]>([])
const activeSymbol = ref('')
const searchSymbol = ref('')
const timeframe = ref('daily')
const chartRef = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null

// Fetch Stock List
const fetchStockList = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/stocks/list')
    stockList.value = response.data.stocks
    if (stockList.value.length > 0) {
      activeSymbol.value = stockList.value[0].symbol
      fetchKlineData()
    }
  } catch (e) {
    ElMessage.error('获取股票列表失败')
  }
}

// Search Handler
const handleSearch = () => {
  if (searchSymbol.value) {
    activeSymbol.value = searchSymbol.value
    // Ideally check if valid, but for now just fetch
    fetchKlineData()
  }
}

// Select Stock
const selectStock = (symbol: string) => {
  activeSymbol.value = symbol
  fetchKlineData()
}

// Fetch Kline and Render Chart
const fetchKlineData = async () => {
  if (!activeSymbol.value) return

  try {
    const response = await axios.get(`http://localhost:8000/api/v1/stocks/${activeSymbol.value}/kline`, {
      params: { period: timeframe.value }
    })
    const data = response.data.kline_data

    if (data && data.length > 0) {
      renderChart(data)
    } else {
      ElMessage.warning('暂无K线数据')
      if (myChart) myChart.clear()
    }
  } catch (e) {
    ElMessage.error('获取K线数据失败')
  }
}

// Render ECharts (4-Grid)
const renderChart = async (klineData: any[]) => {
  await nextTick()
  if (!chartRef.value) return

  if (myChart) {
    myChart.dispose()
  }
  myChart = echarts.init(chartRef.value)

  const dates = klineData.map(item => item.date)
  const ohlc = klineData.map(item => [item.open, item.close, item.low, item.high])
  const ma20 = klineData.map(item => item.ma20)
  const volume = klineData.map(item => item.volume)
  const vol_ma5 = klineData.map(item => item.vol_ma5)
  const macd_dif = klineData.map(item => item.macd_dif)
  const macd_dea = klineData.map(item => item.macd_dea)
  const macd_bar = klineData.map(item => item.macd_bar)
  const kdj_k = klineData.map(item => item.kdj_k)
  const kdj_d = klineData.map(item => item.kdj_d)
  const kdj_j = klineData.map(item => item.kdj_j)

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
      { left: '3%', right: '1%', top: '2%', height: '45%' }, // Grid 0: Price
      { left: '3%', right: '1%', top: '50%', height: '15%' }, // Grid 1: Volume
      { left: '3%', right: '1%', top: '68%', height: '15%' }, // Grid 2: MACD
      { left: '3%', right: '1%', top: '86%', height: '12%' }  // Grid 3: KDJ
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLine: { onZero: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', data: dates, gridIndex: 1, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', data: dates, gridIndex: 2, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', data: dates, gridIndex: 3, axisLine: { onZero: false }, axisLabel: { show: false }, axisTick: { show: false }, min: 'dataMin', max: 'dataMax' }
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitArea: { show: true } },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
      { scale: true, gridIndex: 2, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
      { scale: true, gridIndex: 3, splitNumber: 2, axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1, 2, 3], start: 50, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1, 2, 3], top: '98%', height: '2%', start: 50, end: 100, showDetail: false, handleSize: '0%' } // Minimal slider
    ],
    series: [
      // Grid 0
      {
        name: 'K-Line', type: 'candlestick', data: ohlc,
        itemStyle: { color: '#ef232a', color0: '#14b143', borderColor: '#ef232a', borderColor0: '#14b143' }
      },
      { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { opacity: 0.5 } },

      // Grid 1
      { name: 'Volume', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volume, itemStyle: { color: '#7fbe9e' } },
      { name: 'VOL_MA5', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: vol_ma5, smooth: true },

      // Grid 2
      { name: 'DIF', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: macd_dif },
      { name: 'DEA', type: 'line', xAxisIndex: 2, yAxisIndex: 2, data: macd_dea },
      { name: 'MACD', type: 'bar', xAxisIndex: 2, yAxisIndex: 2, data: macd_bar, itemStyle: { color: '#5470c6' } },

      // Grid 3
      { name: 'K', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_k },
      { name: 'D', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_d },
      { name: 'J', type: 'line', xAxisIndex: 3, yAxisIndex: 3, data: kdj_j }
    ]
  }

  myChart.setOption(option)
  myChart.resize()
}

onMounted(() => {
  fetchStockList()
  window.addEventListener('resize', () => myChart?.resize())
})
</script>

<template>
  <div class="market-view">
    <div class="stock-list-pane">
      <div class="search-box">
        <el-input
          v-model="searchSymbol"
          placeholder="输入代码 (e.g. 600519)"
          size="small"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
      <div class="list-container">
        <div
          v-for="stock in stockList"
          :key="stock.symbol"
          class="stock-item"
          :class="{ active: stock.symbol === activeSymbol }"
          @click="selectStock(stock.symbol)"
        >
          <div class="stock-name">{{ stock.name }}</div>
          <div class="stock-symbol">{{ stock.symbol }}</div>
        </div>
      </div>
    </div>

    <div class="chart-pane">
      <div class="chart-toolbar">
        <div class="current-stock">
          <span class="symbol">{{ activeSymbol }}</span>
        </div>
        <el-radio-group v-model="timeframe" size="small" @change="fetchKlineData">
          <el-radio-button label="daily">日线</el-radio-button>
          <el-radio-button label="weekly">周线</el-radio-button>
          <el-radio-button label="monthly">月线</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-wrapper">
        <div ref="chartRef" style="width: 100%; height: 100%;"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.market-view {
  display: flex;
  height: 100%;
  background-color: #1e1e1e; /* Dark theme background */
  color: #ccc;
}

.stock-list-pane {
  width: 250px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
  background-color: #252526;
}

.search-box {
  padding: 10px;
  background-color: #252526;
}

.list-container {
  flex: 1;
  overflow-y: auto;
}

.stock-item {
  padding: 8px 15px;
  cursor: pointer;
  border-bottom: 1px solid #333;
}

.stock-item:hover {
  background-color: #2a2d2e;
}

.stock-item.active {
  background-color: #37373d;
  border-left: 3px solid #007acc;
}

.stock-name {
  font-size: 14px;
  color: #eee;
  font-weight: bold;
}

.stock-symbol {
  font-size: 12px;
  color: #888;
}

.chart-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
}

.chart-toolbar {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #252526;
  border-bottom: 1px solid #333;
}

.current-stock .symbol {
  font-size: 18px;
  color: #fff;
  font-weight: bold;
}

.chart-wrapper {
  flex: 1;
  overflow: hidden;
}
</style>
