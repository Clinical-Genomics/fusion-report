# Add new fusion database

1. Implement a new database in `fusion_report/data/{database}.py`. You have to include a method `get_all_fusions()`
which should return list of all gene fusion in your database in format `GENEA--GENEB`.

```python
"""Test Database"""
import re
from typing import List

from fusion_report.common.db import Db
from fusion_report.common.singleton import Singleton


class Test(Db, metaclass=Singleton):
    """Implementation of Test Database. All core functionality is handled by parent class."""

    def __init__(self, path: str) -> None:
        super().__init__(path, 'Test', 'Test.sql')

    def get_all_fusions(self) -> List[str]:
        """Returns all fusions from database."""
        query: str = '''SELECT DISTINCT XYZ FROM XYZ'''
        res = self.select(query)

        return res['fusions']
```

2. Create database schema in `fusion_report/schema/{database.sql}`. This is a SQL script which defines a structure 
of your database.
3. Update `__enrich()` function in `fusion_report/app.py`

```python
local_fusions: Dict[str, List[str]] = {
    FusionGDB(path).name: FusionGDB(path).get_all_fusions(),
    MitelmanDB(path).name: MitelmanDB(path).get_all_fusions(),
    CosmicDB(path).name: CosmicDB(path).get_all_fusions(),
    TestDB(path).name: TestDB(path).get_all_fusions() # add your database here
}
```

4. Finally, to make sure everyone can use the database, you have to implement steps of how to download your database.
To do this head over to `fusion_report/download.py`.

    4.1. Create fusion `__get_test()`
    ```python
    # file, url = ...

    # You finish the function by calling TestDB() object and running setup function.
    db = TestDB('.')
    # This is a in-house function which will:
    # 1. Create database using your schema
    # 2. Use provided files as data files which will be imported to the database
    db.setup(files, delimiter='\t', skip_header=True)
    ```
    4.2. Add your function into  `__download_all()`
    ```python
    processes = [
       Process(target=self.get_fusiongdb),
       Process(target=self.get_mitelman),
       Process(target=self.get_cosmic),
       Process(target=self.get_test)
    ]
    ```

5. Give yourself a high five for awesome job! :+1:
