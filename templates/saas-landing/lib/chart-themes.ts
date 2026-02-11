/**
 * ECharts Theme Configuration
 *
 * 6 professional chart themes for dashboard visualization:
 * - infographic: Bright, colorful for presentations
 * - vintage: Retro, muted colors with cream background
 * - dark: Dark mode with purple/blue theme
 * - roma: Elegant pink/navy/sage palette
 * - shine: Clean, professional blue-dominant
 * - macarons: Pastel, colorful (teal/purple/blue)
 */

export interface ChartTheme {
  id: string
  name: string
  description: string
  colorPalette: string[]
  backgroundColor?: string
  darkMode?: boolean
  category: 'light' | 'dark' | 'colorful' | 'minimal'
  bestFor: string[]
}

export const CHART_THEMES: Record<string, ChartTheme> = {
  infographic: {
    id: 'infographic',
    name: 'Infographic',
    description: 'Bright, colorful theme perfect for presentations and reports',
    colorPalette: [
      '#C1232B', '#27727B', '#FCCE10', '#E87C25', '#B5C334',
      '#FE8463', '#9BCA63', '#FAD860', '#F3A43B', '#60C0DD'
    ],
    category: 'colorful',
    bestFor: ['Presentations', 'Reports', 'Marketing dashboards']
  },

  vintage: {
    id: 'vintage',
    name: 'Vintage',
    description: 'Retro, muted colors with a warm cream background',
    colorPalette: [
      '#d87c7c', '#919e8b', '#d7ab82', '#6e7074', '#61a0a8',
      '#efa18d', '#787464', '#cc7e63', '#724e58', '#4b565b'
    ],
    backgroundColor: '#fef8ef',
    category: 'light',
    bestFor: ['Historical data', 'Classic reports', 'Print-friendly']
  },

  dark: {
    id: 'dark',
    name: 'Dark',
    description: 'Modern dark mode with vibrant accent colors',
    colorPalette: [
      '#4992ff', '#7cffb2', '#fddd60', '#ff6e76', '#58d9f9',
      '#05c091', '#ff8a45', '#8d48e3', '#dd79ff'
    ],
    backgroundColor: '#100C2A',
    darkMode: true,
    category: 'dark',
    bestFor: ['Modern dashboards', 'Night mode', 'Technical interfaces']
  },

  roma: {
    id: 'roma',
    name: 'Roma',
    description: 'Elegant theme with sophisticated pink, navy, and sage tones',
    colorPalette: [
      '#E01F54', '#001852', '#f5e8c8', '#b8d2c7', '#c6b38e',
      '#a4d8c2', '#f3d999', '#d3758f', '#dcc392', '#2e4783'
    ],
    category: 'colorful',
    bestFor: ['Executive dashboards', 'Elegant presentations', 'Brand-focused']
  },

  shine: {
    id: 'shine',
    name: 'Shine',
    description: 'Clean, professional theme with blue dominance',
    colorPalette: [
      '#c12e34', '#e6b600', '#0098d9', '#2b821d', '#005eaa',
      '#339ca8', '#cda819', '#32a487'
    ],
    category: 'light',
    bestFor: ['Business dashboards', 'Financial reports', 'Clean interfaces']
  },

  macarons: {
    id: 'macarons',
    name: 'Macarons',
    description: 'Playful pastel colors for approachable, friendly dashboards',
    colorPalette: [
      '#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80',
      '#8d98b3', '#e5cf0d', '#97b552', '#95706d', '#dc69aa'
    ],
    category: 'colorful',
    bestFor: ['User-friendly dashboards', 'SaaS platforms', 'Engaging reports']
  }
}

export const getThemeByCategory = (category: ChartTheme['category']): ChartTheme[] => {
  return Object.values(CHART_THEMES).filter(theme => theme.category === category)
}

export const getDefaultTheme = (): ChartTheme => CHART_THEMES.shine

export const loadEChartsTheme = async (themeId: string): Promise<void> => {
  if (typeof window === 'undefined') return

  // Load theme script dynamically
  const script = document.createElement('script')
  script.src = `/themes/echarts/${themeId}.js`
  script.async = true

  return new Promise((resolve, reject) => {
    script.onload = () => resolve()
    script.onerror = () => reject(new Error(`Failed to load theme: ${themeId}`))
    document.head.appendChild(script)
  })
}
