# Customize report

The final summary report is using Jinja2 as templating engine. Visual customization can be done by
providing a configuration file in YAML format as shown below:

```yaml
report_title: 'Some really cool title'
institution:
  name: 'SciLifeLab'
  img: 'assets/img/scilifelab.jpg'
  url: 'https://www.scilifelab.se'
date_format: '%Y-%m-%d'
assets:
  css: 'custom.css'
  js: 'custom.js'
```
