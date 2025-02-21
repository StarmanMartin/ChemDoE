FROM tobix/pywine:3.12

# docker run $(docker build -q .) > dist/ChemDoE.exe

RUN mkdir /app
WORKDIR /app

COPY . .

RUN wine python -m pip install --upgrade pip setuptools wheel
RUN wine pip install poetry pyinstaller pillow
RUN wine poetry self add  poetry-plugin-export
# CMD ["tail", "-f", "/dev/null"]

RUN wine poetry export --without-hashes --format=requirements.txt > requirements.txt

RUN wine pip install -r requirements.txt

CMD wine python pyinstaller.py > /dev/null 2>&1 & cat dist/ChemDoE.exe