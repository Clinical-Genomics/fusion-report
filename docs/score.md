# Scoring fusion with the fusion indication index

One disadvantage of the tools is that they tend to report false positive results. Not all fusion tools provide
estimated score for a fusion. The only way how to correctly verify a fusion is biologically (RT-qPCR …).

**fusion-report** uses a weighted approach of assigning weights to tools and databases. By default, each tool
is assigned the same weight. This is because each tool uses different approach of discovering fusions and
report different results.

You can customize weight of individual tool by specific parameter `<tool-name>_weight 30`.
The sum of the weights has to be 100!

> It is strongly suggested to use all supported databases in order to get the best estimated Fusion Indication Index.
>

## Formula

The final formula for calculating the Fusion Indication Index is:

$$
Fusion Indication Index = 0.5 * \sum_{tool}^{tools provided} f(fusion, tool) + 0.5 * \sum_{db}^{dbs provided} g(fusion, db)*w(db)
$$

`Tools provided` is the sum of the tools that are passed as CLI arguments. `DBs provided` are the sum of the DBs that are considered.

Weights for databases are as follows:

* COSMIC (50)
* MITELMAN (50)
* FusionGDB2 (0)
