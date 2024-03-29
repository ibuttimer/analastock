
# Strategy
The strategy is to create a website allowing the user to retrieve historical stock data for analysis.

The target audience for the application are investors. The site will provide them with insight into the performance of stocks they have invested in, or are considering investing in.

# Scope
The scope of the project will be to allow the user to:
- Specify the symbol of the stock for analysis
- Specify the date range of the historical data to analyse
- Specify the symbols for multiple stocks to compare


## User Stories/Objectives
As a user:
- I want to understand the purpose of the site.
- I want to be able to specify the stock to analyse.
- I do not want to analyse stock indices, such as the Dow Jones Industrial Average.
- I want to be able to specify the date range to analyse.
- I want to be able to view the statistics for stock analysed, including but not limited
  - min/max opening price
  - min/max high price
  - percentage gain/loss
- I want to have a menu to use
- I want to be able to compare multiple stocks against each other
- I want the analysis data to be easily understood, with important data colour highlighted
- I want to know what currency was used for the data
- I want to be able to search for stock symbols

As the site administrator:
- I want to minimise the download of data from external websites
- I want to aggregate previously downloaded and required data to meet user needs
- I want to use [Yahoo Finance](https://finance.yahoo.com/) to stock data
- I want to use [RapidAPI](https://rapidapi.com/) is used to retrieve stock exchange and company information
- I want to use Google APIs to access and store downloaded data

## Objectives Implementation

| Objective                                                                                | Implementation                                                                                                                                                                                                                                                                            |
|------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| I want to be able to specify the stock to analyse                                        | [Analysis Stock Selection](../../README.md#analysis-stock-selection)<br>[Search](../../README.md#search)                                                                                                                                                                                  |
| I want to be able to specify the date range to analyse                                   | [Period Entry](../../README.md#period-entry)                                                                                                                                                                                                                                              |
| I want to be able to view the statistics for stock analysed                              | [Analysis Results](../../README.md#analysis-results)                                                                                                                                                                                                                                      |
| I want to have a menu to use                                                             | [Menu](../../README.md#menu)                                                                                                                                                                                                                                                              |
| I want to be able to compare multiple stocks against each other                          | [Analysis Stock Selection](../../README.md#analysis-stock-selection)<br>[Multi-Stock Analysis Results](../../README.md#multi-stock-analysis-results)                                                                                                                                      |
| I want the analysis data to be easily understood, with important data colour highlighted | [Multi-Stock Analysis Results](../../README.md#multi-stock-analysis-results)                                                                                                                                                                                                              |
| I want to know what was currency used for the data                                       | [Single Stock Analysis Results](../../README.md#single-stock-analysis-results)<br>[Multi-Stock Analysis Results](../../README.md#multi-stock-analysis-results)                                                                                                                            |
| I want to use Google APIs to access and store downloaded data                            | [Data Storage](../../README.md#data-storage)                                                                                                                                                                                                                                              |
| I want to aggregate previously downloaded and required data to meet user needs           | [process_multi_stock()](https://github.com/ibuttimer/analastock/blob/main/process/basic.py#L150)<br>[process_stock()](https://github.com/ibuttimer/analastock/blob/main/process/basic.py#L295)<br>[fill_gaps()](https://github.com/ibuttimer/analastock/blob/main/process/basic.py#L329)  |


# Structure

# Skeleton
The website will consist of a single page.

# General layout
A console terminal will be used for user input and analysis display purposes.

# Wireframes
Wireframes of page layouts are as followings:

## Home page

The Home page will have the following features:
- 80 x 24 character terminal console
- Run Program button

![](img/analastock-home.drawio.png)

# UX Surface
## Font
The font used for console text will be Courier.

## Colour Scheme

The console text will be white on a black background.

## UX Elements

### Menu
The application menu will display a list of possible options, allowing the user to select an option by inputting the corresponding option number.

#### Menu Structure
1. **_Stock Analysis_**

   Access stock analysis menu

   1. **_Single stock_** : Analyse single stock

      1. **_Enter stock symbol_** : Manually enter single stock

      1. **_Search company_** : Analyse multiple stocks

         - **_Enter period_** : Analyse period

   2. **_Multiple stock_** : Analyse multiple stocks

      - **_Enter number of stocks_** : Number of stocks to analyse

        1. **_Enter stock symbol_** : Manually enter single stock

        2. **_Search company_** : Analyse multiple stocks

           - **_Enter period_** : Analyse period

2. **_Search Company_** : In-app search for company information

     - **_Enter name_** : Search term

3. **_Update Company Information_** : Update the in-app company information

4. **_Quit_** : Quit the application

### Screen Layout

#### Analysis Result (Single Company)
##### Data available
```
80 Columns
12345678901234567890123456789012345678901234567890123456789012345678901234567890

                                                                        Currency
Stock : IBM - International Business Machines Corporation                    USD
Period: 01 Mar 2022 - 01 Jul 2022
              Min          Max          Avg         Change         % 
Open      ............ ............ ............ ............ ............
Low       ............ ............ ............ ............ ............   
High      ............ ............ ............ ............ ............   
Close     ............ ............ ............ ............ ............   
AdjClose  ............ ............ ............ ............ ............       
Volume    ............ ............ ............ ............ ............     
```

##### Missing Data
In the event that it was not possible to retrieve data for the full range requested, this will be highlight as follows:
```
80 Columns
12345678901234567890123456789012345678901234567890123456789012345678901234567890

                                                                        Currency
Stock : IBM - International Business Machines Corporation                    USD
Period: 01 Mar 2022* - 01 Jul 2022**
              Min          Max          Avg         Change         % 
Open      ............ ............ ............ ............ ............
Low       ............ ............ ............ ............ ............
High      ............ ............ ............ ............ ............
Close     ............ ............ ............ ............ ............
AdjClose  ............ ............ ............ ............ ............
Volume^   ............ ............ ............ ............ ............

* : Data n/a 05 Jun 2003 - 28 Feb 2022
**: Data n/a 02 Jul 2003 - 29 Jul 2022
^ : Data missing
```

#### Analysis Result (Multiple Companies)
##### Data available
```
80 Columns
12345678901234567890123456789012345678901234567890123456789012345678901234567890

                                                                        Currency
1] Stock : MSFT    - Microsoft Corporation                                   USD
2] Stock : MSFT.NE - Microsoft Corporation                                   CAD
3] Stock : MSFT.MX - Microsoft Corporation                                   MXN
   Period: 01 Mar 2022 - 01 Jul 2022
          Stock    Min          Max          Avg         Change         % 
Open      1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Low       1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
High      1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Close     1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
AdjClose  1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Volume    1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
```

##### Missing Data
In the event that it was not possible to retrieve data for the full range requested, this will be highlight as follows:
```
80 Columns
12345678901234567890123456789012345678901234567890123456789012345678901234567890

                                                                        Currency
1] Stock : MSFT    - Microsoft Corporation                                   USD
2] Stock : MSFT.NE - Microsoft Corporation                                   CAD
3] Stock : MSFT.MX - Microsoft Corporation                                   MXN
   Period: 01 Mar 2022* - 01 Jul 2022**
          Stock    Min          Max          Avg         Change         % 
Open      1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Low       1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
High      1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Close     1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
AdjClose  1]   ............ ............ ............ ............ ............
          2]   ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............
Volume    1]   ............ ............ ............ ............ ............
          2]^  ............ ............ ............ ............ ............
          3]   ............ ............ ............ ............ ............

* : 1] Data n/a 05 Jun 2003 - 28 Feb 2022
  : 3] Data n/a 05 Jun 2003 - 28 Feb 2022
**: 2] Data n/a 02 Jul 2003 - 29 Jul 2022
^ : Data missing
```

## UX Flow Chart

## Stock Analysis
The flow chart of the analysis of a stock is as follows:

![](img/analastock-analyse-stock.drawio.png)

## Single Stock Analysis
The flow chart of the analysis of stock is as follows:

| Single                                         | Multiple                                           |
|------------------------------------------------|----------------------------------------------------|
| ![](img/analastock-analyse-1-stock.drawio.png) | ![](img/analastock-analyse-multi-stock.drawio.png) |

## Company Search
The flow chart of the search for a company is as follows:

![](img/analastock-search-company.drawio.png)


# Data
## Data Sources
### Historical financial data
The financial data for analysis will be downloaded from [Yahoo Finance](https://finance.yahoo.com/).
Specifically the data used will the `Historical Prices` data provided by [Yahoo Finance](https://finance.yahoo.com/).

The following input will be required from the user:

| Input     | Description                                                                                                                                                                                                                                                                                                                                                                   |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Symbol    | The Yahoo Finance stock exchange symbol used for the stock.<br>Symbols may be found by searching on [Yahoo Finance](https://finance.yahoo.com/) or by using the in-app search functionality. E.g. the symbol for Microsoft Corporation on the [NASDAQ](https://www.nasdaq.com/) Global Select Market is `MSFT`, and for the [NEO Exchange](https://www.neo.inc/) is `MSFT.NE` |
| From date | The data for the start of analysis                                                                                                                                                                                                                                                                                                                                            |
| To date   | The data for the end of analysis<br>__Note:__ This is date is not included in the analysis.                                                                                                                                                                                                                                                                                   |

### Other data
Other data required; exchange and company meta-data, will be downloaded from the [YahooFinance Stocks](https://rapidapi.com/integraatio/api/yahoofinance-stocks1/) API from [RapidAPI](https://rapidapi.com/).
Specifically the endpoints used will be:
| Endpoint | Description |
|----------|-------------|
| List exchanges | List all exchanges known to have stocks associated with them |
| Companies By Exchange | List Of Common Stocks Per Exchange Code |
| Live Stock Metadata | Real time metadata about the stock |

## Data Flow
![](img/analastock-data-flow.drawio.png)


## Data Storage
Data will be stored in a Google Sheets spreadsheet.

### Stock Data
Stock data will be organised as follows:
- The data for each stock will be stored in an individual worksheet
- The stock symbol will be used as the worksheet name
- The following data will be stored:

    | Name | Type | Description |
    |------|------|-------------|
    | Date | Date | Date of data |
    | Open | Float | Opening price |
    | High | Float | High price |
    | Low  | Float | Low price |
    | Close | Float | Closing price<br>__Note:__ Close price adjusted for splits. |
    | Adj Close | Float | Adjusted Closing price<br>__Note:__ Adjusted close price adjusted for splits and dividend and/or capital gain distributions. |
    | Volume | Integer | Opening price |

### Exchanges Data
Exchanges data will be stored in an individual worksheet.
The following data will be stored:

| Data          | Description      |
|---------------|------------------|
| Exchange code | Exchange code    |
| Name          | Name of exchange |

### Companies Data
Companies data will be stored in an individual worksheet.
The following data will be stored:

| Data               | Description                                                |
|--------------------|------------------------------------------------------------|
| Exchange code      | Exchange code                                              |
| Stock symbol       | Symbol used on [Yahoo Finance](https://finance.yahoo.com/) |
| Name               | Name of company                                            |
| IndustryOrCategory | Industry or category of the company                        |
| Currency           | Stock currency                                             |

## External Libraries
The following third party libraries will be utilised:

| Library | Use | Description |
|---------|-----|-------------|
| [google-auth](https://pypi.org/project/google-auth/) | Access Google resources | This library simplifies using Google’s various server-to-server authentication mechanisms to access Google APIs. For details see the [usage and reference documentation](https://googleapis.dev/python/google-auth/latest/index.html). |
| [gspread](https://pypi.org/project/gspread/) | Work with Google Sheets | Provides a Google Spreadsheets Python API. For details see [gspread docs](https://docs.gspread.org/en/v5.4.0/). |
| [pandas](https://pypi.org/project/pandas/) | Perform analysis of stocks | A package providing fast, flexible, and expressive data structures, with powerful data analysis functionality. For details see [pandas documentation](https://pandas.pydata.org/docs/).
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Application configuration | Read key-value pairs from a `.env` file and set them as environment variables. |
| [colorama](https://pypi.org/project/colorama/)<br>[termcolor](https://pypi.org/project/termcolor/) | Coloured terminal text | Makes ANSI escape character sequences work under MS Windows.<br>ANSI Colour formatting for output in terminal. |
| [requests](https://pypi.org/project/requests/) | Perform HTTP requests | A HTTP library. For details see the [documentation](https://requests.readthedocs.io/en/latest/). |
| [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)<br>[lxml](https://pypi.org/project/lxml/) | Capture HTML page content | A library that makes it easy to scrape information from web pages. For details see the [documentation](https://www.crummy.com/software/BeautifulSoup/).<br>XML processing library. For details see the [documentation](https://lxml.de/). |
