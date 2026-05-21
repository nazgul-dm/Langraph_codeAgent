# Dockerfile

# Startpunkt: Python 3.11 (klein und sauber)
FROM python:3.11-slim

# Alle Bibliotheken die du erlauben willst, vorher installieren
RUN pip install \
    numpy \
    pandas \
    scipy \
    matplotlib \
    scikit-learn \
    requests

# Arbeitsordner im Container
WORKDIR /sandbox 
