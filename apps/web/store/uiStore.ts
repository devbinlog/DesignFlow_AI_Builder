import { create } from 'zustand'

interface UiStore {
  isSidebarCollapsed: boolean
  toggleSidebar: () => void
}

export const useUiStore = create<UiStore>((set) => ({
  isSidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
}))
