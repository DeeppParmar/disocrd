import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        blurple: '#5865F2',
        discord_dark: '#2B2D31',
        discord_darker: '#1E1F22',
        sidebar: '#2B2D31'
      }
    },
  },
  plugins: [],
}
export default config
