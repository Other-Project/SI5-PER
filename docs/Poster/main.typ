#import "lib.typ": card, placard
#import "@preview/zebra:0.1.0": datamatrix, qrcode

#set text(lang: "fr")

#show: placard.with(
  title: grid(columns: 2, gutter: 2.5cm, align: horizon,
    [
      //#let _color = rgb("#0380a2").mix(rgb("#00adef"))
      #link("https://github.com/Other-Project/SI5-PER", qrcode("https://github.com/Other-Project/SI5-PER", height: 12cm, options: (ec-level: "m")))
    ],
    
    align(left)[
    #text(size: 100pt)[PER2025-057]\ 
    #text(size: 76pt)[Systèmes collaboratifs pour le contrôle d’atterrissage d’un nano-drone sur plateforme mobile]\
    #text(size: 48pt, weight: "medium")[Encadrement: Gérald ROCHER]
  ]),
  authors: (
    [Komi Jean Paul ASSIMPAH\ komi-jean-paul.assimpah\@etu.univ-cotedazur.fr], 
    [Alban FALCOZ\ alban.falcoz\@etu.univ-cotedazur.fr], 
    [Evan GALLI\ evan.galli\@etu.univ-cotedazur.fr], 
    [Alexandre GRIPARI\ alexandre.gripari\@etu.univ-cotedazur.fr]
  ),
  paper: "a0",
  scaling: 1.25,
  margin: (top: 3cm),
  //scheme: "dark",
  fonts: (
    title: "SF Pro Rounded",
    card: "Monaspace Neon NF",
    headings: "SF Pro Rounded",
    authors: "Monaspace Neon NF"
  ),
  footer: grid(columns: (1fr, 1fr), align: (left + horizon, right + horizon),
    image("uca.png", height: 5cm),
    image("polytech.svg", height: 5cm)
  )
)

#show circle: box

#card(title: "")[
  #figure(
    caption: [
      Séquence d’atterrissage du drone autonome sur plateforme mobile
    ],
    grid(columns: 2, gutter: 2cm, align: left + horizon,
    image("timeline.png"),
    [
      #circle("1", inset: 1pt) Réception de la commande d'atterrissage\
      #circle("2", inset: 1pt) Calcul du vecteur distance entre les robots\
      #circle("3", inset: 1pt) Vol contrôlé par une IA (entraînée par renforcement)\
      #circle("4", inset: 1pt) Coupure des moteurs à quelques\ centimètres de la plateforme (pour éviter l'effet de sol)\
      #circle("5", inset: 1pt) Atterrissage réussi
    ])
  )
]

#grid(
  columns: 2, 
  gutter: 1em,

  card(title: "Abstract")[
    #lorem(55)
  
  ], 
  
  card(title: "Problème")[
    #lorem(20)
  ],
  
  card(title: "Methodologie")[
    #lorem(40)
  ],
  
  card(title: "Solution")[
    #lorem(100)
  ],
  
  card(title: "Perspectives")[
    #lorem(20)
  ]

)
