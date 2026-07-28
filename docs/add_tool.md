# Add new fusion detection tool

> NB: Please follow all the steps before submitting a PR. Make sure to submit also the test results.

1. Implement a new tool in `fusion_report/parsers/{tool_name.py}`.

```python
# Replace Test with the name of the new tool
"""Test module"""
from typing import Any, Dict, List, Tuple
from fusion_report.parsers.abstract_fusion import AbstractFusionTool

class Test(AbstractFusionTool):
    """Test tool parser."""

    def parse(self, line, delimiter='\t') -> Tuple[str, Dict[str, Any]]:
        col: List[str] = line.strip().split(delimiter) # replace delimiter if different
        fusion: str = f'{col[0]}'
        details: Dict[str, Any] = {
            'position': f'{col[2]}#{col[3]}'.replace('chr', ''),
            'FII': int(col[1]),
        }

        return fusion, details
```

2. Run your application on these samples: [test1] and [test2].
3. Store the results in `tests/test_data/`
4. Submit a pull request on GitHub.
5. Give yourself a high five for awesome job! :+1:

[test1]: https://github.com/ndaniel/fusioncatcher/blob/master/test/reads_1.fq.gz
[test2]: https://github.com/ndaniel/fusioncatcher/blob/master/test/reads_2.fq.gz
