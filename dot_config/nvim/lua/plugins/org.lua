return {
  "nvim-orgmode/orgmode",
  event = "VeryLazy",
  ft = { "org" },
  config = function()
    -- Setup orgmode
    require("orgmode").setup({
      org_agenda_files = "~/orgfiles/**/*",
      org_default_notes_file = "~/orgfiles/refile.org",
      org_todo_keywords = { "TODO(t)", "ACTIVE(a)", "WAITING(w)", "|", "DONE(d)" },
      org_todo_keyword_faces = {
        WAITING = ":foreground blue :weight bold",
        ACTIVE = ":foreground green :weight bold",
      },
      org_capture_templates = {
        r = {
          description = "Repo",
          template = "* [[%x][%(return string.match('%x', '([^/]+)$'))]]%?",
          target = "~/org/repos.org",
        },
      },
    })

    -- NOTE: If you are using nvim-treesitter with ~ensure_installed = "all"~ option
    -- add ~org~ to ignore_install
    -- require('nvim-treesitter.configs').setup({
    --   ensure_installed = 'all',
    --   ignore_install = { 'org' },
    -- })
  end,
}
