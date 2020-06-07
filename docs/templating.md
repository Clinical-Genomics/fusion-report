# Available templating variables

The report is generated using a templating engine [Jinja2](http://jinja.pocoo.org/docs/2.10/). Shown below are all
available variables which can be used in the report.

## Variables

* `title`: Title of tha page
* `filename`: Name of the file
* `view`:  View which was used to generate the page
* `modules: Dict[str, Any]`: Dictionary of modules and its variables
* `menu`: List of menu items

Each `Page` has an option to have a custom extra variables. Therefore, you can observe not mentioned variables like i.e: `sample`, `db_path`, `fusion` or `tooL_cutoff`.

## Functions

* `get_id()`: converts title page into a HTML id tag (used in menu to scroll exactly on the section)
* `include_raw()`: load custom CSS or JS. This is necessary as each file has these resources injected into the code base
of the page. This way there is no need for external `assets` folder. The drawback is the final size of the file of course.
