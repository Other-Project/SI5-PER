#set text(lang:"fr", font: "Exo 2")
#set page(footer: context [
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [PER2025-057],
      counter(page).display("1/1", both: true)
    )
  ])
#show heading.where(level: 1): set heading(numbering: "I.")
#show strong: set text(weight: "light")

#grid(columns: (1fr, 1fr), align: (left + horizon, right + horizon),
  image("uca.png", height: 1.5cm),
  image("polytech.svg", height: 1.6cm)
)

#v(15pt)

#align(center, text(lang: "en", size: 18pt, weight: "medium", style: "oblique")[
  Description of Work
])

#v(15pt)

#box(fill: gray.lighten(85%), width: 100%, radius: 0.25cm, pad(x: 0.5cm, y: 0.5cm)[
  #text(size: 20pt, weight: "bold")[PER2025-057 - Développement]
  #linebreak()
  #par(justify: true, text(size: 14pt, weight: "medium")[Systèmes collaboratifs pour le contrôle d'atterrissage d'un nano-drone sur plateforme mobile])
  
  #grid(
    columns: (auto, 1fr),
    inset: 0.25cm,
    text(weight: "medium")[Étudiants:],
    [
      Komi Jean Paul ASSIMPAH (SI5 IoT-CPS),#linebreak()
      Alban FALCOZ (SI5 IA-ID),#linebreak()
      Evan GALLI (SI5 IoT-CPS),#linebreak()
      Alexandre GRIPARI (SI5 IA-ID)
    ],
    
    text(weight: "medium")[Encadrant:], 
    [Gérald ROCHER]
  )
])

#v(15pt)

= Résumé exécutif

Ce projet vise à concevoir un système collaboratif permettant à un nano-drone de type Crazyflie 2.1+ d’atterrir de manière autonome sur une plateforme mobile de type Waveshare AlphaBot2. 

L’objectif est de développer, sous l’environnement ROS 2 Jazzy, un ensemble de modules logiciels assurant la communication et la coordination entre le drone et la plateforme afin d’obtenir un atterrissage précis et sûr, même en mouvement.

Le drone sera équipé de capteurs embarqués (Flow Deck v2 pour estimer la vitesse et la hauteur), tandis que la plateforme mobile disposera potentiellement d’une caméra horizontale capable de suivre la position du drone. Ces informations seront combinées pour définir en temps réel la trajectoire du drone en rapport avec la plateforme.

La stratégie de guidage sera apprise à l’aide d’algorithmes d’apprentissage par renforcement profond (Deep Reinforcement Learning) dans un environnement de simulation avancé (NVIDIA IsaacSim couplé à IsaacLab). Les performances seront ensuite évaluées dans Gazebo afin d’étudier le transfert des modèles entre différents simulateurs (sim2sim), puis sur les systèmes réels pour analyser les écarts entre la simulation et la réalité (sim2real).

Les résultats attendus incluent la mise en œuvre complète d’une architecture collaborative sous ROS 2, la création d’environnements de simulation réalistes et le développement d’une méthode d’apprentissage robuste pour le guidage et l’atterrissage autonome.

= Description du projet

== Contexte technologique

- Le Crazyflie 2.1+, un nano-drone open-source et modulaire de 29 g, utilisé pour la recherche en robotique embarquée. Équipé du Flow Deck v2 et du Multi-ranger Deck, il peut estimer son mouvement et détecter les obstacles dans plusieurs directions.

- L’AlphaBot2, un robot mobile compact à deux roues motrices. Il intégrera, si besoin, une caméra. Sa commande est assurée par une Raspberry Pi, offrant une grande flexibilité pour le développement sous ROS 2.

- ROS 2 (Jazzy), un middleware open-source dédié à la robotique, facilitant la communication et la coordination entre les différents composants logiciels et matériels des deux plateformes.

- NVIDIA IsaacSim / IsaacLab, des environnements de simulation permettent de modéliser avec précision la physique des robots et d’entraîner des modèles de contrôle grâce à l’apprentissage par renforcement profond, en exploitant la puissance de calcul des GPU.

- Gazebo, un simulateur robotique open-source utilisé pour valider les modèles et tester leur comportement dans un environnement virtuel avant le déploiement réel.

- RViz, un outil de visualisation 3D intégré à ROS 2, permettant de suivre en temps réel les trajectoires, les capteurs et l’état des robots.


== Motivations

- Développer un système collaboratif entre un nano-drone et une plateforme mobile pour réaliser un atterrissage autonome.

- Concevoir et intégrer sous ROS 2 les modules de guidage, perception et communication nécessaires au guidage précis.

- Apprendre et tester une stratégie de guidage collaborative dans un environnement simulé (IsaacSim, Gazebo) avant son déploiement réel.

- Étudier le transfert des comportements entre simulation et réalité afin de réduire le reality gap.

- Contribuer à la recherche en robotique autonome et fournir une plateforme expérimentale pour des applications futures (coopération multi-robots, navigation autonome, etc.).

== Objectifs à atteindre

=== Objectif principal

Développer, sous ROS 2 Jazzy, un système de contrôle collaboratif permettant l'atterrissage autonome du Crazyflie 2.1+ sur la plateforme mobile AlphaBot2. La stratégie de guidage sera apprise par renforcement profond (Deep RL) dans l'environnement NVIDIA IsaacSim couplé à IsaacLab.

#pagebreak()

=== Objectifs secondaires

- *Plateforme en mouvement* : L’objectif est de prendre en compte la dynamique de l’AlphaBot2 afin de maintenir une coordination stable avec le drone durant toute la phase d’atterrissage. Cela implique de concevoir un modèle capable d’adapter en temps réel la trajectoire du drone aux changements de vitesse et de direction de la plateforme mobile.
- *Edge computing embarqué* : Une partie du traitement des données pourrait être déployée directement sur la plateforme mobile pour réduire la latence de communication et ainsi accélérer la prise de décision et assurer une meilleure synchronisation entre le drone et l’AlphaBot2.
- *Évitement d’obstacles* : Ajouter au système la capacité de détecter tout obstacle potentiel sur la trajectoire d’approche du drone grâce aux capteurs embarqués pour  adapter automatiquement son plan de vol afin de contourner l’obstacle sans compromettre la stabilité ni la précision de l’atterrissage.
- *Gestion de la distance initiale* : Prévoir une stratégie permettant au drone de localiser et rejoindre la plateforme mobile lorsqu’ils sont initialement éloignés.

== Risques identifiés (et contre-mesures)

=== 1. Complexité du Sim2Real

Le transfert des modèles appris en simulation vers le matériel réel est un défi majeur compte tenu de l'ensemble des événements imprévus dans la réalité qui ne peuvent pas être appris en simulation.

*Contre-mesure *: L'accent sera mis sur l'analyse et la compréhension des déviations (pourquoi ça ne marche pas).

=== 2. Écart entre l’odométrie calculée et la position réelle de l’AlphaBot2

L’odométrie de la plateforme (estimation de la position) sera basée sur la rotation des roues. Cependant, la position estimée par l’odométrie peut avec le temps, diverger significativement de la position réelle, ce qui affecte la précision de la trajectoire du drone et la qualité de la coordination entre les deux systèmes.

*Contre-mesure :* La caméra embarquée sur la plateforme permettra de recalibrer la position estimée à chaque détection du drone, compensant ainsi les erreurs cumulées d’odométrie

=== 3. Effet de sol et mouvement de la plateforme pendant l’atterrissage

Le flux d’air généré par le drone lorsqu’il vole très près d'une surface crée un effet de sol, qui modifie la portance et peut déséquilibrer l’appareil, surtout pour les nano-drones en raison de leur faible masse. Il est alors courant de couper net les moteurs à une hauteur fixe.

Cependant, si la plateforme d’atterrissage est en mouvement, cette méthode devient problématique puisque couper les moteurs à une hauteur fixe peut réduire la précision et faire manquer la plateforme.

*Contre-mesure :* Ajouter des ouvertures ou trous sur la surface de la plateforme pour dissiper la surpression d’air et limiter l’effet de sol.
Ou encore, fournir au drone la vitesse et la direction de la plateforme afin qu’il puisse prédire sa trajectoire et ajuster la sienne pour se positionner en amont.

== Scenarios

== Scénario 1 : Test de validation en environnement contrôlé

==== Contexte d'utilisation
Un ingénieur en robotique ou chercheur souhaite démontrer la faisabilité technique du système collaboratif avant de l'intégrer dans des applications plus complexes. Il dispose d'un espace intérieur sécurisé (laboratoire, gymnase) et veut vérifier que le drone peut effectivement atterrir sur la plateforme mobile en mouvement.

==== Déroulement

1. L'utilisateur démarre le système ROS 2 sur l'AlphaBot2 et initialise le Crazyflie 2.1+
2. Via une interface de commande, il programme une trajectoire circulaire simple pour l'AlphaBot2
3. Le drone décolle et se stabilise à une hauteur de 1.5m au-dessus de la zone
4. L'utilisateur lance la commande d'atterrissage autonome
5. Le système collaboratif s'active : la caméra de l'AlphaBot2 détecte le drone, calcule sa position relative et transmet cette information
6. Le drone ajuste sa trajectoire en temps réel en fonction du mouvement de la plateforme
7. L'atterrissage s'effectue sur la surface de l'AlphaBot2
8. L'utilisateur consulte les logs ROS et visualise la trajectoire dans RViz pour analyser les performances

==== Critères d'acceptation
- Le taux de réussite d'atterrissage doit être supérieur à 85% sur 20 tentatives consécutives
- La précision de positionnement à l'atterrissage est inférieure à 1 cm du centre de la plateforme
- Aucune collision ou perte de contrôle n'est observée durant la manœuvre
- Les données de télémétrie (position, vitesse, commandes) sont correctement enregistrées et exploitables pour l'analyse

== Scénario 2 : Récupération d'urgence avec évitement d'obstacles

==== Contexte d'utilisation
Une équipe de maintenance technique utilise le drone pour effectuer une mission d'inspection dans une zone encombrée (présence d'étagères, de machines, de câbles suspendus). 
L'AlphaBot2 sert de plateforme de récupération mobile pouvant naviguer dans l'environnement encombré jusqu'à proximité du drone.

==== Déroulement
1. À la fin de sa mission d'inspection, le drone se positionne en vol stationnaire à 2 m de hauteur en attendant la récupération
2. L'utilisateur envoie l'AlphaBot2 vers la zone via une commande de navigation autonome
3. Une fois à portée, la caméra de l'AlphaBot2 détecte le drone et initialise la phase de guidage collaboratif
4. Le drone commence sa descente en s'alignant progressivement avec la plateforme mobile
5. Durant l'approche, le Multi-ranger Deck du drone détecte une étagère
6. Le système d'évitement d'obstacles ajuste automatiquement la trajectoire du drone pour contourner l'obstacle par le côté
7. L'AlphaBot2 adapte également sa position pour maintenir l'alignement avec le nouveau plan de vol du drone
8. L'atterrissage final s'effectue avec succès malgré la présence d'obstacles environnants
9. L'utilisateur récupère le drone en ramenant l'AlphaBot2 à la station de base

==== Critères d'acceptation
- La trajectoire alternative calculée permet d'éviter l'obstacle tout en convergeant vers la plateforme 
- Le système maintient la coordination entre le drone et la plateforme durant toute la manœuvre d'évitement  
- Les logs permettent de reconstituer la trajectoire complète incluant les points d'évitement 

= Mise en en œuvre

== Liste d'activités à réaliser avant les semaines à plein temps

- Configuration de ROS et d'IsaacSim/IsaacLab
- Entraînement simple d'un drone pour un vol stable (avec la création d'une fonction de récompense adaptée)
- Coordination des deux systèmes dans IsaacSim/Gazebo
- Mise en place des nœuds ROS nécessaires à la captation des données, à l'inférence et au contrôle des dispositifs
- Entraînement du drone sur une plateforme fixe avec initialisation aléatoire, puis sur une plateforme en mouvement

== Listes d’activités prévues durant les semaines à plein temps

- Aboutissement du travail effectué en amont
- Test du drone en situation réelle pour évaluer les écarts du Sim2Real
- Réalisation des objectifs secondaires (évitement d'obstacle, edge computing, etc.) selon le temps restant
 
== Organisation du travail (répartition de l'équipe)

Le travail est organisé entre les 4 membres du groupe selon leurs mineurs :

- Mineur IA-ID : Instanciation de la plateforme mobile dans IsaacSim/Lab, entraînement du modèle DeepRL (fonction de récompense, observations nécessaires) et la vérification Sim2Sim (Gazebo).

- Mineur IoT-CPS : Mise en place de l'architecture ROS 2 (le développement du nœud de calcul de position relative, la mise en place du nœud d'inférence, etc.), et le setup matériel.
