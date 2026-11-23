import { defineStore } from 'pinia'

export const useFileNavigationStore = defineStore('fileNavigation', {
  state: () => ({
    currentPath: []
  }),

  getters: {
    getCurrentPath: (state) => state.currentPath,
    getCurrentPathString: (state) => state.currentPath.map(folder => folder.name).join('/')
  },

  actions: {
    setCurrentPath(path) {
      this.currentPath = path
    },

    addToPath(folder) {
      const lastFolder = this.currentPath[this.currentPath.length - 1]
      if (!lastFolder || lastFolder.id !== folder.id) {
        this.currentPath.push(folder)
      }
    },

    navigateToPath(path) {
      this.currentPath = path
    },

    navigateToRoot() {
      this.currentPath = []
    },

    navigateToFolder(index) {
      this.currentPath = this.currentPath.slice(0, index + 1)
    },

    reset() {
      this.currentPath = []
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'zenith-file-navigation',
        storage: localStorage,
        paths: ['currentPath']
      }
    ]
  }
})
