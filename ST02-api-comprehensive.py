"""
Create a new Python project in VS Code that uses the third-party requests
library to consume data from the provided web API.

Allow a user to enter range of zip codes they are interested in (from and to).
Make API calls to capture the data and extract all pieces of information from
the returned JSON payload. Place all data in a 2D List. Generate a report with
the data properly formatted. Check the HTTP status code in case a value in the
range is invalid.

After completing the program, initialize Git source control, create a GitHub
repository with the same name as your project folder, commit your files, and
push the project to GitHub.
"""

import requests
