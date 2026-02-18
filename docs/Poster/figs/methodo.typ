#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "../lib.typ": _default-themes

#let _node(pos, label, tint, id, ..args) = node(pos, label, name: id, width: 9.5em, height: 6em,  ..args)
#let _edge_txt(label, tint, ..args) = text(fill: tint.darken(30%), label, ..args)

#let fill_color = _default-themes.light.paper-fill.saturate(50%).mix(black)
#diagram(
  spacing: (20mm, 10mm),
  node-inset: 15pt,
  node-fill: fill_color.lighten(90%),
  node-stroke: fill_color + 2pt,
  edge-stroke: fill_color + 2pt,
  node-corner-radius: 10pt,

  
  _node((0, 0), [Entraînement d'un modèle par renforcement  sur IsaacLab/IsaacSim], fill_color, <detect>),
  edge("-|>", bend: -10deg),
  edge("<|-", bend: 10deg),
  _node((1, 0), [Vérification\ du modèle appris\ sur Gazebo], fill_color, <detect>),
  edge("-|>", bend: -10deg),
  edge("<|-", bend: 10deg),
  _node((2, 0), [Déploiement réel], fill_color, <detect>),
)
