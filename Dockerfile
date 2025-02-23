FROM tobix/pywine:3.11

# docker run $(docker build -q .) > dist/ChemDoE.exe

RUN mkdir /app
WORKDIR /app

COPY . .

RUN wine python -m pip install --upgrade pip setuptools wheel
RUN wine pip install poetry
RUN wine poetry add pyinstaller
RUN wine poetry add python-magic-bin

CMD wine poetry install > requirements.txt & wine poetry run python pyinstaller.py