=== Deep RL

#{
  show table.cell: set text(size: 8pt)
  
  table(
    columns: 5,
    inset: 6pt,
    table.header(
      [*Critères*],
      [*Amendola @amendola2024drone*],
      [*Azar @azar2021drone*],
      [*Chen @chen2025survey*],
      [*Sönmez @sonmez2024survey*],
    ),

[*Focus principal*],[Apprentissage En Ligne (Online) vs Hors Ligne. Focus sur l'implémentation temps réel.],[Vue d'ensemble RL pour drones. Classification par type (Value/Policy/Actor-Critic).],[Revue généraliste DRL. Focus sur la navigation et le contrôle bas niveau.],[Atterrissage de drones. Focus très spécifique sur cette tâche critique.],
[*Algorithmes comparés*],[Cite PPO, DDPG, TD3. Distingue surtout On-policy (PPO) vs Off-policy (DDPG, TD3).],[Compare les familles : AC (DDPG, TD3) vs Policy-based (PPO).],[Discute beaucoup de DQN (discret) et DDPG (continu).],[Comparaison directe entre DDPG, TD3 et SAC pour la tâche d'atterrissage.],
[*Verdict sur la stabilité*],[Note que les méthodes Off-policy (DDPG) convergent plus lentement et sont plus complexes que les On-policy (PPO).],[Critique envers les Actor-Critic (DDPG/TD3) : qualifiés de "très instables" à l'entraînement. PPO a une variance élevée mais est moins complexe à tuner que les AC.],[Souligne que DDPG nécessite un "Target Network" pour assurer la convergence, mais reste sensible.],[TD3 est explicitement cité comme une amélioration de la stabilité du DDPG (réduit la surestimation des Q-values).],
[*Verdict Sim-to-Real*],[Souligne que l'apprentissage Online est clé pour gérer les perturbations réelles, là où l'Offline (entraîné en simulation) échoue souvent.],[Identifie le "Sim-to-Real" comme un défi majeur futur. Ne donne pas de gagnant clair, mais suggère que la simulation doit être haute-fidélité.],[Mentionne le "Reality Gap" comme limitation majeure empêchant le déploiement direct d'agents entraînés.],[Note que le Sim-to-Real est un "gap" critique non résolu. Cite des succès réels avec TD3 et PPO.],
[*Meilleur compromis (selon le papier)*],[Tend à favoriser les approches capables d'apprendre ou de s'adapter en temps réel (Online) pour compenser les erreurs de modèle.],[Suggère implicitement que les méthodes Actor-Critic (TD3) sont les plus puissantes si bien réglées, malgré l'instabilité.],[Pas de vainqueur définitif, mais met en avant le continu pour le contrôle.],[TD3 semble favorisé par rapport à DDPG pour la robustesse.]
  )
}

#pagebreak()

=== Curriculum

#{
  show table.cell: set text(size: 8pt)
table(
  columns: 6,
  inset: 6pt,
  table.header(
    [*Critères*],
    [*Review evaluation system @electronics12071676*],
    [*Guided RL @esser2022guided*],
    [*CL for RL domains @JMLR:v21:20-212*],
    [*A survey on CL @wang2021survey*],
    [*Automatic CL @portelas2020automaticcurriculumlearningdeep*],
  ),

  [*Problématique*], [Revue méthodologique générale], [Robotique], [Différents domaines : jouets / robotique simulée / robotique réelle / jeux vidéo ], [Aucun domaine particulier], [Robotique et jeux vidéos],
  [*Type de RL*], [Single-Agent / Multi-Agent RL], [Single-Agent et Hierarchical RL], [Single-Agent / Multi-Agent / Hierarchical RL
], [Single-Agent RL et Multi-Task Learning], [Single-Agent / Multi-Agent RL / Multi-Goal RL],
  [*Knowledge Source*], [Expert Knowledge et Learned/Automatic ], [World Knowledge et Expert Knowledge], [Target, Automatic, Domain Experts et Naive Users], [Scientific/Implicit et Expert Knowledge], [Learned/Automatic],
  [*Mécanisme de génération*], [Sample sequencing / Task Generation], [Task Generation et Reward Shaping], [Sample Sequencing /
Task Generation / Co-learning], [ Sample Sequencing et Task Generation], [Initial state / Reward Shaping / Goal Generation / Environment Generation / Opponent Generation
],
  [*Agent de contrôle (Sequencer)*], [Fixed et Adaptive/Closed-loop], [Teacher-Student Curriculum Learning : enseignant choisit les sous-tâches en fonction des progrès de l'élève], [Fixed et Adaptive], [Fixed et Adaptive/Closed-loop], [ Adaptive / Closed-loop],
  [*Métrique de vitesse de convergence*], [Time to threshold], [Sample efficiency ], [Time to threshold et asymptotic performance], [Time to threshold], [Sample Efficiency et asymptotic performance],
  [*Évaluation & Validité*], [Comparaison avec no curriculum et  random curriculum], [Comparaison avec un processus d'entraînement RL standard sans l'intégration de connaissances supplémentaires], [Comparaison avec la performance sans curriculum], [Comparaison avec la performance sans curriculum ], [Comparaison avec la performance sans curriculum],
  [*Gain observé*], [Réduction du temps d'entrainement de 70%], [Impact fort sur l'efficiency et l'efficacité (Effectiveness), mais un impact modéré sur le Sim-to-Real s'il est utilisé seul], [Convergence plus rapide + une meilleure performance sur des tâches trop difficiles pour être apprises from scratch], [Réduction de 70% du temps d'entrainement], [ Les gains sont dépendants du papier cité et ne sont pas comparables entre eux],
)
}

#pagebreak()

=== Sim2Sim

#{
  show table.cell: set text(size: 8pt)
table(
  columns: 5,
  table.header([*Critères*], [*Survey ADR @hanover2024autonomous*], [*NeuroBEM @bauersfeld2021bem*], [*Agilicious @foehn2022agilicious*], [*Digital Twin @liu2022twin*]),
  [*Biais de Perception*], [Flou cinétique, éclairage, bruit ], [N/A], [Changements éclairage, flou visuel ], [Éclairage, occlusions, bruit visuel],
  [*Biais de Dynamique*], [Aérodynamique, traînée, portance], [Aérodynamique complexe, interactions rotors], [Flux d'air, limites physiques], [Écarts cinématiques et dynamiques],
  [*Biais Temporel/Latence*], [Délais système et communication], [Constante temps moteur (33ms)], [Latence commande (35-75ms)], [Décalage synchronisation temporelle],
  [*Approche*], [Sim2Sim (benchmark dataset)], [Sim2Sim], [Variations extrêmes de paramètres en simulation], [Digital Twin (simulation synchronisée avec les paramètres du robot réel)],
  [*Métriques de succès*], [Temps au tour (lap)], [RMSE force et couple], [Erreur moyenne de suivi], [Taux de succès saisie],
  [*Erreur de prédiction multi-étapes*], [Prédiction d'états futurs], [Prédiction du comportement dynamique], [Prédiction d'horizon pour MPC], [N/A],
  [*Zero-shot Transfer*], [Objectif final de robustesse], [Généralisation aux trajectoires invisibles], [Testé en milieux encombrés], [Cœur du transfert proposé],
  [*Comparaison Side-by-Side*], [Benchmarks entre divers algorithmes], [Trajectoires Réel vs Sim], [Erreurs de suivi comparées], [Saisie Réel vs Sim],
  [*Domain Randomization*], [Méthode standard de transfert], [Non utilisé], [Non utilisé], [Cité en travaux connexes],
  [*Modèles Hybrides*], [Physique + Apprentissage automatique], [Théorie BEM + Réseau neurones], [Politique NN + Contrôle], [DRL + Correction par DT],
  [*System Identification*], [Identification via soufflerie], [Banc de test statique], [Réponse à l'échelon (moteurs)], [Importation URDF du réel],
  [*Moteur utilisé*], [Gazebo, Unity, AirSim], [Intégrateur Euler symplectique], [Unity (Flightmare), Gazebo], [V-REP (CoppeliaSim)],
  [*Niveau d'abstraction*], [Images ou vecteurs caractéristiques], [États (vitesse, RPM)], [Vision monoculaire et IMU], [Pixels bruts (cartes hauteur)],
  [*Complexité computationnelle*], [Temps réel embarqué], [Inférence réseau neurones rapide], [Accélération GPU, Linux RT ], [Inférence GPU (travail station)],
)
}

#pagebreak()


=== Transfert Sim2Real

#{
  show table.cell: set text(size: 7pt) 

  table(
    columns: 9,
    align: (col, row) => if col == 0 { left + horizon } else { center + horizon },
    table.header(
      [*Critères*],
      [*Salvato \ @salvato2021crossing*],
      [*Polvara \ @polvara2020sim*],
      [*Kooi \ @kooi2021inclined*],
      [*Malmir \ @malmir2023diarel*],
      [*Wu \ @wu2022two*],
      [*Sangeerth \ @sangeerth2025quantification*],
      [*Coursey \ @coursey2024quantifying*],
      [*Shi \ @shi2023marl*],
    ),
    
    [*Verrou Scientifique* \ (Quel problème ?)],
    [Classification globale des erreurs Sim2Real.],
    [Gap Visuel \ (Transférer la vision caméra).],
    [Gap Dynamique \ (Vol haute précision).],
    [Gap Temporel \ (Latence & Délais variables).],
    [Perturbations \ (Effet de sol).],
    [Sûreté \ (Garantie de non-crash).],
    [Diagnostic \ (Cause physique échec).],
    [Non-Stationnarité \ (Multi-agents).],

    [*Approche Technique* \ (Quelle solution ?)],
    [Taxonomie \ (Survey).],
    [Domain Rand. \ (Textures) + SDQN.],
    [System ID \ (Délais moteurs 33ms).],
    [State Augmentation \ (Historique actions).],
    [Two-Policy \ (Nav + Atterrissage).],
    [Neural Gap Function \ (Apprentissage erreur).],
    [Divergence J-S \ (Statistique).],
    [R-MADDPG \ (Réseaux RNN/LSTM).],

    [*Type d'Entrée* \ (Observation)],
    [N/A],
    [Images \ (Pixels caméra).],
    [États \ (Vitesse, IMU).],
    [États + Historique \ (Buffer).],
    [États \ (Pos. relative).],
    [États \ (Pos., Vitesse).],
    [Logs de Vol \ (Post-mortem).],
    [États Partagés \ (Comm. Multi-Robots).],

    [*Randomisation* \ (Hypothèse)],
    [Discutée.],
    [Centrale \ (Lumière, Sol).],
    [Rejetée \ (Modèle fidèle).],
    [Partielle \ (Perturbations).],
    [Auxiliaire.],
    [Non utilisée.],
    [Non utilisée.],
    [Centrale \ (Scénarios).],

    [*Cible Matérielle* \ (Contexte)],
    [Robots génériques.],
    [Quadrotor \ + Caméra embarquée.],
    [Nano-drone \ (Crazyflie 2.1).],
    [Robots pilotés \ ROS / Wifi.],
    [Drone en phase \ d'atterrissage.],
    [Systèmes critiques \ autonomes.],
    [Analyseurs de \ données de vol.],
    [Multi-Agents \ (UAV + UGV).],

    [*Validation & Gain* \ (métriques)],
    [ N/A ],
    [Succès réel : \ 28% -> 91% (avec DR).],
    [Vol réussi \ sans randomisation.],
    [Stable malgré \ délais > 40ms.],
    [Réduction erreur \ position finale.],
    [Bornes math. \ (Lipschitz).],
    [Identification \ précise (ex: Yaw).],
    [Réduction erreur \ suivi collaboratif.],
  )
}