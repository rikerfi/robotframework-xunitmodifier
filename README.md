# Robot Framework's XUnit Output Modifier (xom)
Simple implementation for Robot Framework XUnit output modifier. The modifier implementation produces identical XUnit output file as Robot Framework's XUnit output does, but the modifier `xom.py` is much easier to custom various needs of XUnit output. Several requests discussed on Robot Framework community are pinpointed to the code allowing fast forward implementation like:

- Plural root node `<testsuites>` when multiple testsuites in a test run.
- Separate root node attributes for `<testsuites>` element.
- Testsuite attribute `hostname`.
- XUnit timestamp to UTC time.
- Local time UTC offset to testsuite's property element.
- Testcase attributes `file` and `lineno` pointing to the test source file and line number.
- Timestamp modification.

This work is derived from Robot Framework's XUnitFileWriter:
https://github.com/robotframework/robotframework/blob/master/src/robot/reporting/xunitwriter.py

## Simple Installation
Clone this repository or just download the `xom.py` file.
Place the `xom.py` file to your `PYTHONPATH` or use `--pythonpath` specifier for Robot Framework test run. See examples below. Examples assume `xom.py` is located to very same folder than `.robot` files.

## Example Usage
Naturally using `xom` requires [Robot Framework installed](https://github.com/robotframework/robotframework#installation). 

--prerebotmodifier [module_name].[class_name]:[output_filename]

Get `xunit.xml` output file from the modifier:
```shell session
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml test.robot
```

**NOTE**: Do not use same filename for the modifier and Robot Framework's XUnit output. That won't work, because Robot Framework's XUnitWriter (specified with -x) overwrites the target file:
```shell session
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml -x xunit.xml test.robot
```
This works fine:
```shell session
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xcustom.xml -x xdefault.xml test.robot
```

## Possible Modifications
Example code modification points are denoted with `# *` comment lines in the code.

### Configuration Flags
Configuration flags are set to `False` by default.

- Root node is generated to `<testsuites>` when multiple suites in a test run.
    ```python
    ROOT_NODE_PLURAL = True
    ```
- Robot Framework uses local time for test suite's timestamp. Use this flag to set timestamp from local system time to UTC time.
    ```python
    XUNIT_UTC_TIME_IN_USE = True
    ```
- Report local time offset to UTC time in seconds to Suite's property element. Offset is negative to east from GMT and positive to west from GMT.
    ```python
    REPORT_UTC_TIME_OFFSET = True
    ```

### Root Node
Root node could have plural form `<testsuites>`. You may modify `<testsuites>` root element's attributes:
```python
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
```python
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
```python
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

## Full-Blown Example Output
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test &amp; Test2" tests="4" errors="0" failures="1" skipped="1" time="0.037" timestamp="2022-06-09T17:57:05000" hostname="osstest-desktop-1">
    <testsuite name="Test" tests="3" errors="0" failures="1" skipped="1" time="0.013" timestamp="2022-06-09T17:57:05000" hostname="osstest-desktop-1">
        <testcase classname="Test &amp; Test2.Test" name="Metadata Test" time="0.003" file="/home/osstest/demo/test.robot" lineno="2">
        </testcase>
        <testcase classname="Test &amp; Test2.Test" name="Test Failing" time="0.004" file="/home/osstest/demo/test.robot" lineno="8">
            <failure message="This is failing case." type="AssertionError"/>
        </testcase>
        <testcase classname="Test &amp; Test2.Test" name="Test Skip" time="0.002" file="/home/osstest/demo/test.robot" lineno="12">
            <skipped message="This is skipped case." type="SkipExecution"/>
        </testcase>
        <properties>
            <property name="Documentation" value="Test suite to demonstrate XUnit modification features."/>
            <property name="metaname" value="metavalue"/>
            <property name="metaname2" value="metavalue2"/>
            <property name="utc-offset" value="-10800"/>
        </properties>
    </testsuite>
    <testsuite name="Test2" tests="1" errors="0" failures="0" skipped="0" time="0.004" timestamp="2022-06-09T17:57:05000" hostname="osstest-desktop-1">
        <testcase classname="Test &amp; Test2.Test2" name="Just One Thing To Test" time="0.002" file="/home/osstest/demo/test2.robot" lineno="2">
        </testcase>
        <properties>
            <property name="utc-offset" value="-10800"/>
        </properties>
    </testsuite>
    <properties>
        <property name="utc-offset" value="-10800"/>
    </properties>
</testsuites>
```

## References
[Robot Framework's prerebotmodifier](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#toc-entry-498)

[JUnit team's xds](https://github.com/junit-team/junit5/blob/main/platform-tests/src/test/resources/jenkins-junit.xsd)

[Robot Framework API](https://robot-framework.readthedocs.io/en/stable/index.html)

[Robot Framework's Visitor Model](https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html?highlight=SuiteVisitor#module-robot.model.visitor)

[Robot Framework's Testsuite Model](https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html#module-robot.model.testsuite)
