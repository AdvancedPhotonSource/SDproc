# SDproc
## Development
- Download and install [anaconda](https://www.anaconda.com/download/#linux)
- Fork the project to your Git profile from: AdvancedPhotonSource/SDproc

## IDE
- Downlad and install [PyCharm](https://www.jetbrains.com/pycharm/download/#section=linux)

## Execute in terminal
```
# Clone the project from your fork
git clone <WEB URL>

# cd into the project directory
cd toTheProject

# create a conda environment to run the applicaiton dependencies
conda env create -f anaconda/environment.yml

# activate the conda environment
conda activate SDproc

#Run this command every time you start a new terminal session to run the project
python app.py 
```

## Notes
- DM module access
    - to connect to DM api ask Sinisa for username and password
- DM module for some reason hides server log
    - to fix this comment out the DM import
    - line #58 and #88 on app.py file
- Access to DB
    ##### Execute in terminal
    ```
    # cd into the data folder
    cd SDproc/data
    
    # open database
    sqlite3 test.db
  
    # view tables
    .tables
  
    # SQL example
    select * from <table name>;
    
    # exit
    cntrl + z
    ```
