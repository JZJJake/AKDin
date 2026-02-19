
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
    <h3>Market Overview</h3>
    <el-table :data="tableData" style="width: 100%" stripe>
      <el-table-column prop="symbol" label="Symbol" width="120" />
      <el-table-column prop="name" label="Name" width="150" />
      <el-table-column prop="price" label="Current Price" />
      <el-table-column prop="change" label="Change %">
        <template #default="scope">
          <span :style="{ color: scope.row.change >= 0 ? 'red' : 'green' }">
            {{ scope.row.change }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="Volume" />
      <el-table-column prop="turnover" label="Turnover %" />
    </el-table>
  </div>
</template>

<style scoped>
.market-view {
  padding: 20px;
}
</style>
