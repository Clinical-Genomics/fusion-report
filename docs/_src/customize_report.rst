Customize report
================

The final summary report is using Jinja2 as templating engine. Visual customization can be
done by providing a configuration file in YAML format as shown below:

.. literalinclude:: ../../example_config.yml

To use the `example_config <https://github.com/matq007/fusion-report/blob/master/example_config.yml>`_ 
use ``-c`` parameter like so:

``fusion_report run -c example_config.yml ...``
