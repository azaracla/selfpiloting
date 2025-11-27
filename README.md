# Star Citizen AI Agent - Training Data Recorder

Un outil pour enregistrer des sessions de jeu Star Citizen afin d'entraîner une IA de pilotage type AlphaStar. L'outil capture simultanément la vidéo de gameplay et tous les inputs clavier/souris de manière synchronisée.

## 🎯 Objectif

Créer un dataset d'entraînement pour développer une IA capable de piloter un vaisseau dans Star Citizen en utilisant uniquement:
- Vision par ordinateur (analyse de l'écran)
- Actions clavier/souris (comme un joueur humain)
- Apprentissage par renforcement (Reinforcement Learning)

**Aucune modification du code du jeu n'est nécessaire** - l'IA apprend en observant l'écran et en reproduisant les actions du joueur.

## 🚀 Installation

### Prérequis
- Windows 10/11
- Python 3.8 ou supérieur
- Star Citizen installé

### Installation des dépendances

```bash
# Cloner ou télécharger ce projet
git clone <repo-url>
cd selfpiloting

# Installer les dépendances
pip install -r requirements.txt
```

## 📹 Utilisation

### Enregistrement de base

```bash
# Démarrer un enregistrement simple
python record.py
```

L'outil vous donne 3 secondes pour basculer vers Star Citizen, puis commence l'enregistrement.

**Pour arrêter:** Appuyez sur `Ctrl+C`

### Options avancées

```bash
# Enregistrer avec un nom personnalisé
python record.py --name "ace_pilot_session_01"

# Enregistrer en 60 FPS
python record.py --fps 60

# Enregistrer en Full HD
python record.py --fps 30 --resolution 1920 1080

# Enregistrer sur un dossier personnalisé
python record.py --output D:/StarCitizen_Training_Data

# Capturer un moniteur spécifique (pour multi-écrans)
python record.py --monitor 2
```

### Voir toutes les options

```bash
python record.py --help
```

## 📊 Données enregistrées

Chaque session génère un dossier avec les fichiers suivants:

```
recordings/
└── session_20231127_143022/
    ├── gameplay.mp4                    # Vidéo de gameplay
    ├── inputs.json                     # Tous les événements clavier/souris bruts
    ├── inputs_frame_aligned.json       # États des inputs alignés par frame
    └── metadata.json                   # Métadonnées de la session
```

### Format des données

#### `inputs_frame_aligned.json`
Format optimisé pour l'entraînement IA - un état d'input par frame vidéo:

```json
[
  {
    "timestamp": 0.033,
    "pressed_keys": ["Key.w", "Key.shift"],
    "mouse_x": 960,
    "mouse_y": 540,
    "mouse_buttons": ["left"]
  },
  ...
]
```

#### `inputs.json`
Événements bruts avec timestamps précis:

```json
{
  "events": [
    {
      "timestamp": 0.052,
      "type": "key_press",
      "data": {"key": "w", "key_id": "Key.w"}
    },
    {
      "timestamp": 0.053,
      "type": "mouse_move",
      "data": {"x": 960, "y": 540}
    },
    ...
  ]
}
```

## 🤖 Utilisation des données pour l'entraînement IA

### Charger les données

Utilisez le module `utils/load_data.py`:

```python
from utils.load_data import load_session

# Charger une session
loader = load_session("recordings/session_20231127_143022")

# Obtenir des informations
info = loader.get_info()
print(f"Frames: {info['num_frames']}, FPS: {info['fps']}")

# Charger un batch de frames + inputs
frames, inputs = loader.get_batch(start_frame=0, num_frames=100)

# frames.shape = (100, 720, 1280, 3)  # 100 frames RGB
# inputs = list of 100 input states
```

### Exemple d'intégration avec PyTorch

```python
import torch
from torch.utils.data import Dataset
from utils.load_data import load_session

class StarCitizenDataset(Dataset):
    def __init__(self, session_path):
        self.loader = load_session(session_path)
        self.num_frames = self.loader.get_num_frames()

    def __len__(self):
        return self.num_frames

    def __getitem__(self, idx):
        # Charger frame et input
        frames, inputs = self.loader.get_batch(idx, 1)

        frame = torch.from_numpy(frames[0]).permute(2, 0, 1)  # HWC -> CHW
        # Convertir inputs en tensor selon votre architecture...

        return frame, input_tensor

# Utilisation
dataset = StarCitizenDataset("recordings/session_20231127_143022")
dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
```

## 🎮 Conseils pour l'enregistrement

### Qualité des données

1. **Sessions courtes et ciblées** (5-10 minutes)
   - Plus facile à labelliser
   - Moins de données corrompues en cas de crash

2. **Scénarios variés**
   - Décollage/atterrissage
   - Combat spatial
   - Navigation en atmosphère
   - Manœuvres d'évasion
   - Vol en formation

3. **Qualité > Quantité**
   - Enregistrez vos meilleures performances
   - Évitez les sessions où vous êtes AFK ou dans les menus

### Performance

- **30 FPS** suffisant pour commencer (fichiers plus petits)
- **60 FPS** recommandé pour des actions rapides (combat)
- **Résolution 1280x720** bon compromis performance/qualité
- **1920x1080** si vous avez beaucoup d'espace disque

### Espace disque

Estimation pour 10 minutes d'enregistrement:
- 720p @ 30fps: ~500 MB
- 1080p @ 30fps: ~1 GB
- 1080p @ 60fps: ~2 GB

## 🛠️ Architecture du projet

```
selfpiloting/
├── src/
│   ├── screen_recorder.py      # Capture d'écran avec MSS
│   ├── input_recorder.py       # Enregistrement clavier/souris
│   └── data_recorder.py        # Coordination et sauvegarde
├── utils/
│   └── load_data.py            # Utilitaires de chargement
├── record.py                   # Script principal
├── requirements.txt            # Dépendances
└── README.md                   # Documentation
```

## 🔧 Configuration avancée

Copiez `config.example.yaml` vers `config.yaml` et ajustez selon vos besoins:

```yaml
recording:
  fps: 30
  resolution:
    width: 1280
    height: 720
  monitor: 1
  codec: libx264

output:
  directory: recordings
```

## 📝 Prochaines étapes

Une fois que vous avez enregistré suffisamment de données:

1. **Prétraitement des données**
   - Normalisation des images
   - Encodage des inputs
   - Découpage en séquences

2. **Architecture du modèle**
   - CNN pour traitement d'image
   - LSTM/Transformer pour séquences temporelles
   - Policy network pour actions

3. **Entraînement**
   - Behavioral Cloning (imitation learning)
   - Fine-tuning avec Reinforcement Learning
   - Multi-task learning

## ❓ FAQ

**Q: L'outil ralentit-il le jeu?**
A: Non, la capture d'écran avec MSS est très rapide. Impact minimal sur les performances.

**Q: Puis-je enregistrer d'autres jeux?**
A: Oui! L'outil fonctionne avec n'importe quel jeu Windows.

**Q: Les fichiers sont énormes!**
A: Réduisez la résolution (`--resolution 1280 720`) ou le FPS (`--fps 20`).

**Q: Puis-je rejouer les enregistrements?**
A: Les vidéos peuvent être lues avec n'importe quel lecteur MP4. Pour rejouer les inputs, vous devrez créer un script de playback séparé.

**Q: L'outil détecte-t-il les touches de manette?**
A: Non, uniquement clavier/souris pour le moment. Support manette prévu dans le futur.

## 🤝 Contribution

Les contributions sont bienvenues! N'hésitez pas à:
- Signaler des bugs
- Proposer des améliorations
- Partager vos modèles entraînés

## 📄 Licence

Ce projet est à but éducatif et de recherche. Respectez les conditions d'utilisation de Star Citizen.

## ⚠️ Avertissement

- Cet outil est pour l'**entraînement local** et la **recherche en IA**
- Ne pas utiliser pour tricher en multijoueur
- Vérifiez que l'enregistrement est conforme aux TOS de Star Citizen
- L'IA entraînée ne doit pas être utilisée pour automatiser le gameplay en ligne

## 🌟 Inspirations

- [AlphaStar](https://deepmind.com/blog/article/alphastar-mastering-real-time-strategy-game-starcraft-ii) - DeepMind's StarCraft II AI
- [OpenAI Five](https://openai.com/research/openai-five) - Dota 2 AI

---

**Bon vol, commandant! o7** 🚀
