
<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    symbol: '000001',
    name: '平安银行',
    price: 10.5,
    change: 1.2,
    volume: 1000000,
    turnover: 0.5
  },
  {
    symbol: '600519',
    name: '贵州茅台',
    price: 1800.0,
    change: -0.5,
    volume: 50000,
    turnover: 0.1
  }
])
</script>

<template>
  <div class="market-view">
    <h3>全市场行情</h3>
    <el-table :data="tableData" style="width: 100%" stripe>
      <el-table-column prop="symbol" label="代码" width="120" />
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column prop="price" label="最新价" />
      <el-table-column prop="change" label="涨跌幅">
        <template #default="scope">
          <span :style="{ color: scope.row.change >= 0 ? 'red' : 'green' }">
            {{ scope.row.change }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="成交量" />
      <el-table-column prop="turnover" label="换手率" />
    </el-table>
  </div>
</template>

<style scoped>
.market-view {
  padding: 20px;
}
</style>
