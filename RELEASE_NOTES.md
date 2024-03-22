# v0.8.0
- **[FEATURE]** Added LogBase as an easier way to use logger

# v0.7.1

- **[FEATURE]** Added statid default log level

# v0.7.0

- **[FEATURE]** Added log level functionality
- **[FEATURE]** Added static default log levels
- **[FEATURE]** Added static color definitions for log levels
- **[FEATURE]** Added unit tests for new functionality

# v0.6.1

- **[BUMP]** setuptools : 65.5.0 -> 69.1.1
- **[BUMP]** black : 23.9 -> 24.2
- **[BUMP]** mypy : 1.7 -> 1.8
- **[BUMP]** flake8 : 6.1 -> 7.0
- **[BUMP]** pytest : 7.4 -> 8.0
- **[ADD]** pytest-cov 4.1
- **[REMOVE]** coverage 7.3
- **[CHANGE]** pytest-cov instead of coverage

# v0.6.0

- **[FEATURE]** Added move() functionality [see: Function move()](README.md#function_move)
- **[BUG_FIX]** Fixed a bug where release does not actually releases the resources
- **[CI_FIX]** Added missing pytest which was removed with the coverage
- **[BUMP]** Bumped mypy to v1.7

# v0.5.0

- **[FEATURE]** Added PEP-561 compliance (py.typed)

# v0.4.0

- **[BUGFIX]** Fixed publish with the lowest supported python version

# v0.3.0 [NOT PUBLISHED]

- **[FEATURE]** Added Python 3.10 support
- **[FEATURE]** Added Python 3.12 support
- **[DOC]** Added Release Notes
- **[DOC]** Updated README
- **[FEATURE]** Fixed **init**.py so the module can now be used as  
  `from uglylogger import Logger`  
  instead of  
  `from uglylogger.logger import Logger`

# v0.2.0

- **[FEATURE]** introduced logger.console_oneline() method which enables user to print to a single console row (Useful for progress output)

# v0.1.1

- **[FEATURE]** logger.log() method now accepts _LogOutput_ as an argument

# v0.1.0

- **[INITIAL]** Initial Release
