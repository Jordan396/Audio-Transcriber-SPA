import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
  { path: '/audio-transcriber', component: 'Main' },
  { path: '*', component: '404NotFound' },
]

const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`)
  }
})

Vue.use(Router)

export default new Router({
  routes,
  mode: 'history'
})
