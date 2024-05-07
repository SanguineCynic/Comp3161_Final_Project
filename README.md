# Student Management DBMS Project

For the UWI course COMP3161 - Introduction to Database Management Systems

## Authors

- [Jonathan Astwood](https://github.com/SanguineCynic) : 620151038
- [Richard Barnett](https://github.com/rbarnett3940) : 
- [Pierre Mannix](https://github.com/Xman77713) : 620151974
- [Calvin Stephenson](https://github.com/cstephenson882) : 620130499


## Usage

1. Prerequisites
   - Python3 v3.11+
   - MySQL Server / Workbench CE
   - Cloned git repo
2. Initial Setup (MySQL CLI)
   - CREATE USER 'calvin2'@'localhost' IDENTIFIED BY '12345678';
   - GRANT ALL PRIVILEGES ON database_final_project_v1.* TO 'calvin2'@'localhost';
   - FLUSH PRIVILEGES;
   - SOURCE ./Comp3161_Final_Project/Raw SQL/create_db.sql;
3. Running scripts (Windows CLI / Terminal / CMD / PowerShell)
   - cd ./Comp3161_Final_Project/Flask/
   - python -m venv venv
   - .\\venv\\Scripts\\activate
   - python -m pip install -r ../requirements.txt
   - python -m insert_values.py
       - If you would like a new set of randomized data for any of the tables, simply run the associated .py file
   - 
