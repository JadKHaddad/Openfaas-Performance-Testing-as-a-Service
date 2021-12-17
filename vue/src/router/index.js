import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Control from '../views/Control.vue'
import License from '../views/License.vue'
import Openfaas from '../views/Openfaas.vue'
import Project from '../views/project/Project.vue'
import Script from '../views/project/Script.vue'
import Egg from '../views/Egg.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/control',
    name: 'Control',
    component: Control
  },
  {
    path: '/openfaas',
    name: 'Openfaas',
    component: Openfaas
  },
  {
    path: '/license',
    name: 'License',
    component: License
  },
  {
    path: '/project/:id',
    name: 'Project',
    component: Project,
    props: true
  },
  {
    path: '/project/:pid/:id',
    name: 'Script',
    component: Script,
    props: true
  },
  {
    path: '/egg',
    name: 'Egg',
    component: Egg,
  },
  //404
  {
    path: '/:catchAll(.*)',
    name: 'NotFound',
    component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
