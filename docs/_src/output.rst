Output
======

The tool generates multiple files for different purposes:

* ``fusions.json``

  * List of all fusions together with database name it was found in, fusion tool output and score.
  * This file should be used for further processing by researcher or developer
  * See example `here <https://matq007.github.io/fusion-report/example/fusions.json>`_.
* ``fusions_list.txt``

  * List of all unique fusions which serve as an input for tool FusionInspector 
  * See example `here <https://matq007.github.io/fusion-report/example/fusions_list.txt>`_.
* ``fusions_list_filtered.txt``

  * Filtered list of unique fusions where fusion was found by at least specified cutoff for FusionInspector 
  * See example `here <https://matq007.github.io/fusion-report/example/fusions_list_filtered.txt>`_.
* ``fusions_mqc.json``

  * This file generates a fusion section for `MultiQC <http://multiqc.info>_` 
  * See example `here <https://matq007.github.io/fusion-report/example/fusions_mqc.json>`_.