-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
require("legendary").setup({
  extensions = {
    lazy_nvim = true,
  },
})
