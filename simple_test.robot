*** Settings ***
Documentation  Demonstrate XUnit outout modifier.


*** Test Cases ***
Simple Skip Test
    [Documentation]  This test case always Skips.
    [Tags]  simple-skip
    Skip  This test case skips.

Simple Fail Test
    [Documentation]  This test case always Fails.
    [Tags]  simple-fail
    Fail  This test case fails.

Simple Pass Test
    [Documentation]  This test case should pass.
    [Tags]  simple-pass
    Log Wrap  This test case passes.
    Set Suite Metadata  my_name  my_value


*** Keywords ***
Log Wrap
    [Documentation]  Just wrapping Log keyword.
    [Arguments]  ${text}
    Log  ${text}
