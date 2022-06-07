#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""XUnit Output Modifier.
Simple implementation to form a custom XUnit output from Robot Framework test run.

See RF prerebotmodifier:
https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#toc-entry-498

See JUnit team's xds:
https://github.com/junit-team/junit5/blob/main/platform-tests/src/test/resources/jenkins-junit.xsd

See about RF API, visitor and testsuite:
https://robot-framework.readthedocs.io/en/stable/index.html
https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html?highlight=SuiteVisitor#module-robot.model.visitor
https://robot-framework.readthedocs.io/en/stable/autodoc/robot.model.html#module-robot.model.testsuite

Example usages:

--prerebotmodifier [module_name].[class_name]:[output_filename]:[root node plurar, True|False]

Get `xunit.xml` output file from the modifier:
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml test.robot

Applying <testsuites> root node instead of <testsuite> i.e root node plurar set True:
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml:True test.robot

NOTE: This won't work, because RF's XUnitWriter (specified with -x) overwrites the target file:
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xunit.xml -x xunit.xml test.robot

This works fine:
robot --pythonpath . --prerebotmodifier xom.XUnitOut:xcustom.xml -x xdefault.xml test.robot

Example code modification points are denoted with `# *` comment lines in the code
- Root node <testsuites> attributes.
- Testsuite attribute `hostname`
- Testcase attribute `file` as testcase's source filename.
- Testcase attribute `lineno` as line number of testcase in the source file.
- Function `starttime_to_isoformat` to custom timestamp.
"""

# * import platform  # Used for testsuite hostname attribute.
from robot.api import SuiteVisitor
from robot.utils import XmlWriter


class XUnitOut(SuiteVisitor):
    """Creates modified XUnit output."""

    def __init__(self, name='xunit_mod.xml', p_root=False):
        self._writer = XmlWriter(output=name, usage='xunit')
        # * If you desire <testsuites> as root node, enable this flag. See: Example usages
        self._root_node_plural = p_root

    def start_suite(self, suite):
        """When suite is started writes testsuite/testsuites element's start tag and attributes."""
        attrs = {'name':        suite.name,
                 'tests':       str(suite.statistics.total),
                 # No meaningful data available from suite for `errors`.
                 'errors':      '0',
                 'failures':    str(suite.statistics.failed),
                 'skipped':     str(suite.statistics.skipped),
                 'time':        time_as_seconds(suite.elapsedtime),
                 'timestamp':   starttime_to_isoformat(suite.starttime),
                 # * Define custom suite attributes here:
                 # * 'hostname': platform.node(),
                 }
        if self._root_node_plural and suite.parent is None and suite.suites:
            # * Define custom attributes for <testsuites> element here:
            # See JUnit team's xds:
            # https://github.com/junit-team/junit5/blob/main/platform-tests/src/test/resources/jenkins-junit.xsd
            # * attrs = {}
            self._writer.start('testsuites', attrs)
        else:
            self._writer.start('testsuite', attrs)

    def end_suite(self, suite):
        """When suite is ended, writes properties and end tag for testsuite/testsuites."""
        if suite.metadata or suite.doc:
            self._writer.start('properties')
            if suite.doc:
                self._writer.element('property', attrs={
                                     'name': 'Documentation', 'value': suite.doc})
            for meta_name, meta_value in suite.metadata.items():
                self._writer.element('property', attrs={
                                     'name': meta_name, 'value': meta_value})
            self._writer.end('properties')
        if self._root_node_plural:
            if suite.parent is not None:
                self._writer.end('testsuite')
            elif suite.suites:
                # handling root node and it has sub-suites.
                self._writer.end('testsuites')
            else:
                self._writer.end('testsuite')   # single suite
        else:
            self._writer.end('testsuite')
        if suite.parent is None:
            self._writer.close()

    def visit_test(self, test):
        """Writes testcase element"""
        attrs = {'classname': test.parent.longname,
                 'name': test.name,
                 'time': time_as_seconds(test.elapsedtime),
                 # * Define Custom test attributes here:
                 # * 'file': test.source,
                 # * 'lineno': str(test.lineno),
                 }
        self._writer.start('testcase', attrs)
        if test.failed:
            self._writer.element('failure', attrs={'message': test.message,
                                                   'type': 'AssertionError'})
        if test.skipped:
            self._writer.element('skipped', attrs={'message': test.message,
                                                   'type': 'SkipExecution'})
        self._writer.end('testcase')

def time_as_seconds(millis):
    """Convert milliseconds to seconds"""
    return f'{millis / 1000:.3f}'

def starttime_to_isoformat(stime):
    """RF start time have precision .XYZ seconds, while JUnit have timestamps .XYZabc seconds.
    Adjust padding to comply or modify timestamp format to your favor."""
    if not stime:
        return None
    padding = '000'
    return f'{stime[:4]}-{stime[4:6]}-{stime[6:8]}T{stime[9:]}{padding}'
