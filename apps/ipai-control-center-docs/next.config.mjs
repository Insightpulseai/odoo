import nextra from 'nextra'

const withNextra = nextra({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.jsx',
  mdxOptions: {
    remarkPlugins: [],
    rehypePlugins: []
  }
})

export default withNextra({
  reactStrictMode: true,
  output: 'standalone'
})
