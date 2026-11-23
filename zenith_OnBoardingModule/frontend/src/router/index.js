import { defineRouter } from '#q-app/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'stores/auth-store'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function ({ store }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  // Auth guard - redirect to login if not authenticated
  Router.beforeEach((to, from, next) => {
    const auth = useAuthStore(store)

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/set-password']

    // Allow access to public routes
    if (publicRoutes.includes(to.path)) {
      // If already logged in and trying to access login, redirect to dashboard
      if (to.path === '/login' && auth.isAuthenticated) {
        next('/')
      } else {
        next()
      }
      return
    }

    // Check authentication for all other routes
    if (!auth.isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  })

  return Router
})
