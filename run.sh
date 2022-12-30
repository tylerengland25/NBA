 #!/bin/bash

 python backend/scraping/update.py

 python backend/preprocess/3p/shooting.py
 python backend/preprocess/3p/game_totals.py
 python backend/preprocess/3p/game_details.py

 python modeling/main.py

 streamlit run frontend/main.py
