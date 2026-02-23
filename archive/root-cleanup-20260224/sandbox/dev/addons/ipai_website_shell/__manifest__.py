{
  "name": "IPAI Website Shell",
  "version": "18.0.1.0.0",
  "category": "Website",
  "summary": "Minimal website shell: keep header, reduce footer, remove default blocks",
  "depends": ["website", "website_sale"],  # drop website_sale if you don't need Shop
  "data": [
    "views/layout.xml",
  ],
  "assets": {
    "web.assets_frontend": [
      "ipai_website_shell/static/src/scss/site_shell.scss",
    ],
  },
  "installable": True,
  "application": False,
  "license": "LGPL-3",
}
