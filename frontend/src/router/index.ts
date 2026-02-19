
import { createRouter, createWebHistory } from 'vue-router'
import MarketView from '../views/MarketView.vue'
import LabView from '../views/LabView.vue'
import ScreenerView from '../views/ScreenerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/market'
    },
    {
      path: '/market',
      name: 'market',
      component: MarketView
    },
    {
      path: '/lab',
      name: 'lab',
      component: LabView
    },
    {
      path: '/screener',
      name: 'screener',
      component: ScreenerView
    }
  ]
})

export default router
