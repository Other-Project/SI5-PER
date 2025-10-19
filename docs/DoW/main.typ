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

#grid(columns: (1fr, 1fr), align: (left + horizon, right + horizon),
  image("uca.png", height: 1.5cm),
  image("polytech.svg", height: 1.6cm)
)

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

(20 lignes, 300 mots max)

[Insérer ici un résumé d’un maximum de 20 lignes décrivant succinctement l’objectif de votre projet et les résultats que vous espérez fournir. Ce résumé doit être clair, concis et compréhensible par un non-spécialiste.] 

= Description du projet

 (quel#text(fill: red)[que]s paragraphes, utilisez des bulles)

== Contexte technologique

[Contexte technologique dans lequel se situe le projet]
- Contexte techno 1
- Contexte techno 2
- …

== Motivations

[Quels sont les problèmes à résoudre ? Quel pan de la science va avancer grâce à lui ? Quel#text(fill: red)[le] utilité a le projet ? 
- Motivation 1…
- Motivation 2… 
- …


== Objectifs à atteindre

[Listez les objectifs que vous comptez atteindre, que ce soit des résultats de recherche ou des livrables.]

- Objectif principal
- Objectif secondaire 1…
- Objectif secondaire 2…
- …

== Risques identifiés (et contre-mesures)

[Listez les risques associés à l’obtention des résultats escomptés, et décri#strike[r]#text(fill: red)[v]ez comment vous comptez les surmonter.]
- Risque 1
- Risque 2
- …

== Scenarios

[Décrivez 2 à 3 scénarios d’utilisation de votre projet. Ces scénarios doivent être montrés du point de vue des utilisateurs du système que vous construirez. Pour chaque scénario, vous soulignerez les critères d’acceptation, qui servent à prouver que le système permet l’exécution de ces scénarios. Maximum deux pages.]

= Mise en en œuvre
(quel#text(fill: red)[que]s paragraphes, utilisez des bulles)

Liste d'activités déjà réalisé#text(fill: red)[e]s avant les semaines à plein temps
Listes d’activités prévues pour chaque semaine à plein temps
Organisation du travail (répartition de l'équipe)
