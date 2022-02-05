import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
//import Control from '../views/Control.vue'
//import License from '../views/License.vue'
//import Openfaas from '../views/Openfaas.vue'
//import Project from '../views/project/Project.vue'
//import Script from '../views/project/Script.vue'
//import Egg from '../views/Egg.vue'
//import NotFound from '../views/NotFound.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/control',
    name: 'Control',
    //component: Control
    component: () => import('../views/Control.vue')

  },
  {
    path: '/openfaas',
    name: 'Openfaas',
    //component: Openfaas
    component: () => import('../views/Openfaas.vue')
  },
  {
    path: '/license',
    name: 'License',
    //component: License
    component: () => import('../views/License.vue')
  },
  {
    path: '/project/:id',
    name: 'Project',
    //component: Project,
    component: () => import('../views/project/Project.vue'),
    props: true
  },
  {
    path: '/project/:pid/:id',
    name: 'Script',
    component: () => import('../views/project/Script.vue'),
    //component: Script,
    props: true
  },
  {
    path: '/check/:script',
    name: 'Check',
    component: () => import('../views/Check.vue'),
    props: true
  },
  {
    path: '/egg',
    name: 'Egg',
    component: () => import('../views/Egg.vue')
    //component: Egg,
  },
  //404
  {
    path: '/:catchAll(.*)',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
    //component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
