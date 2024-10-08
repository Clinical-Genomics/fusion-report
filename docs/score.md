# Scoring fusion

One disadvantage of the tools is that they tend to report false positive results. Not all fusion tools provide
estimated score for a fusion. The only way how to correctly verify a fusion is biologically (RT-qPCR …).

**fusion-report** uses weighted approach of assigning weights to tools and databases. By default, each tool
is assigned the same weight. This is because each tool uses different approach of discovering fusions and
report different results, for example FusionCatcher will work best on somatic samples.

You can customize weight of individual tool by specific parameter `<tool-name>_weight 30`.
The sum of the weights has to be 100!

Weights for databases are as follows:

* COSMIC (50)
* MITELMAN (50)
* FusionGDB2 (0)

> It is strongly suggested to use all supported databases in order to get the best estimated score.
>

## Formula

The final formula for calculating score is:

$$
score = 0.8 * \sum_{tool}^{tools provided} f(fusion, tool) + 0.2 * \sum_{db}^{dbs provided} g(fusion, db)*w(db)
$$

Weights for databases are as follows:

* COSMIC (50)
* MITELMAN (50)
* FusionGDB2 (0)