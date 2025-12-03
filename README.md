Chart of Account Connector
===========================

This project handles the Chart of Accounts synchornisation between an excel workbook and Quickbooks. The connector takes in a .xlsx workbook, and adds the accounts from the workbooks to quickbooks.

The results of running the chart of accounts connector are compiled into a json file which will indicate which accounts were added to quickbooks and any conflits that may have occured.

## Build
To build an `.exe` file of the connector:

1. Install dependencies
    ```bash
    poetry install
    ```

2. Build the executable:
    ```bash
    poetry run pyinstaller --onefile --name src --hidden-import win32timezone --hidden-import win32com.client build_exe.py
    ```

3. The executable will be created in the `dist` folder.

The `--hidden-import` flags ensure PyInstaller includes the Windows COM dependencies needed for QuickBooks integration.

After building, to run the exe, launch the CLI directly from Command Prompt:

1. Change into the `dist` directory (or reference the full path):
   ```cmd
   cd dist
   ```
2. Run the executable with the same arguments the Python entry point expects:
   ```cmd
   ./src.exe --workbook C:\path\to\ChartOfAccounts.xlsx --output C:\path\to\report.json
   ```

If you omit `--output`, the report defaults to `chartOfAccounts_report.json` in the current directory. You can also invoke it without `cd` by using the absolute path, e.g.:

```cmd
.\src.exe --workbook C:\Users\\MunozJ\QB_Connector_CoA_Python_Fall_2025\company_data.xlsx --output C:\Users\MunozJ\QB_Connector_CoA_Python_Fall_2025\report.json
```
