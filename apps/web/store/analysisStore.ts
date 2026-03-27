import { create } from 'zustand'

type AnalysisTab = 'tokens' | 'components' | 'code'

interface AnalysisStore {
  selectedNodeId: string | null
  activeTab: AnalysisTab
  selectedFile: string | null
  isPanelOpen: boolean

  setSelectedNodeId: (id: string | null) => void
  setActiveTab: (tab: AnalysisTab) => void
  setSelectedFile: (path: string | null) => void
  togglePanel: () => void
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  selectedNodeId: null,
  activeTab: 'tokens',
  selectedFile: null,
  isPanelOpen: true,

  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedFile: (path) => set({ selectedFile: path }),
  togglePanel: () => set((state) => ({ isPanelOpen: !state.isPanelOpen })),
}))
