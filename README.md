
## Design
The design specification is available in [design.md](design/design.md).

## Development/Local Deployment
### Environment
The development environment requires:
| Artifact | Download and installation instructions |
|----------|----------------------------------------|
| [Node.js](https://nodejs.org/) | https://nodejs.org/en/download/ |
| [npm](https://www.npmjs.com/) |  Included with Node.js installation |
| [git](https://git-scm.com/) | https://git-scm.com/downloads |
| [Python](https://www.python.org/) | https://www.python.org/downloads/ |
| [Total.js framework](https://www.totaljs.com/) | Installed during [Framework Setup](#framework-setup) |

### Setup
#### Clone Repository
In an appropriate folder, run the following commands:
```shell
> git clone https://github.com/ibuttimer/analastock.git
> cd analastock
```

#### Virtual Environment
It is recommended that a virtual environment be used for development purposes.
Please see [Creating a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) for details.

> __Note:__ Make sure to [activate the virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

#### Framework Setup
In the `analastock` folder, run the following command to setup the [Total.js](https://www.totaljs.com/) framework:
```shell
> npm install
```

#### Python Setup
In the `analastock` folder, run the following command to install the necessary python packages:
```shell
> pip install -r requirements-dev.txt
```
#### Production versus Development Setup
Installing the requirements from [requirements-dev.txt](requirements-dev.txt) installs extra development-only requirements in addition to the production requirements from [requirements.txt](requirements.txt).

### Configuration
The application configuration may be set using using environment variables or a configuration file.

#### Credentials

##### Google Drive API
TODO

##### RapidAPI
[RapidAPI](https://rapidapi.com/) is used to retrieve stock exchange and company information.

- Sign up or log in on the [RapidAPI home page](https://rapidapi.com/)
- In the [API hub](https://rapidapi.com/hub), select the [Finance](https://rapidapi.com/category/Finance) category
- Select the [YahooFinance Stocks](https://rapidapi.com/integraatio/api/yahoofinance-stocks1/) API
- Select the `Subscribe to Test` option
- Select the `Basic` plan and enter payment card details
- Once subscribed, the API credentials may be retrieved by selecting `Python (Requests)` under `Code Snippets`, and copying the JSON for the `headers` variable
  ```python
  {
    "X-RapidAPI-Key": "this-is-the-api-key",
    "X-RapidAPI-Host": "yahoofinance-stocks1.p.rapidapi.com"
  }
  ```

#### Configuration file
Create a file named `.env` in the project root folder, see [.sample-env](.sample-env). The following variables may be set:

###### Table 1: Configuration settings
| Key | Value |
|-----|-------|
| PORT | Port application is served on; default 8000 |
| NODE_ENV | Set to 'production' or 'development', see [Node.js, the difference between development and production](https://nodejs.dev/learn/nodejs-the-difference-between-development-and-production) |
| PYTHON_PATH | Path to python executable; default ''.<br>__Note:__ if a relative path is specified, it must be relative to the project root folder. E.g. if using a [venv virtual environment](https://docs.python.org/3/library/venv.html#module-venv) in the project root folder, use `./venvd/Scripts/` |
| PYTHON_EXE | Python executable; default 'python3'.<br>__Note:__ If running on windows, full filename including extension is required, e.g. 'python.exe' |
| APP_PATH | Path to app folder; default '/app'.<br>__Note:__ if a relative path is specified, it must be relative to the project root folder. E.g. the default location is the project root folder, so use `CREDS_PATH` |
| CREDS | Google Drive API credentials |
| CREDS_FILE | Name of name of Google Drive API credentials file; default `creds.json` |
| CREDS_PATH | Path to Google Drive API credentials file; default `./`<br>__Note:__ must be relative to the project root folder |
| RAPID_CREDS | [RapidAPI](https://rapidapi.com/) credentials |
| RAPID_CREDS_FILE | Name of name of [RapidAPI](https://rapidapi.com/) credentials file; default `rapid_creds.json` |
| RAPID_CREDS_PATH | Path to [RapidAPI](https://rapidapi.com/) credentials file; default `./`<br>__Note:__ must be relative to the project root folder |
| DATA_PATH | Path to sample data folder; default `./data`<br>__Note:__ must be relative to the project root folder |
| SPREADSHEET_NAME | Name of Google Sheets spreadsheet |

#### Environment variables
Set environment variables corresponding to the keys in [Table 1: Configuration settings](#table-1-configuration-settings).

E.g.
```shell
For Linux and Mac:                       For Windows:
$ export NODE_ENV=development            > set NODE_ENV=development
```

### Application structure
The application structure is split in two; a [Total.js](https://www.totaljs.com/) application which hosts the console, and a [Python](https://www.python.org/) application which provides the application logic.

```
├─ README.md            - this file
| [------------ Total.js application ------------]
├─ index.js             - application entry point
├─ controllers          - JavaScript controllers
├─ views                - views html files
├─ public               - application assets
│  └─ img               - image files
| [------------  Python application  ------------]
├─ run.py               - Python application entry point
├─ data                 - sample data files
├─ misc                 - miscellaneous functions
├─ sheets               - Google sheets-related functions
├─ stock                - stock-related functions
├─ process              - process-related functions
├─ utils                - utility functions
└─ test                 - test scripts
   ├─ sheets_tests      - Google sheets-related tests
   ├─ stock_tests       - stock tests
   └─ utils_tests       - utility tests
```

## Deployment

The site was deployed on [Heroku](https://www.heroku.com).

The following steps were followed to deploy the website: 
  - Login to Heroku
  - From the dashboard select `New -> Create new app`
  - Set the values for `App name`, choose the appropriate region and click `Create app`
  - From the app settings, select the `Settings` tab.
    - Under `Buildpacks` add the following buildpacks
      1. `heroku/python`
      1. `heroku/nodejs`
    - Under `Config Vars` add the following environment variables

      | Key | Value |
      |-----|-------|
      | PORT | 8000 |
      | CREDS | Google Drive API credentials |
      | RAPID_CREDS | [RapidAPI](https://rapidapi.com/) credentials |

      See [Table 1: Configuration settings](#table-1-configuration-settings) for details.

  - From the app settings, select the `Deploy` tab.
    - For the `Deployment method`, select `GitHGub` and link your Heroku app to your GitHub repository.

      __Note:__ To configure GitHub integration, you have to authenticate with GitHub. You only have to do this once per Heroku account. See [GitHub Integration (Heroku GitHub Deploys)](https://devcenter.heroku.com/articles/github-integration).
    - `Enable Automatic Deploys` under `Automatic deploys` to enable automatic deploys from GitHub following a GitHub push if desired.
    - The application may also be deployed manually using `Deploy Branch` under `Manual deploy`

The live website is available at [https://analastock.herokuapp.com/](https://analastock.herokuapp.com/)





Welcome USER_NAME,

This is the Code Institute student template for deploying your third portfolio project, the Python command-line project. The last update to this file was: **August 17, 2021**

## Reminders

* Your code must be placed in the `run.py` file
* Your dependencies must be placed in the `requirements.txt` file
* Do not edit any of the other files or your code may not deploy properly

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

-----


## Credits

The following resources were used to build the website.

### Content

- The favicon for the site was generated by [RealFaviconGenerator](https://realfavicongenerator.net/) from [graph image](https://lineicons.com/icons/?search=graph&type=free) by [Lineicons](https://lineicons.com/)
