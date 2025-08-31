import { createContext, useContext, useEffect, useMemo, useState } from 'react'

type ThemeMode = 'light' | 'dark' | 'system'

interface ThemeContextValue {
  mode: ThemeMode
  resolved: 'light' | 'dark'
  toggle: () => void
  setMode: (mode: ThemeMode) => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

function getSystemPrefersDark() {
  if (typeof window === 'undefined') return false
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

function resolveMode(mode: ThemeMode): 'light' | 'dark' {
  if (mode === 'system') return getSystemPrefersDark() ? 'dark' : 'light'
  return mode
}

export function ThemeProvider(props: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('theme-mode') : null
    return (saved as ThemeMode) || 'system'
  })

  const resolved = resolveMode(mode)

  useEffect(() => {
    if (typeof document !== 'undefined') {
      const root = document.documentElement
      root.dataset.theme = resolved
      // Also toggle Tailwind dark class for compatibility
      root.classList.toggle('dark', resolved === 'dark')
    }
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('theme-mode', mode)
    }
  }, [mode, resolved])

  useEffect(() => {
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      if (mode === 'system') {
        document.documentElement.dataset.theme = resolveMode('system')
      }
    }
    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [mode])

  const value = useMemo<ThemeContextValue>(
    () => ({
      mode,
      resolved,
      toggle: () => setMode((prev) => (resolveMode(prev) === 'dark' ? 'light' : 'dark')),
      setMode,
    }),
    [mode, resolved]
  )

  return <ThemeContext.Provider value={value}>{props.children}</ThemeContext.Provider>
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return ctx
}


