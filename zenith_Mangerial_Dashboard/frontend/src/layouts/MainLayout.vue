<template>
  <q-layout view="HHh Lpr lFf">
    <q-header elevated class="bg-white text-dark">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          <q-avatar size="32px" class="q-mr-sm">
            <img src="/logo.png" alt="Logo">
          </q-avatar>
          Zenith
        </q-toolbar-title>

        <div class="q-ml-auto">
          <q-btn flat round dense icon="notifications" class="q-mr-sm">
            <!-- <q-badge color="red" floating>3</q-badge> -->
          </q-btn>
          <q-btn flat dense icon="account_circle" class="q-mr-sm q-px-sm" style="border-radius: 50px;" :label="auth?.user?.first_name || ''">
            <q-menu>
              <q-list style="min-width: 150px;">
                <q-item clickable v-close-popup @click="handleLogout">
                  <q-item-section avatar>
                    <q-icon name="logout" color="negative" />
                  </q-item-section>
                  <q-item-section>Logout</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </div>
      </q-toolbar>

    </q-header>

    <q-drawer
      v-model="drawerModel"
      show-if-above
      bordered
      :width="280"
      :breakpoint="1024"
      :mini="leftDrawerOpen"
      class="bg-white text-dark"
    >
      <div class="">
        <q-list>
          <template v-for="(category, index) in drawerLinks" :key="category.category">
            <q-item-label header class="text-subtitle2 text-grey-6">
              {{ category.category }}
            </q-item-label>

            <EssentialLink
              v-for="link in category.links"
              :key="link.title"
              v-bind="link"
            />

            <template v-if="category.category === 'Management'">
              <q-item-label header class="text-subtitle2 text-grey-6">
                Managerial Dashboards
              </q-item-label>

              <EssentialLink
                title="TL Group Dashboard"
                caption="Team onboarding progress"
                icon="groups"
                link="/tl-group-dashboard"
              />

              <q-item v-for="title in upcomingManagerialDashboards" :key="title" disable>
                <q-item-section avatar>
                  <q-icon name="insights" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ title }}</q-item-label>
                  <q-item-label caption>Coming soon</q-item-label>
                </q-item-section>
              </q-item>
            </template>

            <q-separator v-if="index < drawerLinks.length - 1" class="q-my-md" />
          </template>

          <q-separator class="q-my-md" />

          <q-item-label header class="text-subtitle2 text-grey-6">
            Settings
          </q-item-label>

          <EssentialLink
            v-for="link in settingsLinks"
            :key="link.title"
            v-bind="link"
            @action="handleLinkAction"
          />
        </q-list>
      </div>

      <!-- <div class="absolute-bottom q-pa-md">
        <q-card class="bg-primary text-white">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle2">Need Help?</div>
            <div class="text-caption">Contact support for assistance</div>
          </q-card-section>
          <q-card-actions align="right" class="q-pa-sm">
            <q-btn flat dense label="Contact" size="sm" />
          </q-card-actions>
        </q-card>
      </div> -->
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'stores/auth-store'
import EssentialLink from 'components/EssentialLink.vue'

const settingsLinks = [
  // {
  //   title: 'Settings',
  //   caption: 'App configuration',
  //   icon: 'settings',
  //   link: '/settings'
  // },
  {
    title: 'Profile',
    caption: 'Account settings',
    icon: 'account_circle',
    link: '/profile'
  },
  {
    title: 'Logout',
    caption: 'Sign out',
    icon: 'logout',
    action: 'logout'
  }
]

const upcomingManagerialDashboards = [
  'PM Dashboard',
  'Leadership Dashboard',
  'Other Role Based Dashboard'
]

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink
  },

  setup () {
    const leftDrawerOpen = ref(false)
    const drawerModel = ref(true)
    const router = useRouter()
    const auth = useAuthStore()

    // Short captions for drawer items (defined in frontend)
    const pageCaptions = {
      home: 'News & Updates',
      dashboard: 'Overview & Analytics',
      status_report: 'Status Update Reports',
      files: 'File management',
      kra: 'Key Result Areas',
      organization: 'Company details',
      teams: 'Team management',
      members: 'User management',
      departments: 'Department structure',
      permissions: 'Access control',
      reports: 'Analytics & reports',
      spreadsheet: 'Data & budget sheets',
      'page-manager': 'Create custom pages',
      documents: 'File management',
      calendar: 'Schedule & events',
      daily_status: 'Update Tasks',
      clients: 'Client management',
      projects: 'Project management',
    }

    // Build drawer links from permissions
    const drawerLinks = computed(() => {
      const permissions = auth.permissions || []

      // Group permissions by page to get unique pages user has access to
      const pageMap = new Map()

       permissions.forEach(perm => {
         if (perm.page === 'home') return
         if (!pageMap.has(perm.page)) {
          pageMap.set(perm.page, {
            title: perm.display_name,
            caption: pageCaptions[perm.page] || '',
            icon: perm.icon,
            link: perm.route,
            category: perm.category,
            order: perm.order || 0
          })
        }
      })

      // Convert to array and sort by order
      const pages = Array.from(pageMap.values()).sort((a, b) => a.order - b.order)

      // Group by category
      const categoryMap = new Map()
      pages.forEach(page => {
        const category = page.category || 'general'
        if (!categoryMap.has(category)) {
          categoryMap.set(category, [])
        }
        categoryMap.get(category).push(page)
      })

      // Define category display names and icons
      const categoryInfo = {
        main: { name: 'Main', icon: 'dashboard' },
        management: { name: 'Management', icon: 'settings' },
        organization: { name: 'Organization', icon: 'business' },
        general: { name: 'General', icon: 'apps' }
      }

      // Build final structure
      const result = []
      categoryMap.forEach((links, category) => {
        const info = categoryInfo[category] || { name: category, icon: 'folder' }
        result.push({
          category: info.name,
          icon: info.icon,
          links: links
        })
      })

      // Sort categories by predefined order
      const categoryOrder = ['main', 'organization', 'management', 'general']
      result.sort((a, b) => {
        const aIndex = categoryOrder.indexOf(a.category.toLowerCase()) ?? 999
        const bIndex = categoryOrder.indexOf(b.category.toLowerCase()) ?? 999
        return aIndex - bIndex
      })

      return result
    })

    const handleLinkAction = (action) => {
      if (action === 'logout') {
        handleLogout()
      }
    }

    const handleLogout = () => {
      auth.logout()
      router.push('/login')
    }

    return {
      auth,
      drawerLinks,
      settingsLinks,
      upcomingManagerialDashboards,
      leftDrawerOpen,
      drawerModel,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
      handleLinkAction,
      handleLogout
    }
  }
})
</script>
