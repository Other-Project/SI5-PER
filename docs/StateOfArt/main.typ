#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.8": *

#set text(lang:"fr", font: "Exo 2")
#set page(footer: context [
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [PER2025-057],
      counter(page).display("1/1", both: true)
    )
  ])
#show strong: set text(weight: "light")
#show: codly-init
#codly(zebra-fill: none, number-format: none, display-name: false)

#grid(columns: (1fr, 1fr), align: (left + horizon, right + horizon),
  image("uca.png", height: 1.5cm),
  image("polytech.svg", height: 1.6cm)
)

#v(15pt)

#align(center, text(size: 18pt, weight: "medium", style: "oblique")[
  État de l'art
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

#show heading: set heading(numbering: none, outlined: false)

= Avant-propos

Des outils d’intelligence artificielle ont été utilisés pour la formulation des phrases de ce document et pour la sélection des publications présentées.

= Table des matières

#outline(title: none, depth: 2)

#pagebreak()
#show heading: set heading(numbering: "I.1.", outlined: true)

#include "content.typ"

#pagebreak()

= Bibliographie

#bibliography("bib.bib", title: none, style: "ieee", full: true)
