# create venv
python3 -m venv environments/training
# activate
source environments/preprocessing/bin/activate

# requirements
pip install -r "requirements_training.txt"
# nb: optional dependencies for torch
pip install torch==1.8.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# nb: optional dependencies for spacy
pip install spacy[cuda101]

deactivate