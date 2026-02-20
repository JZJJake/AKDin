
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <el-container class="layout-container">
    <el-header class="main-header">
      <div class="logo">
        <h2>智能量化投研平台</h2>
      </div>
      <el-menu
        router
        :default-active="$route.path"
        mode="horizontal"
        class="top-menu"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/market">行情中心</el-menu-item>
        <el-menu-item index="/lab">策略研究室</el-menu-item>
        <el-menu-item index="/screener">智能选股</el-menu-item>
      </el-menu>
    </el-header>

    <el-main class="main-content">
      <RouterView />
    </el-main>
  </el-container>
</template>

<style>
/* Global styles */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* Prevent body scroll */
}
#app {
  height: 100%;
}
</style>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  background-color: #545c64;
  display: flex;
  align-items: center;
  height: 50px !important; /* Compact height */
  padding: 0 20px;
}

.logo {
  margin-right: 40px;
  color: #fff;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  white-space: nowrap;
}

.top-menu {
  border-bottom: none;
  height: 50px;
  line-height: 50px;
  flex: 1;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.main-content {
  flex: 1;
  padding: 0; /* Remove default padding to let views take full space */
  overflow: hidden;
}
</style>
