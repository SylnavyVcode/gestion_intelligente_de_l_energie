## Créer le dossier du projet et initialiser le projet pour git
`
    mkdir gestion_intelligente_de_l_energie && cd gestion_intelligente_de_l_energie
    git init
`

## Créer un environnement virtuel
pour faire l'isolation des dépendances, pour ne pas casser d'autres projets Python sur la machine en installant des version différentes des mêmes librairies.

`
python3 -m venv venv
source venv/bin/activate
`

## Mettre en place l'arborence du projet 

`
mkdir -p data src/ingestion src/detection src/forecast src/api notebooks tests
touch requirements.txt README.md .gitignore
`

energie-dashboard/
├── data/              # datasets bruts et générés
├── src/               # tout ton code Python
│   ├── ingestion/
│   ├── detection/
│   ├── forecast/
│   └── api/
├── notebooks/         # exploration, tests rapides
├── tests/             # tests unitaires
├── requirements.txt
├── README.md
└── .gitignore

Avec le fichier .gitignore pour ne jamais versionner l'environnement virtuel ni les données dolumineuses.

faire le premier commit :
`git add . 
git commit -m "Initialisation structure du projet"`

## Télécharger et explorer le dataset UCI
### Installer les librairies nécessaires pour explorer
Ajoute dans requirements.txt :

pandas
matplotlib
jupyter

puis exécuter la commande : 
`pip install -r requirements.txt`

### télécharger le dataset
`
cd data
wget https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip
unzip individual+household+electric+power+consumption.zip
cd ..
`

### Lancer jupyter pour explorer
jupyter notebook

une fois ouvert on crée un fichier 01_exploration.ipynb,