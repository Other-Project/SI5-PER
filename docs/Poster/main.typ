#import "lib.typ": card, placard
#import "@preview/zebra:0.1.0": datamatrix, qrcode
#import "@preview/larrow:1.0.0": *
#import "@preview/lilaq:0.5.0" as lq

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
    [Alexandre GRIPARI\ #text(size: 0.9em)[IA-ID]\ #mail("alexandre.gripari@etu.univ-cotedazur.fr")]
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
      curve.line((25%, 2200pt)),
      curve.line((50%, 2200pt)),
      curve.line((50%, 512.5pt)),
      curve.line((75%, 512.5pt)),
      curve.line((75%, 2125pt)),
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
  
    La stratégie de guidage et d’atterrissage est apprise à l’aide d’algorithmes de _Deep Reinforcement Learning_, entraînés dans des environnements de simulation réalistes basés sur NVIDIA IsaacSim et IsaacLab. Les modèles obtenus sont ensuite évalués dans Gazebo afin d’analyser le transfert entre simulateurs (_Sim2Sim_), puis déployés sur les systèmes réels pour étudier les écarts entre simulation et réalité (_Sim2Real_).

    /* - *Communication* drone Crazyflie–plateforme via ROS2 Jazzy
    - Apprentissage du *guidage* et de l’*atterrissage* par Deep RL

    #colbreak()
    - Entraînement massivement *parallèle* avec NVIDIA Isaac Sim / Isaac Lab
    - Évaluation sous *Gazebo* pour analyser le *sim2sim* gap
    - Déploiement réel pour mesurer l’écart simulation–réalité. */
  ])
]

block(columns(2, gutter: 2em, [
  #card(title: "Problématique")[
  Apprentissage en simulateur de séquences d'atterrissage pour un drone autonome sur cible mobile\
  → Comment réduire l'écart _"Sim2Real"_ entre simulation et réalité
    (modélisation imparfaite,\ dynamiques divergentes, bruit capteurs)
  //=> Estimation relative bruitée\
  //=> Effets aérodynamiques (effet de sol, perturbations)
]

  
  #card(title: "Methodologie")[

    Nous mettons en œuvre une chaîne de validation _Sim2Sim2Real_ pour mieux apprécier le _reality gap_ inhérent à la simulation utilisée pour l'apprentissage.
    
    #figure(
      caption: [Workflow de travail],
      include("figs/methodo.typ")
    )

    Ce flux de travail permet d'entraîner une politique de contrôle définie par les espaces d'observation et d'action ci-dessous.
    
    #figure(
      caption: [Entrées et sorties du modèle],
      include("figs/model.typ")
    )
    
  ]

    #card(title: "Environnement ROS 2", [
      - Conversion de la politique entraînée vers le format standard ONNX pour une inférence autonome
      - Pont avec l'environnement Isaac pour la création d’un espace de validation sim2sim
      - Contrôleur de vol en charge de la gestion des commandes moteurs, des phases de décollage/atterrissage et du maintien des ordres dans les limites physiques
      - Phase de vol libre suivie du déclenchement de la séquence d'atterrissage autonome via la politique entraînée
    ])

#colbreak()
  
  #card(title: "Apprentissage par renforcement profond")[
    - Minimisation de la distance entre le drone et la plateforme
    - Régulation de la vitesse d'approche (pénalisation des vélocités excessives)
    - Respect des contraintes d'inclinaison et de l'altitude de sécurité
    - L'entraînement est réalisé sur 4096 environnements en parallèle via l'algorithme PPO (RSL-RL)
    
    #v(0.5em)

    Pour garantir la convergence, l'apprentissage est séquencé par niveau de difficulté croissante :
  
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
            #image("imgs/curriculum_learning_1.png", height: 8cm)
            #legend("1", [Atterrissage sur\ cible statique])
          ],
          align(center)[
            #box(height: 8cm, image("imgs/curriculum_learning_2.png", width: 100%))
            #legend("2", [Déplacement jusqu'à\ cible statique et atterrissage])
          ],
          align(center)[
            #image("imgs/curriculum_learning_3.png", height: 8cm)
            #legend("3", [Déplacement jusqu'à cible en mouvement et atterrissage])
          ]
        )
        #v(0.5em)
      ]
    )
  ]

    #card(title: "Résultats", grid(columns: (2fr, 3fr), gutter: 2em, align: horizon, 
      figure(image("imgs/monitoring.png", width: 100%), caption: [Parcours du drone selon\ différents simulateurs]),
      /*figure(table(
        columns: (auto, 1fr, 1fr, 1fr),
        inset: (5pt, 10pt),
        align: center + horizon,
        fill: (col, row) => if row == 0 { gray.lighten(80%) } else if calc.even(row) { gray.lighten(95%) } else { none },
        
        [*Métrique*], [*Isaac (Réf)*], [*Gazebo (Gap)*], [*Webots (Gap)*],
        
        [Altitude Moyenne de Vol ], [*0.26 m*], [0.38 m \ (+0.12)], [0.55 m \ (+0.29) ],
        
        [Écart-type d'altitude], [*0.38 m*], [0.42 m \ (+0.04)], [0.66 m \ (+0.28) ],
        table.cell(colspan: 4)[],
        [Vitesse Moyenne], [*0.4C9 m/s*], [0.24 m/s \ (-0.25)], [0.63 m/s \ (+0.14) ],
        [Écart-type Vitesse], [*0.53 m/s*], [0.21 m/s \ (-0.32)], [0.61 m/s \ (+0.08)]
      ), caption: [Comparaison entre les simulations], kind: image),*/
      {
        
        // IBM
        let gazebo = rgb("#FFB000")
        let isaac = rgb("#785EF0")
        let webots = rgb("#DC267F")

        // Okabe-Ito
        /*let gazebo = rgb("#E69F00")
        let isaac = rgb("#009E73")
        let webots = rgb("#56B4E9")*/

        
        
      grid(rows: 2, gutter: 1em, 
      figure(caption: [Distribution des altitudes entre simulateurs], lq.diagram(
        width: 100%,
        height: 250pt,
        legend: (position: top + left),
        xaxis: none,
        lq.boxplot(
          x: 1,
          lq.load-txt(read("metrics/altitude_isaac.csv"), header: true).Altitude,
          stroke: isaac + 2pt,
          fill: isaac.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Isaac Sim"
        ),
        lq.boxplot(
          x: 2,
          lq.load-txt(read("metrics/altitude_gazebo.csv"), header: true).Altitude,
          stroke: gazebo + 2pt,
          fill: gazebo.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Gazebo"
        ),
        lq.boxplot(
          x: 3,
          lq.load-txt(read("metrics/altitude_webots.csv"), header: true).Altitude,
          stroke: webots + 2pt,
          fill: webots.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Webots"
        )
      )
    ),
    figure(caption: [Distribution des vitesses entre simulateurs], lq.diagram(
        width: 100%,
        height: 200pt,
        xaxis: none,
        legend: (position: top + left),
        lq.boxplot(
          x: 1,
          lq.load-txt(read("metrics/speed_isaac.csv"), header: true).Speed,
          stroke: isaac + 2pt,
          fill: isaac.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Isaac Sim"
        ),
        lq.boxplot(
          x: 2,
          lq.load-txt(read("metrics/speed_gazebo.csv"), header: true).Speed,
          stroke: gazebo + 2pt,
          fill: gazebo.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Gazebo"
        ),
        lq.boxplot(
          x: 3,
          lq.load-txt(read("metrics/speed_webots.csv"), header: true).Speed,
          stroke: webots + 2pt,
          fill: webots.lighten(30%),
          median: black + 2pt,
          outliers: none,
          label: "Webots"
        )
      )
    ))
  }
    ))
  
  #card(gap: 0em, [
    #text(font: "Permanent Marker", fill: rgb("#1a1a1a"), size: 35pt, weight: "semibold",  smallcaps(("Perspectives")))
    #h(0.5em)
    Architecture Manager-Based, Domain Randomization et LSTM
  ])
]))


  /*card([
    #text(font: "Permanent Marker", fill:  rgb("#1a1a1a"), size: 35pt, weight: "semibold",  smallcaps([Perspectives]))
    #h(0.5em)
    Passer en Manager-Based sur Isaac, Domain Randomization, LSTM 
  ])*/
}