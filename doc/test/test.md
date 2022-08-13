# Testing 

Test release: [Release v1.0.0](https://github.com/ibuttimer/analastock/releases/tag/v1.0.0)

## Environment
If using a [Virtual Environment](../../README.md#virtual-environment), ensure it is activated. Please see [Activating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

The site was tested using the following methods:

## Unittest Unit Testing
Unit testing of scripts was undertaken using [unittest](https://docs.python.org/3/library/unittest.html#module-unittest).
The test scripts are located in the [tests](../../tests/) folder.

**Note 1:** [Environment](#environment)

**Note 2:** The rate of execution of Google Sheets related tests is limited in order to avoid test failure due to exceeding the Google Sheets API, `Read requests per minute per user` and/or `Write requests per minute per user` [quotas](https://developers.google.com/sheets/api/limits)

The tests may be run from the project root folder:
```shell
Run all tests
> python -m unittest

Run an individual test, e.g.
> python -m unittest tests\utils_tests\test_input.py
```
Alternatively, if using:
* Visual Studio Code
 
    The [Test Explorer UI](https://marketplace.visualstudio.com/items?itemName=hbenl.vscode-test-explorer) or Visual Studio Code's native testing UI<sup>*</sup>, allows tests to be run from the sidebar of Visual Studio Code.
* IntelliJ IDEA

  The allows tests to be run from the Project Explorer of IntelliJ IDEA.

<sup>*</sup> Set `testExplorer.useNativeTesting` to `true` in the Visual Studio Code settings.

## PEP8 Testing
[PEP8](https://peps.python.org/pep-0008/) compliance testing was performed using [pycodestyle](https://pypi.org/project/pycodestyle/)

**Note:** [Environment](#environment)

The tests may be run from the project root folder:
```shell
Run all tests
> pycodestyle .

Run an individual test, e.g.
> pycodestyle sheets\load_data.py 
```

The basic pycodestyle configuration is contained in [setup.cfg](../../setup.cfg). See [Configuration](https://pycodestyle.pycqa.org/en/latest/intro.html#configuration) for additional configuration options.

> **Note:** PEP8 testing is also performed as part of the unit test suite, see [test_style.py](../../tests/test_style.py).
> When running unit tests from the terminal, it may be disabled by setting the `SKIP_PEP8` environment variable to `y` or `n`.

```shell
For Linux and Mac:                            For Windows:
$ export SKIP_PEP8=y                          > set SKIP_PEP8=y
```

## Manual 
The site was manually tested in the following browsers:

|     | Browser                                   | OS                          | 
|-----|-------------------------------------------|-----------------------------|
| 1   | Google Chrome, Version 104.0.5112.81      | Windows 11 Pro Version 21H2 |
| 2   | Mozilla Firefox, Version 103.0.2 (64-bit) | Windows 11 Pro Version 21H2 |
| 3   | Opera, Version:89.0.4447.91               | Windows 11 Pro Version 21H2 |

Testing undertaken:

| Feature                                             | Expected                                                  | Action                                                                                                                                        | Related                                                                            | Result                                              | 
|-----------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------|
| Number of stock to analyse                          | Able to enter number of stocks                            | Enter number of stocks                                                                                                                        | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Stock symbol to analyse                             | Able to enter stock symbol                                | Enter stock symbol                                                                                                                            | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Search for stock to via company name search         | Able to search for stock                                  | Perform name search                                                                                                                           | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period by date                     | Able to enter analysis period by date                     | Enter analysis period as `date from/to date` in `dd-mm-yyyy`, `dd-mm-yy`, `dd-MMM-yyyy` and `dd-MMM-yy` formats                               | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period by text                     | Able to enter analysis period by text                     | Enter analysis period as `period from/to date` in `1d to dd-mm-yyyy`, `1w from dd-mm-yy`, `1m to dd-MMM-yyyy` and `1y from dd-MMM-yy` formats | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period as year-to-date             | Able to enter analysis period as year-to-date             | Enter analysis period as `ytd date` in `dd-mm-yyyy`, `dd-mm-yy`, `dd-MMM-yyyy` and `dd-MMM-yy` formats                                        | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period by abbreviated date         | Able to enter analysis period by abbreviated date         | Enter analysis period as `date from/to date` in `mm-yyyy`, `mm-yy`, `MMM-yyyy` and `MMM-yy` formats                                           | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period by abbreviated text         | Able to enter analysis period by abbreviated text         | Enter analysis period as `period from/to date` in `1d to mm-yyyy`, `1w from mm-yy`, `1m to MMM-yyyy` and `1y from MMM-yy` formats             | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period as abbreviated year-to-date | Able to enter analysis period as abbreviated year-to-date | Enter analysis period as `ytd date` in `mm-yyyy`, `mm-yy`, `MMM-yyyy` and `MMM-yy` formats                                                    | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Specify analysis period by date (ambiguous)         | Able to select date for analysis period                   | Enter date for analysis period in an ambiguous form e.g. `1 2` could represent 1st Feb current year or 1st Jan 2002                           | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Stock analysis (single) is displayed                | Able to view stock analysis                               | Enter stock symbol and analysis period                                                                                                        | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Stock analysis (multiple) is displayed              | Able to view stock analysis                               | Enter multiple stock symbols and analysis period                                                                                              | Stock Analysis option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Perform company search                              | Able to perform company search                            | Enter company name or part of company, and matching results are shown                                                                         | Company Search option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Perform analysis from company search                | Able to perform analysis from company search              | Enter company name or part of company, select option from matching results and enter analysis parameters                                      | Company Search option                                                              | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Update company information                          | Able to update company information                        | Select Update Company Information from main menu, and enter required parameters                                                               | Update Company Information option                                                  | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Delete stock data                                   | Able to delete stock data                                 | Select Delete Stock Data option                                                                                                               | Delete Stock Data                                                                  | ![pass](https://badgen.net/badge/checks/Pass/green) |
| View Help                                           | Help is displayed                                         | Select Help option from main menu                                                                                                             | Help option                                                                        | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Exit program                                        | Program is terminated                                     | Select Quit option from main menu                                                                                                             | Quit option                                                                        | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Data download                                       | Graceful recovery from network interruptions              | Select Update Company Information from main menu, and enter required parameters                                                               | Stock Analysis/Company Search/Update Company Information/Delete Stock Data options | ![pass](https://badgen.net/badge/checks/Pass/green) |


## Responsiveness Testing

As the terminal window size is fixed, this makes the site is unsuitable for responsiveness testing.

## Lighthouse

Lighthouse testing was not performed, as due to the nature of the application, it is unsuitable for testing.

## Accessibility
As the main content of the site is in the terminal window, this makes the site is unsuitable for accessibility testing.

## User

User testing identified the following [issues](https://github.com/ibuttimer/analastock/labels/user).

| Issue                                 | Description                                      |
|---------------------------------------|--------------------------------------------------|
| More complete example of period entry | https://github.com/ibuttimer/analastock/issues/6 |
| Add full time periods; 'month' etc.   | https://github.com/ibuttimer/analastock/issues/7 |
| Duplicate symbol analysis             | https://github.com/ibuttimer/analastock/issues/8 |

## Validator Testing 

The [W3C Nu Html Checker](https://validator.w3.org/nu/) was utilised to check the HTML validity, while the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) was utilised to check the CSS validity with respect to [CSS level 3 + SVG](https://www.w3.org/Style/CSS/current-work.html.)

| Page    | HTML                                                                                        | HTML Result                                         | CSS                                                                                                                                                                             | CSS Result                                          |
|---------|---------------------------------------------------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Landing | [W3C validator](https://validator.w3.org/nu/?doc=https%3A%2F%2Fanalastock.herokuapp.com%2F) | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fanalastock.herokuapp.com%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | ![pass](https://badgen.net/badge/checks/Pass/green) |


## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/analastock/issues).

#### Bug

[Bug list](https://github.com/ibuttimer/analastock/labels/bug)

| Issue                                                           | Description                                      |
|-----------------------------------------------------------------|--------------------------------------------------|
| Home key not working correctly from Company Search Results menu | https://github.com/ibuttimer/analastock/issues/9 |
