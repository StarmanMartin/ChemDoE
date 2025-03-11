
python -m pip install --upgrade pip setuptools wheel
pip install poetry
poetry add pyinstaller

poetry install --no-root
poetry run python ./pyinstaller.py