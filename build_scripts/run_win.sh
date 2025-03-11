
wine python -m pip install --upgrade pip setuptools wheel
wine pip install poetry
wine poetry add pyinstaller

wine poetry install --no-root
wine poetry run python ./pyinstaller.py

