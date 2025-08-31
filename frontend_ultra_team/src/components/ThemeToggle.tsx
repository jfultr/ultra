import { Switch } from '@headlessui/react'
import { MoonIcon, SunIcon } from '@heroicons/react/24/outline'
import { useTheme } from '../theme/ThemeProvider'

export function ThemeToggle() {
  const { resolved, toggle } = useTheme()
  const isDark = resolved === 'dark'

  return (
    <Switch
      checked={isDark}
      onChange={toggle}
      className={`relative inline-flex h-7 w-14 items-center rounded-full border transition-colors
        ${isDark ? 'bg-gray-800 border-white/10' : 'bg-slate-200 border-gray-200'}`}
    >
      <span className={`absolute left-1 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full grid place-items-center text-white transition-transform
        ${isDark ? 'translate-x-6 bg-blue-600' : 'translate-x-0 bg-blue-600'}`}>
        {isDark ? <MoonIcon className="h-4 w-4" /> : <SunIcon className="h-4 w-4" />}
      </span>
      <span className="sr-only">Toggle theme</span>
    </Switch>
  )
}


