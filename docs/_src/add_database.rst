Add new database
================

1. Convert the database into `sqlite3`
2. Write documentation on how to download and create the database
3. Copy the `*.db` file into folder where all local databases are stored
4. The name of the database has to be **lower cased**
5. .. code-block:: python

    db = Db()
    new_db = db.connect('<newnew_db>')
    res = new_db.select('SELECT ...')
