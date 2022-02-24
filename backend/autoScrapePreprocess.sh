 #!/bin/bash

 PATH=$PATH_ENV_JUPYTER
 
 cd scraping

 python update.py

 cd ../analysis/3p

 #papermill 3p_advanced_details.ipynb output.ipynb
 #papermill 3p_advanced_totals.ipynb output.ipynb
 #papermill 3p_game_details.ipynb output.ipynb
 #papermill 3p_game_totals.ipynb output.ipynb
 papermill 3p_shooting.ipynb output.ipynb

