import nextra from 'nextra'

const withNextra = nextra({
  defaultShowCopyCode: true,
  search: true,
})

export default withNextra({
  output: 'standalone',
})
