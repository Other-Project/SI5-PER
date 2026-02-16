#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "../lib.typ": _default-themes

#let _node(pos, label, tint, id, ..args) = node(pos, label, name: id, width: 12em,  ..args)
#let _edge(from, to, tint, mark: "-|>", ..args) = edge(from, to, mark, ..args)
#let _edge_txt(label, tint, ..args) = text(fill: tint.darken(30%), label, ..args)

#let fill_color = _default-themes.light.paper-fill.saturate(50%).mix(black)
#diagram(
  spacing: (35mm, 10mm),
  node-inset: 20pt,
  node-fill: fill_color.lighten(90%),
  node-stroke: fill_color + 2pt,
  edge-stroke: fill_color + 2pt,
  node-corner-radius: 10pt,
  
  _node((0, 0.5), [Vélocité linéaire du drone\ (3 dimensions)], fill_color, <in_vel_lin>),
  _node((0, 1), [Rotation du drone\ (4 dimensions)], fill_color, <in_ang>),
  _node((0, 1.5), [Distance à la cible\ (3 dimensions)], fill_color, <in_distance>),
  
  _edge(<in_vel_lin.east>, <model>, black),
  _edge(<in_ang.east>, <model>, black),
  _edge(<in_distance.east>, <model>, black),
  
  _node((1, 1), [Modèle IA 
  
  MLP 
  
  [256, 128, 64]], fill_color, <model>, height: 12em, width: 7em),

  _edge(<model>, <out_vel_lin.west>, black),
  _edge(<model>, <out_vel_ang.west>, black),
  
  _node((2, 0.5), [Vélocité linéaire\ (3 dimensions)], fill_color, <out_vel_lin>),
  _node((2, 1.5), [Vélocité angulaire\ (1 dimension)], fill_color, <out_vel_ang>),
)
