# 🎥 Enregistrements Vidéo des Simulations — AMR RAIA 4.0

Ce dossier regroupe les enregistrements vidéo de simulation de l'AMR RAIA 4.0 dans son atelier industriel CMS (**ISET Bizerte — Projet HMIDA / Rapport RAIA 01.26**).

---

## 📹 Contenu de la Démonstration Vidéo (`raia_amr_simulation.mp4`)

La vidéo capture l'écran unifié sous **WSLg** (Gazebo 11 ODE + RViz2 Nav2) et valide l'intégralité du cahier des charges :

1. **État Initial à la Borne MiR Charge (Quai Sud : $x=0.0, y=-3.80$)** :
   - Robot amarré aux plots 24V DC, en veille, batterie à 100%.
   - Réception du signal d'appel opérateur (`/operator_call` ou bouton `/line_call_button`).
   - Déconnexion automatique des plots de charge et départ en mission.

2. **Étape 1 : Évitement Piéton Mobile & Avertisseur Sonore (Vers ST1 Sérigraphie)** :
   - Un opérateur piéton (`human_worker_pedestrian` avec tenue haute visibilité et casque) traverse l'allée centrale de transit ($y = -1.60\text{ m}$).
   - Le LiDAR 2D de l'AMR détecte le travailleur dans son gabarit de sécurité ISO 3691-4 ($d = 1.02\text{ m}$).
   - **Arrêt d'urgence automatique** : consigne moteur `cmd_vel = 0`.
   - **Avertisseur sonore d'alerte** : diffusion de la mélodie industrielle (`amr_safety_melody.wav`) via le transducteur acoustique du robot.
   - Dès que le piéton a traversé et dégagé le couloir, l'alarme sonore s'éteint et l'AMR reprend sa marche vers ST1.
   - Arrivée à ST1 ($x=1.80, y=0.65$) : simulation du chargement automatique de la carte PCB.

3. **Étape 2 : Évitement Autonome d'Obstacle Fixe (Vers ST2 Quai Convoyeur)** :
   - Un chariot de maintenance technique (`chariot_maintenance_fixe`) est placé au carrefour central ($x=0.0, y=0.65$), bloquant la ligne droite entre ST1 et ST2.
   - Les costmaps Nav2 (locale et globale) intègrent le chariot en temps réel via le balayage LiDAR.
   - Le planificateur global `Navfn` et le contrôleur local `RPPC` calculent une **trajectoire de déviation autonome** qui contourne le chariot par le Nord ($y \approx 1.25\text{ m}$), laissant plus de $0.60\text{ m}$ de marge de sécurité.
   - Arrivée à ST2 ($x=-1.80, y=0.65$, écart $15.3\text{ cm}$) : simulation de la dépose de la carte PCB sur les rouleaux du convoyeur.

4. **Étape 3 : Retour Autonome & Amarrage MiR Charge (ST0)** :
   - Acheminement retour vers le Quai Sud.
   - Réalignement précis face à la borne MiR Charge (écart $18.4\text{ cm}$, cap $15.1^\circ$).
   - Connexion automatique aux broches de recharge 24V DC.

---

## 🎬 Comment rejouer ou relancer l'enregistrement ?

Pour lancer une nouvelle session d'enregistrement vidéo automatique :

```bash
cd ~/ros2_ws/src/raia_amr_description
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
bash record_and_run_simulation.sh
```

La vidéo MP4 est générée directement dans ce dossier :
`simulations/raia_amr_simulation.mp4`
