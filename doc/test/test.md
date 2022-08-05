# Testing 

Test release: [Release ??]()

The site was tested using the following methods:

## Unittest Unit Testing 
Unit testing of scripts was undertaken using [unittest](https://docs.python.org/3/library/unittest.html#module-unittest).
The test scripts are located in the [tests](../../tests/) folder.

**Note:** If using a [Virtual Environment](../../README.md#virtual-environment), ensure it is activated. Please see [Activating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

The tests may be run from the project root folder:
```shell
Run all tests
> python -m unittest

Run an individual test, e.g.
> python -m unittest tests\utils_tests\test_input.py
```
Alternatively, if using Visual Studio Code, the [Test Explorer UI](https://marketplace.visualstudio.com/items?itemName=hbenl.vscode-test-explorer) or Visual Studio Code's native testing UI<sup>*</sup>, allows tests to be run from the sidebar of Visual Studio Code.

<sup>*</sup> Set `testExplorer.useNativeTesting` to true in the Visual Studio Code settings.

## Manual 
The site was manually tested in the following browsers:

|   | Browser | OS | 
|---|---------|----|
| 1 | Google Chrome, Version 103.0.5060.53 | Windows 11 Pro Version 21H2 |
| 2 | Mozilla Firefox, Version 101.0.1 (64-bit) | Windows 11 Pro Version 21H2 |
| 3 | Opera, Version:88.0.4412.53 | Windows 11 Pro Version 21H2 |

Testing undertaken:

| Feature | Expected | Action | Related | Result | 
|---------|----------|--------|---------|--------|
|  |  |   | ![pass](https://badgen.net/badge/checks/Pass/green) |


## Responsiveness Testing

As the terminal window size is fixed, this makes the site is unsuitable for responsiveness testing.

## Lighthouse

TODO

## Accessibility
As the main content of the site is in the terminal window, this makes the site is unsuitable for accessibility testing.

## User
TODO


## Validator Testing 

The [W3C Nu Html Checker](https://validator.w3.org/nu/) was utilised to check the HTML validity, while the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) was utilised to check the CSS validity with respect to [CSS level 3 + SVG](https://www.w3.org/Style/CSS/current-work.html.)

| Page | HTML | HTML Result | CSS | CSS Result |
|------|------|-------------|-----|------------|
| Landing | [W3C validator](https://validator.w3.org/nu/?doc=https%3A%2F%2Fanalastock.herokuapp.com%2F) | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fanalastock.herokuapp.com%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | ![pass](https://badgen.net/badge/checks/Pass/green) |


## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/analastock/issues).

### Unfixed Issues

#### Bug
There are currently no issues outstanding. 

#### Enhancement
TODO
