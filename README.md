# MTU - time series annotator

## Quick start

### Install dependencies

Using python 3.10 or 3.11 install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Place your data

Place your plots and data in the "artifacts/app_data" directory.
It should maintain the following structure:

- moving average window size (e.g. 0.05):
  - reference_table.csv - table with all measurements and path to their plots
  - machine id:
    - plots:
      - measurement:
        - plot_file.html

### Run app

```bash
streamlit run src/annotator.py
```

### Select parameters

Select all parameters and click "To Annotations".

### Start your annotations

Annotate time serieses using hot keys.

#### Hot keys

- ← - previous  
- → - next  
- 1 - normal  
- space - normal  
- 2 - edge case  
- 3 - anomaly  
- ctrl/cmd + s - save  

## Other apps

### All data viewer

Here you can search through entire dataset.
