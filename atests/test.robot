*** Settings ***
Library             SeleniumLibrary
Library             AxeLibrary

Suite Teardown      Close Browser


*** Variables ***
&{axe_config}=      reporter=v2


*** Test Cases ***
Run One Accessibility Test
    Open Browser    https://www.gofore.com    firefox
    &{results}=    Run Accessibility Tests
    ...    results/axe-results.json
    ...    axe_js_path=..${/}node_modules${/}axe-core${/}axe.js
    ...    options=${axe_config}
    Log To Console    ${results}
    Accessibility Issues Log
