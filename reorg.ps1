$dir = "C:\Users\Lenovo\Desktop\DAP391_project"

# Create new directories
New-Item -ItemType Directory -Force -Path "$dir\01_data\raw"
New-Item -ItemType Directory -Force -Path "$dir\01_data\processed"
New-Item -ItemType Directory -Force -Path "$dir\01_data\train_test"
New-Item -ItemType Directory -Force -Path "$dir\02_docs\planning"
New-Item -ItemType Directory -Force -Path "$dir\02_docs\reports"
New-Item -ItemType Directory -Force -Path "$dir\03_src\api"
New-Item -ItemType Directory -Force -Path "$dir\03_src\app"
New-Item -ItemType Directory -Force -Path "$dir\03_src\data_prep"
New-Item -ItemType Directory -Force -Path "$dir\03_src\models"
New-Item -ItemType Directory -Force -Path "$dir\04_models\saved"
New-Item -ItemType Directory -Force -Path "$dir\05_visuals\eda"
New-Item -ItemType Directory -Force -Path "$dir\05_visuals\evaluation"
New-Item -ItemType Directory -Force -Path "$dir\06_database"

# Move files
# Data
if (Test-Path "$dir\03_Data\data\raw\*") { Move-Item -Force "$dir\03_Data\data\raw\*" "$dir\01_data\raw\" }
if (Test-Path "$dir\03_Data\data\processed\*") { Move-Item -Force "$dir\03_Data\data\processed\*" "$dir\01_data\processed\" }
if (Test-Path "$dir\05_visual\data visualization step 3\train_data.csv") { Move-Item -Force "$dir\05_visual\data visualization step 3\train_data.csv" "$dir\01_data\train_test\" }
if (Test-Path "$dir\05_visual\data visualization step 3\test_data.csv") { Move-Item -Force "$dir\05_visual\data visualization step 3\test_data.csv" "$dir\01_data\train_test\" }

# Docs
if (Test-Path "$dir\01_Docs\PLaning\*") { Move-Item -Force "$dir\01_Docs\PLaning\*" "$dir\02_docs\planning\" }
if (Test-Path "$dir\proposal\*") { Move-Item -Force "$dir\proposal\*" "$dir\02_docs\planning\" }
if (Test-Path "$dir\06_Final_Reports\*") { Move-Item -Force "$dir\06_Final_Reports\*" "$dir\02_docs\reports\" }
if (Test-Path "$dir\01_Docs\User_Guide_Step6.md") { Move-Item -Force "$dir\01_Docs\User_Guide_Step6.md" "$dir\02_docs\" }
if (Test-Path "$dir\03_Data\docs\*") { Move-Item -Force "$dir\03_Data\docs\*" "$dir\02_docs\" }

# Src
if (Test-Path "$dir\02_src\app.py") { Move-Item -Force "$dir\02_src\app.py" "$dir\03_src\api\" }
if (Test-Path "$dir\02_src\export_predictions.py") { Move-Item -Force "$dir\02_src\export_predictions.py" "$dir\03_src\api\" }
if (Test-Path "$dir\02_src\streamlit_app.py") { Move-Item -Force "$dir\02_src\streamlit_app.py" "$dir\03_src\app\" }

if (Test-Path "$dir\03_Data\scripts\python\generate_rfm.py") { Move-Item -Force "$dir\03_Data\scripts\python\generate_rfm.py" "$dir\03_src\data_prep\" }
if (Test-Path "$dir\03_Data\scripts\python\import_to_sql.py") { Move-Item -Force "$dir\03_Data\scripts\python\import_to_sql.py" "$dir\03_src\data_prep\" }
if (Test-Path "$dir\03_Data\scripts\python\split_train_test.py") { Move-Item -Force "$dir\03_Data\scripts\python\split_train_test.py" "$dir\03_src\data_prep\" }

if (Test-Path "$dir\02_src\models\train_uplift_model.py") { Move-Item -Force "$dir\02_src\models\train_uplift_model.py" "$dir\03_src\models\" }
if (Test-Path "$dir\05_visual\data visualization step 3\visualization.py") { Move-Item -Force "$dir\05_visual\data visualization step 3\visualization.py" "$dir\03_src\models\" }
if (Test-Path "$dir\02_src\check_stats.py") { Move-Item -Force "$dir\02_src\check_stats.py" "$dir\03_src\models\" }

# Models
if (Test-Path "$dir\04_Model\*.pkl") { Move-Item -Force "$dir\04_Model\*.pkl" "$dir\04_models\saved\" }

# Visuals
if (Test-Path "$dir\03_Data\outputs\step2\*.png") { Move-Item -Force "$dir\03_Data\outputs\step2\*.png" "$dir\05_visuals\eda\" }
if (Test-Path "$dir\03_Data\outputs\step2\*.md") { Move-Item -Force "$dir\03_Data\outputs\step2\*.md" "$dir\05_visuals\eda\" }
if (Test-Path "$dir\05_visual\*.png") { Move-Item -Force "$dir\05_visual\*.png" "$dir\05_visuals\evaluation\" }
if (Test-Path "$dir\05_visual\data visualization step 3\*.png") { Move-Item -Force "$dir\05_visual\data visualization step 3\*.png" "$dir\05_visuals\evaluation\" }

# Database
if (Test-Path "$dir\03_Data\database\Project11DB.sql") { Move-Item -Force "$dir\03_Data\database\Project11DB.sql" "$dir\06_database\" }

# Delete empty directories (if they are empty)
Write-Output "Done creating and moving!"
