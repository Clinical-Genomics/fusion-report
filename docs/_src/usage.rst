Usage
=====

Before running the tool make sure you have downloaded all the databases you want to use.

Run all fusion detection tools
------------------------------

.. code-block:: bash

    fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ 
        --ericscript tests/test_data/ericscript.tsv 
        --starfusion tests/test_data/starfusion.tsv 
        --fusioncatcher tests/test_data/fusioncatcher.txt
        --squid tests/test_data/squid.txt 
        --pizzly tests/test_data/pizzly.tsv

Set a custom weight for tool
----------------------------

The total sum of all triggered tools has to be 100. By default the weights are
equal `100 / (number of tools)`.

.. code-block:: bash

    fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ 
        --ericscript tests/test_data/ericscript.tsv 
        --ericscript_weight 30.5
        --fusioncatcher tests/test_data/fusioncatcher.txt
        --fusioncatcher_weight 70.5

Specify tool cutoff
-------------------

You can specify how many tools have to detect the fusion. By default
at least ``2`` tools are required. This can be changed by appending
``-t`` parameter to ``fusion_report run`` command. If you want to
disable filter set ``-t`` to ``0``.
 
.. code-block:: bash

    fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ 
        --ericscript tests/test_data/ericscript.tsv 
        --starfusion tests/test_data/starfusion.tsv 
        --fusioncatcher tests/test_data/fusioncatcher.txt
        --squid tests/test_data/squid.txt 
        --pizzly tests/test_data/pizzly.tsv
        -t 3

All parameters and options
--------------------------

.. code-block:: bash

    fusion_report --help
    fusion_report run --help
    fusion_report download --help