const routes = [
  {
    path: '/login',
    component: () => import('layouts/PlainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/LoginPage.vue') }
    ]
  },
  {
    path: '/set-password',
    component: () => import('layouts/PlainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/SetPasswordPage.vue') }
    ]
  },
  {
    path: '/spreadsheet',
    component: () => import('layouts/PlainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/SpreadsheetPage.vue') }
    ]
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/HomePage.vue'),
        alias: 'home'
      },
      {
        path: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
      },
      { path: 'onboarding-dashboard', component: () => import('pages/OnboardingDashboard.vue') },
      { path: 'onboarding-metrics', component: () => import('pages/Onboardingmetrics.vue') },
      { path: 'employee-onboarding', component: () => import('pages/EmployeeOnboarding.vue') },
      { path: 'week-0', component: () => import('pages/Week0.vue') },
      { path: 'vdi-activation', component: () => import('pages/Week0.vue') },
      { path: 'day-1', component: () => import('pages/Day1.vue') },
      { path: 'day-2', component: () => import('pages/Week0.vue') },
      { path: 'day-3', component: () => import('pages/Week0.vue') },
      { path: 'day-4', component: () => import('pages/Week0.vue') },
      { path: 'day-5', component: () => import('pages/Week0.vue') },
      { path: 'status-report', component: () => import('pages/StatusReportPage.vue') },
      { path: 'files', component: () => import('pages/FilesPage.vue') },
      { path: 'members', component: () => import('pages/MembersPage.vue') },
      { path: 'members/add/:id?', component: () => import('pages/AddMemberPage.vue') },
      { path: 'permissions', component: () => import('pages/PermissionsPage.vue') },
      { path: 'clients', component: () => import('pages/ClientsPage.vue') },
      { path: 'projects', component: () => import('pages/ProjectsPage.vue') },
      { path: 'daily-status', component: () => import('pages/DailyStatusPage.vue') },
      { path: 'profile', component: () => import('pages/ProfilePage.vue') },
      { path: 'settings/holidays', component: () => import('pages/HolidaySettingsPage.vue') },
      { path: 'page-manager', component: () => import('pages/PageManager.vue') },
      { path: 'page-builder/:pageId?', name: 'PageBuilder', component: () => import('pages/PageBuilder.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
