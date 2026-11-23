import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    role: null,
    permissions: [],
    organization: null
  }),

  getters: {
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    getRefreshToken: (state) => state.refreshToken,
    getRole: (state) => state.role,
    getOrganization: (state) => state.organization,
    hasPermission: (state) => (permission) => state.permissions.includes(permission),
    hasRole: (state) => (role) => state.role === role,
    isAdmin: (state) => state.role === 'admin' || state.permissions.includes('admin')
  },

  actions: {
    setUser(user) {
      this.user = user
      this.isAuthenticated = !!user
    },

    setToken(token) {
      this.token = token
    },

    setRefreshToken(refreshToken) {
      this.refreshToken = refreshToken
    },

    setPermissions(permissions) {
      this.permissions = permissions
    },

    setRole(role) {
      this.role = role
    },

    setOrganization(organization) {
      this.organization = organization
    },

    login({ user, token, refreshToken = null, role = null, permissions = [], organization = null }) {
      this.user = user
      this.token = token
      this.refreshToken = refreshToken
      this.role = role
      this.isAuthenticated = true
      this.permissions = permissions
      this.organization = organization
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.role = null
      this.isAuthenticated = false
      this.permissions = []
      this.organization = null
    },

    updateUser(userData) {
      this.user = { ...this.user, ...userData }
    },

    addPermission(permission) {
      if (!this.permissions.includes(permission)) {
        this.permissions.push(permission)
      }
    },

    removePermission(permission) {
      this.permissions = this.permissions.filter(p => p !== permission)
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'zenith-auth',
        storage: localStorage,
        paths: ['user', 'token', 'refreshToken', 'isAuthenticated', 'role', 'permissions', 'organization']
      }
    ]
  }
})
