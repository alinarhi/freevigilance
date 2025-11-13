import { createRouter, createWebHistory } from 'vue-router'
import TasksView from '@/views/TasksView.vue'
import LoginView from '@/views/LoginView.vue'
import { useUserStore } from '@/stores/user';
import PVAsView from '@/views/PVAsView.vue';
import PVAObligationsView from '@/views/PVAObligationsView.vue';
import AuditlogView from '@/views/AuditlogView.vue';
import TaskView from '@/views/TaskView.vue';
import ObligationTasksView from '@/views/ObligationTasksView.vue';
import NotFoundView from '@/views/NotFoundView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/tasks'
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: TasksView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/tasks/:id',
      name: 'task',
      component: TaskView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/pvas',
      name: 'pvas',
      component: PVAsView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/pvas/:id',
      name: 'pva',
      component: PVAObligationsView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/obligations/:id',
      name: 'obligation',
      component: ObligationTasksView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/auditlog',
      name: 'auditlog',
      component: AuditlogView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/logout',
      redirect: '/login'
    },
    { 
      path: '/:pathMatch(.*)*',
      name: 'notfound', 
      component: NotFoundView },

  ],
})

router.beforeEach(async (to, from, next) => {
  const store = useUserStore();
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router
