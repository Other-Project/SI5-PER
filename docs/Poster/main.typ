#import "lib.typ": card, placard
#import "@preview/zebra:0.1.0": datamatrix, qrcode
#import "@preview/larrow:1.0.0": *

#set text(lang: "fr")

#let mail(mail, body: none) = text(size: 0.8em, fill: gray.darken(60%), link("mailto:" + mail, if body == none [#mail] else [#body]))
#let legend(num, txt) = {
  show circle: box
  grid(columns: 2, column-gutter: 10pt, circle(align(horizon + center, num), inset: 1pt), txt)
}

#show: placard.with(
  title: grid(columns: 2, gutter: 2.5cm, align: horizon,
    [
      //#let _color = rgb("#0380a2").mix(rgb("#00adef"))
      #link("https://github.com/Other-Project/SI5-PER", qrcode("https://github.com/Other-Project/SI5-PER", height: 10cm, options: (ec-level: "m")))
    ],
    
    align(left)[
    #text(size: 100pt)[PER2025-057]\ 
    #text(size: 76pt)[Systèmes collaboratifs pour le contrôle d’atterrissage d’un nano-drone sur plateforme mobile]
  ]),
  authors: (
    [Komi Jean-Paul ASSIMPAH\ #text(size: 0.9em)[IoT-CPS]\ #mail("komi-jean-paul.assimpah@etu.univ-cotedazur.fr")], 
    [Alban FALCOZ\ #text(size: 0.9em)[IA-ID]\ #mail("alban.falcoz@etu.univ-cotedazur.fr")], 
    [Evan GALLI\ #text(size: 0.9em)[IoT-CPS]\ #mail("evan.galli@etu.univ-cotedazur.fr")], 
    [Alexandre GRIPARI\ #text(size: 0.9em)[IA-ID]\ #mail("alexandre.gripariS@etu.univ-cotedazur.fr")]
  ),
  prof: [Gérald ROCHER - #text(size: 1.25em, mail("gerald.rocher@univ-cotedazur.fr"))],
  paper: "a0",
  scaling: 1.25,
  margin: (top: 3cm),
  //scheme: "dark",
  fonts: (
    title: "Libertinus Serif",
    card: "EB Garamond",
    headings: "Permanent Marker",
    authors: "EB Garamond"
  ),
  footer: grid(columns: (1fr, 1fr), align: (left + horizon, right + horizon),
    image("imgs/uca.png", height: 3cm),
    image("imgs/polytech.svg", height: 3cm)
  )
)

#context {
place(left, dx: 0pt, dy: 10%, 
      curve(
      stroke: (thickness: 5pt, paint: gray, dash: (15pt, 15pt)),
      curve.move((25%, 485pt)),
      curve.line((25%, 550pt)),
      curve.line((25%, 2100pt)),
      curve.line((50%, 2100pt)),
      curve.line((50%, 525pt)),
      curve.line((75%, 525pt)),
      curve.line((75%, 2000pt)),
    )
)

card(title: "Abstract")[
  #figure(
    caption: [
      Séquence d’atterrissage du drone autonome sur plateforme mobile
    ],
    grid(columns: 2, gutter: 2cm, align: left + horizon,
    image("imgs/timeline.png", height: 12cm),
    [
      
      #legend("1", [Déclenchement de la procédure d'approche])
      #legend("2", [Estimation continue de la distance entre le drone et sa cible])
      #legend("3", [Guidage par inférence du modèle neuronal (Deep RL)])
      #legend("4", [Coupure des moteurs à basse altitude (mitigation de l'effet de sol)])
      #legend("5", [Atterrissage finalisé])
    ]),
  )
  \

  #columns(2, text(size: 1.2em)[
    Ce projet porte sur le développement d’un système collaboratif permettant l’atterrissage autonome et précis d’un nano-drone sur une plateforme mobile. Il s’appuie sur une architecture distribuée sous ROS 2 Jazzy assurant la communication et la coordination entre un drone Crazyflie 2.1+ et un robot mobile.
  
    #colbreak()
  
    La stratégie de guidage et d’atterrissage est apprise à l’aide d’algorithmes de Deep Reinforcement Learning, entraînés dans des environnements de simulation réalistes basés sur NVIDIA IsaacSim et IsaacLab. Les modèles obtenus sont ensuite évalués dans Gazebo afin d’analyser le transfert entre simulateurs (sim2sim), puis déployés sur les systèmes réels pour étudier les écarts entre simulation et réalité (sim2real).

    /* - *Communication* drone Crazyflie–plateforme via ROS2 Jazzy
    - Apprentissage du *guidage* et de l’*atterrissage* par Deep RL

    #colbreak()
    - Entraînement massivement *parallèle* avec NVIDIA Isaac Sim / Isaac Lab
    - Évaluation sous *Gazebo* pour analyser le *sim2sim* gap
    - Déploiement réel pour mesurer l’écart simulation–réalité. */
  ])
]

grid(
  columns: (1fr, 1.4fr),
  gutter: 2em,
  [
    #card(title: "Problématique")[
      Apprentissage en simulateur de séquences d'atterrissage pour un drone autonome sur cible mobile\
      => Sim2Real : Quid de l'écart entre simulation et réalité
      (modélisation imparfaite, dynamiques divergentes, bruit capteurs)\
    ]
  
    #card(title: "Methodologie")[
      #figure(
        caption: [Workflow de travail],
        include("figs/methodo.typ")
      )
  
      #v(0.5em)
      
      #figure(
        caption: [Entrées et sorties du modèle],
        include("figs/model.typ")
      )
    ]
  
    #card(title: "Transfert Sim-to-Sim", [
      - Bridge Isaac - ROS 
      - Fonctionnement indépendant par exécution du modèle en *.onnx*
    ])
  ],
  [
    #card(title: "Apprentissage par renforcement profond")[
      - Minimisation de la distance entre le drone et la plateforme.
      
      - Régulation de la vitesse d'approche (pénalisation des vélocités excessives).
      
      - Respect des contraintes d'inclinaison et de l'altitude de sécurité.
      
      - 4096 environnement en parallèle
      
      - RSL-RL (PPO)
    
      #figure(
        caption: [ Étapes du Curriculum ],
        alt: "
          Le *Curriculum Learning * consiste à segmenter l'entraînement en niveaux de difficulté croissante. Cela guide l'agent vers la solution optimale sans qu'il ne se perde dans des minimums locaux.
        - Phase 1 : *Stabilisation* (Vol stationnaire, maintien d'altitude).
        - Phase 2 : *Cible Statique* (Atterrissage sur plateforme fixe, positions aléatoires).
        - Phase 3 : *Cible Mobile* (Introduction progressive de la vitesse et de l'accélération de la plateforme). 
        ",
        [
          #grid(columns: (1fr, 1fr, 1fr), gutter: 1cm, align: left + horizon,
            align(center)[
              #image("imgs/curriculum_learning_1.png", height: 5cm)
              #legend("1", [Atterrissage sur\ cible statique])
            ],
            align(center)[
              #image("imgs/curriculum_learning_2.png", height: 5cm)
              #legend("2", [Déplacement jusqu'à\ cible statique et atterrissage])
            ],
            align(center)[
              #image("imgs/curriculum_learning_3.png", height: 5cm)
              #legend("3", [Déplacement jusqu'à cible en mouvement et atterrissage])
            ]
          )
          #v(1em)
        ]
      )
    ]
  
    #card(title: "Résultats", grid(columns: (0.8fr, 1.5fr), gutter: 1em, 
      figure(image("imgs/monitoring.png", width:97%), caption: [Parcours du drone dans \ différentes simulateurs]),
      align(horizon + center, box(fill: white, width: 100%, height: 13.5cm, inset: 0.2cm, align(horizon, text(size: 1.1em, table(
        columns: (auto, 1fr, 1fr, 1fr),
        inset: 12pt,
        align: center + horizon,
        fill: (col, row) => if row == 0 { gray.lighten(80%) } else if calc.even(row) { gray.lighten(95%) } else { none },
        
        [*Métrique*], [*Isaac (Réf)*], [*Gazebo (Gap)*], [*Webots (Gap)*],
        
        [Erreur Moyenne de Distance], [*0.26 m*], [0.52 m \ (+0.26)], [1.03 m \ (+0.77) ],
        [Écart-type d'altitude], [*0.40 m*], [0.42 m \ (+0.02)], [0.66 m \ (+0.26) ],
        [Vitesse Moyenne], [*0.20 m/s*], [0.04 m/s \ (-0.16)], [0.21 m/s \ (+0.01) ],
        [Écart-type Vitesse], [*0.35 m/s*], [0.04 m/s \ (-0.31)], [0.20 m/s \ (-0.15)]
      )))))
    ))
  
    #card([
      #text(font: "Permanent Marker", fill: rgb("#1a1a1a"), size: 35pt, weight: "semibold",  smallcaps(("Perspectives")))
      #h(0.5em)
      Passer en Manager-Based sur Isaac, Domain Randomization, LSTM 
    ])
  ]
)


  /*card([
    #text(font: "Permanent Marker", fill:  rgb("#1a1a1a"), size: 35pt, weight: "semibold",  smallcaps([Perspectives]))
    #h(0.5em)
    Passer en Manager-Based sur Isaac, Domain Randomization, LSTM 
  ])*/
<<<<<<< HEAD
}
=======
}
>>>>>>> origin/sim2sim-monitoring
