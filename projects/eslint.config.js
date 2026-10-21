import eye from "eslint-config-eye"

const extraFiles = [ `**/*.jsx`, `**/*.cjs`, `**/*.cts` ]

export default [
  { ignores:[ `**/dist/**`, `**/build/**` ] },
  ...eye.map( config => ({ ...config, files:[ ...config.files ?? [], ...extraFiles ] }) ),
]
