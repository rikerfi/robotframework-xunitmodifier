# Robot Framework's XUnit Modifier
Simple implementation for Robot Framework XUnit output modifier.

This work is derived from Robot Framework's XUnitFileWriter:
https://github.com/robotframework/robotframework/blob/master/src/robot/reporting/xunitwriter.py

## Simple Installation
Clone this repository or just download the `xom.py` file.
Place the `xom.py` file to your `PYTHONPATH` or use `--pythonpath` specifier for Robot Framework test run. See examples below. Examples assume `xom.py` is located to very same folder than `.robot` files.

## Example Usage

--prerebotmodifier [module_name].[class_name]:[output_filename]

Get `xunit.xml` output file from the modifier:
```
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml test.robot
```

**NOTE**: Do not use same filename for the modifier and Robot Framework's XUnit output. That won't work, because Robot Framework's XUnitWriter (specified with -x) overwrites the target file:
```
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml -x xunit.xml test.robot
```
This works fine:
```
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xcustom.xml -x xdefault.xml test.robot
```

## Possible Modifications
Example code modification points are denoted with `# *` comment lines in the code.

### Configuration Flags
Configuration flags are set to `False` by default.

- Root node is generated to `<testsuites>` when multiple suites in a test run.
    ```
    ROOT_NODE_PLURAL = True
    ```
- Robot Framework uses local time for test suite's timestamp. Use this flag to set timestamp from local system time to UTC time.
    ```
    XUNIT_UTC_TIME_IN_USE = True
    ```
- Report local time offset to UTC time in seconds to Suite's property element. Offset is negative to east from GMT and positive to west from GMT.
    ```
    REPORT_UTC_TIME_OFFSET = True
    ```

### Root Node
Root node could have plural form `<testsuites>`. You may modify `<testsuites>` root element's attributes:
```
    if ROOT_NODE_PLURAL and suite.parent is None and suite.suites:
        attrs = {
            'name': suite.name,
            'time': time_as_seconds(suite.elapsedtime),
            'tests': str(suite.statistics.total),
            'failures': str(suite.statistics.failed),
            'disabled': str(suite.statistics.skipped), # If you feel that skipped tests maps to disabled.
            'errors': '0'
        }
        self._writer.start('testsuites', attrs)
```
See also [JUnit team's xsd reference.](https://github.com/junit-team/junit5/blob/main/platform-tests/src/test/resources/jenkins-junit.xsd)

### Testsuite Attribute `hostname`
To get `hostname` within testsuite element you may use following reference implementation:
```
import platform

def start_suite(self, suite):
    attrs = {'name':       suite.name,
            'tests':       str(suite.statistics.total),
            # No meaningful data available from suite for `errors`.
            'errors':      '0',
            'failures':    str(suite.statistics.failed),
            'skipped':     str(suite.statistics.skipped),
            'time':        time_as_seconds(suite.elapsedtime),
            'timestamp':   self._starttime_to_isoformat(suite.starttime),
            'hostname':    platform.node(),
            }
    self._writer.start('testsuite', attrs)
```

### Testcase Attribute `file` And `lineno`
Testcase attributes `file` as testcase's source filename and `lineno` as line number of testcase in the source file.
```
def visit_test(self, test):
    attrs = {'classname': test.parent.longname,
                'name': test.name,
                'time': time_as_seconds(test.elapsedtime),
                'file': test.source,
                'lineno': str(test.lineno),
                }
    self._writer.start('testcase', attrs)
```

### Method `_starttime_to_isoformat` to custom timestamp.
Alternate XUnit output's timestamps to your favor.

## References
Robot Framework's prerebotmodifier:
https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#toc-entry-498

JUnit team's xds:
https://github.com/junit-team/junit5/blob/main/platform-tests/src/test/resources/jenkins-junit.xsd

Robot Framework API, visitor and testsuite:
https://robot-framework.readthedocs.io/en/stable/index.html
https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html?highlight=SuiteVisitor#module-robot.model.visitor
https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html#module-robot.model.testsuite
