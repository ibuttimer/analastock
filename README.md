
## Design
The design specification is available in [design.md](design/design.md).

## Development
### Environment
The development environment requires:
* [Node.js](https://nodejs.org/)
* [npm](https://www.npmjs.com/)
* [git](https://git-scm.com/)
* [Python](https://www.python.org/)

### Setup
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

#### Configuration file
Create a file named `.env` in the project root folder, see [.sample-env](.sample-env). The following variables may be set:

###### Table 1: Configuration settings
| Key | Value |
|-----|-------|
| PORT | Port application is served on; default 8000 |
| NODE_ENV | Set to 'production' or 'development', see [Node.js, the difference between development and production](https://nodejs.dev/learn/nodejs-the-difference-between-development-and-production) |
| PYTHON_PATH | Path to python executable; default ''.<br>__Note:__ if a relative path is specified, it must be relative to the project root folder. E.g. if using a [venv virtual environment](https://docs.python.org/3/library/venv.html#module-venv) in the project root folder, use `./venvd/Scripts/` |
| PYTHON_EXE | Python executable; default 'python3'.<br>__Note:__ If running on windows, full filename including extension is required, e.g. 'python.exe' |
| APP_PATH | Path to app folder; default '/app'.<br>__Note:__ if a relative path is specified, it must be relative to the project root folder. E.g. the default location is the project root folder, so use `./` |
| CREDS | Google Drive API credentials |

#### Environment variables
Set environment variables corresponding to the keys in [Table 1: Configuration settings](#table-1-configuration-settings).

E.g.
```shell
For Linux and Mac:                       For Windows:
$ export NODE_ENV=development            > set NODE_ENV=development
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
