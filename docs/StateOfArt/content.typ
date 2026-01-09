
#set table(
      inset: 6pt,
    stroke: 0.5pt + luma(200),
  
    fill: (x, y) => if y == 0 or x == 0 { gray.lighten(70%) },
)

= Contexte

L'automatisation complète des missions de drones nécessite de maîtriser des phases critiques, dont l'interaction physique ou l'atterrissage sur des supports mobiles constitue l'un des défis les plus ardus. La capacité d'un drone à se synchroniser avec une cible en mouvement est devenue un enjeu majeur pour des applications allant de la surveillance maritime à la logistique militaire.
Traditionnellement, le contrôle de telles interactions repose sur des méthodes analytiques classiques. Cependant, la complexité de la dynamique de vol, couplée aux perturbations aérodynamiques comme l'effet de sol et à la nature imprévisible des mouvements de la plateforme cible, met en défaut la rigidité de ces approches. Pour pallier ces limites, l'apprentissage par renforcement profond (DRL) émerge comme une solution privilégiée. En permettant à l'agent d'apprendre une politique de contrôle directement à partir de l'expérience, le DRL offre la flexibilité nécessaire pour gérer des scénarios non linéaires et dynamiques.

Toutefois, l'application du DRL à la robotique réelle se heurte à une contrainte fondamentale : la nécessité de collecter une quantité massive de données d'entraînement, souvent dangereuse ou impraticable sur des systèmes physiques fragiles. L'entraînement s'effectue donc majoritairement en simulation (par exemple sous IsaacSim ou Gazebo). Cette dichotomie entre l'environnement d'apprentissage virtuel et le monde physique engendre un écart de performance, qualifié de « Reality Gap ».

Ce décalage se manifeste par des divergences de dynamique, de perception et de latence qui peuvent rendre inopérantes les politiques apprises une fois déployées sur le réel.

= Questionnements

Dès lors, l'enjeu ne se limite pas à la sélection d'un algorithme, mais s'étend à la validation d'une méthodologie complète de transfert. 
Pour répondre à ce défi, nous structurons notre analyse autour des interrogations suivantes :

- Quelle combinaison d'architecture algorithmique et de stratégie d'entraînement maximise la performance #footnote[Efficacité de l’échantillonnage, stabilité de l’entraînement, complexité de l'algorithme, résultat obtenu sur les drones.] en Deep Reinforcement Learning ?
  - Parmi les algorithmes couramment utilisés (PPO, TD3, DDPG), lequel offre le meilleur compromis entre stabilité d'entraînement et taux de succès lors du transfert vers le réel ? 
  - Quel est l'impact de l'apprentissage par curriculum sur la vitesse de convergence et la robustesse des politiques en DRL ?
- Quelles techniques permettent de réduire le Reality Gap ?
  - Comment quantifier les biais de simulation et évaluer la fidélité d'un environnement virtuel en amont du déploiement physique ?
  - Quelles sont les approches prédominantes permettant d'assurer la robustesse du transfert Sim2Real pour les systèmes robotiques aériens ?

#pagebreak()

= Méthodologie de sélection des publications

== Outils utilisés

Notre recherche bibliographique s'est appuyée sur les bases de données suivantes :

- #link("https://scholar.google.com/")[Google Scholar] : pour la recherche de publications
- #link("https://ieeexplore.ieee.org/")[IEEE Xplore]: pour la recherche de publications
- #link("https://elicit.com/")[Elicit] : pour la sélection des publications

== Requêtes

Les requêtes suivantes ont été utilisées sur Google Scholar pour obtenir nos publications.

#let question(content) = text(style: "italic", fill: black.lighten(20%), content)

- #question["Parmi les algorithmes couramment utilisés (PPO, TD3, DDPG), lequel offre le meilleur compromis entre stabilité d'entraînement et taux de succès lors du transfert vers le réel ?"] :
  ```sql
  ("PPO" OR "TD3" OR "DDPG") AND "deep reinforcement learning" AND ("UAV" OR "quadrotor" OR "crazyflie") AND "landing"
  ```  
  ```sql
  ("survey" OR "systematic review") AND ("PPO" OR "TD3" OR "DDPG") AND "deep reinforcement learning" AND ("UAV" OR "quadrotor" OR "crazyflie") AND "comparison"
  ```
  
- #question["Quel est l'impact de l'apprentissage par curriculum sur la vitesse de convergence et la robustesse des politiques en DRL ?"] :
  ```sql
  "Curriculum Learning" AND "Deep Reinforcement Learning" AND ("convergence speed" OR "sample efficiency") AND "robustness" and "uav"
  ```
  

- #question["Comment quantifier les biais de simulation et évaluer la fidélité d'un environnement virtuel en amont du déploiement physique ?"] :
  ```sql
  ("sim-to-sim" OR "fidelity transfer" OR "digital twin" OR "dynamics adaptation") AND ("quadrotor" OR "UAV" OR "drone") 
  ```
  
- #question["Quelles sont les approches prédominantes permettant d'assurer la robustesse du transfert Sim2Real pour les systèmes robotiques aériens ?"] :
  ```sql
  ("Sim2Real" OR "Sim-to-Real" OR "reality gap" OR "simulation-to-reality") 
AND ("domain randomization" OR "dynamics randomization" OR "domain adaptation" OR "meta-learning" OR "robustness") 
AND ("UAV" OR "quadrotor" OR "drone" OR "aerial robot")
  ```

  ```sql
("sim2real" OR "sim-to-real" OR "reality gap") 
AND ("quadrotor" OR "quadcopter" OR "UAV" OR "drone")
AND ("survey" OR "review" OR "comparison" OR "benchmark" OR "comparative")
  ```

  ```sql
  ("UAV" OR "quadrotor" OR "drone") AND ("sim2real" OR "transfer" OR "reality gap")
  ```


== Critères d'inclusion et d'exclusion

La constitution du corpus documentaire repose sur un ensemble de critères d'inclusion et d'exclusion, visant à garantir tant la pertinence thématique que la qualité scientifique des sources mobilisées.

=== Critères thématiques et temporels

Afin de refléter l'état de l'art le plus actuel dans un domaine à évolution rapide, la sélection s'est concentrée sur des publications récentes (postérieures à 2020) et rédigées exclusivement en langue anglaise. Le périmètre de recherche a été restreint aux travaux appliquant explicitement le Deep Reinforcement Learning (DRL) et en favorisant, dans la mesure du possible, les vecteurs aériens de type UAV.

=== Hiérarchisation et typologie des sources

Une priorité analytique a été accordée aux articles de synthèse (surveys) et aux revues de littérature systématiques. Ces documents sont privilégiés car ils offrent une structure comparative pré-établie des techniques existantes, permettant de situer les contributions individuelles dans un cadre global. Par ailleurs, l'impact des publications, mesuré par leur taux de citation, a été utilisé comme indicateur de reconnaissance par la communauté scientifique pour hiérarchiser les lectures.

=== Critères de qualité et d'exclusion

Pour assurer la fiabilité des données et des méthodologies analysées, un filtrage strict sur la qualité éditoriale a été appliqué :

- Afin de garantir l'excellence scientifique du corpus, la sélection se limite aux articles de revues indexées Q1 ou Q2 par le #link("https://www.scimagojr.com/")[Scimago Journal Rank (SJR)] et aux communications de conférences classées de A\* à C selon #link("https://direction.bordeaux.inria.fr/~roussel/rankings/era/index.cgi")[l'Excellence in Research for Australia (ERA)], assurant ainsi un processus de révision par les pairs rigoureux.

- Les journaux identifiés comme prédateurs ainsi que les pré-publications non encore validées par un comité de lecture ont été systématiquement exclus du corpus final.

== Critères de sélection

La sélection des articles retenus a été guidée par l'objectif de construire une revue de littérature apte à répondre à nos questions de recherches. Les critères d'inclusion ont été structurés autour de la pertinence des contributions de chaque publication par rapport à ces problématiques.

Notre processus de sélection s'est déroulé en trois étapes successives : 
- l'examen des titres et des sources des articles
- l'analyse des mots-clés  
- la lecture des abstracts

Ce filtre a permis de réduire le corpus initial à une vingtaine de publications.

=== Algorithmes DRL : Architectures et Performance

L’examen des titres a d’abord permis d'isoler les travaux traitant spécifiquement du contrôle de drones (UAV) par Deep Reinforcement Learning, en privilégiant les revues systématiques et les études comparatives. Cette étape a ciblé les publications centrées sur les défis du déploiement, point de départ essentiel pour évaluer les compromis entre les architectures PPO, TD3 et DDPG.

L’analyse des mots-clés a ensuite confirmé un ancrage technique autour de la stabilité d’entraînement et de l’efficacité de l’échantillonnage.

Enfin, la lecture des résumés a constitué le dernier critère de sélection. Elle a permis d'écarter les approches purement théoriques pour ne retenir que les publications abordant explicitement les contraintes opérationnelles indispensables à une navigation autonome fiable : la robustesse face aux perturbations dynamiques, la gestion du temps réel et, surtout, la prise en compte du fossé entre simulation et réalité.

=== Curriculum Learning (CL) : Justification de la progression de l'apprentissage


L’examen des titres a d’abord permis d'isoler les travaux fondamentaux, allant de la revue généraliste du domaine aux cadres formels spécifiques reliant le Curriculum Learning au Deep RL. Cette étape a privilégié les revues de littérature transversales plutôt que les applications isolées, afin d'analyser comment complexifier graduellement l'environnement peut influencer positivement la dynamique d'apprentissage d'un agent.

L'analyse des mots-clés s'est ensuite concentrée sur l'Automatic Curriculum Learning et la génération automatique de tâches. Ce critère est essentiel pour accélérer la convergence et prévenir les stagnations de performance, typiques lors de l'apprentissage de manœuvres complexes comme l'atterrissage.

Enfin, la lecture des résumés a validé l’inclusion des articles sur le Guided Reinforcement Learning pour leur analyse critique du transfert Sim-to-Real en robotique, ainsi que des études dédiées aux systèmes d'évaluation, indispensables pour objectiver et quantifier l'impact réel des stratégies de curriculum.


=== Biais de simulation (Sim-to-Sim) : Assurance de la fidélité virtuelle

Le titre doit indiquer que l'étude porte sur la transition entre le virtuel et le réel. Comme le terme technique « sim2sim » est peu utilisé, il convient de privilégier les expressions décrivant l'écart de réalité. Les articles sélectionnés doivent mentionner le transfert sim-to-real, le Reality Gap ou l'usage de Jumeaux Numériques (Digital Twins). De plus, le titre doit préciser le domaine d'application, à savoir les drones (UAV) et l'utilisation de l'apprentissage par renforcement (DRL).

L'approche par mots-clés n'a pas été assez discriminante pour permettre une étape de sélection supplémentaire.

Le résumé doit attester que l'étude dépasse la simple simulation pour s'engager dans une démarche active d'évaluation et de correction de l'environnement virtuel. La sélection repose sur une méthodologie structurée en trois étapes clés : l'identification des anomalies, telles que les erreurs de trajectoire ou les biais aérodynamiques non modélisés, la mesure précise de l'écart de performance par rapport à des données réelles de référence (souvent via l'erreur RMSE) et l'utilisation de ces écarts pour affiner le simulateur.

=== Transfert Sim2Real

L'examen des titres a d'abord permis d'isoler les travaux traitant du transfert de la simulation vers réalité (Sim2Real) pour les systèmes robotiques aériens. Cette étape a privilégié les revues systématiques et les études comparatives (survey) établissant une taxonomie claire des techniques existantes. Ce choix méthodologique vise à identifier les approches qui ont démontré leur efficacité non seulement en simulation mais également sur des plateformes physiques, critère indispensable pour évaluer leur applicabilité réelle.

L'analyse des mots clés a confirmé la nécessité de sélectionner les articles plus techniques centrés sur la robustification du transfert. Nous avons exclusivement retenu les travaux quantifiant le reality gap par des mesures objectives (RMSE, taux de succès réel) plutôt que par des estimations qualitatives, garantissant ainsi la reproductibilité et la rigueur des résultats.

Enfin, la lecture des résumés a validé l'inclusion des articles démontrant une validation expérimentale rigoureuse sur des systèmes robotiques en général et sur les systèmes aériens réels en particulier. 
D'une part, nous avons sélectionné les travaux établissant Domain Randomization comme approche prédominante, car ils proposent des protocoles de randomisation détaillés et des résultats sur des milliers d'essais physiques. D'autre part, l'intégration d'études sur les approches émergentes (Disturbance-Aware RL, Reward Design robuste) permet d'identifier les innovations récentes qui complètent ou dépassent les techniques classiques. Un autre critère déterminant a été la présence d'une validation sur nano-drones ou quadrotors similaires au Crazyflie 2.1+, assurant la transférabilité directe des enseignements à notre projet.

#pagebreak()

== Critères d'analyse

#include "analysis.typ"

#pagebreak()

= Analyse de l'existant

== Quelle combinaison d'architecture algorithmique et de stratégie d'entraînement maximise la performance #footnote[Efficacité de l’échantillonnage, stabilité de l’entraînement, complexité de l'algorithme, résultat obtenu sur les drones.] en Deep Reinforcement Learning ?

=== Parmi les algorithmes couramment utilisés (PPO, TD3, DDPG), lequel offre le meilleur compromis entre stabilité d'entraînement et taux de succès lors du transfert vers le réel ? <Q1.1>

Pour déterminer quel algorithme offre le meilleur compromis pour le transfert vers le réel, il est essentiel de comprendre d'abord leurs mécanismes fondamentaux. En effet, PPO, TD3 et DDPG se distinguent par leur appartenance à deux familles majeures de l'apprentissage par renforcement, ce qui influence directement leur stabilité :

- Policy-Based : Ces méthodes apprennent directement une politique, qui est une cartographie des états aux actions. L'objectif est d'optimiser les paramètres de cette politique pour maximiser la récompense cumulée. Le PPO est un exemple phare de cette catégorie @azar2021drone.

- Actor-Critic : Cette approche combine les avantages des méthodes basées sur la valeur et celles basées sur la politique. Elle utilise deux réseaux de neurones : l'acteur, qui contrôle le comportement de l'agent en choisissant les actions (la politique), et le critique, qui évalue l'action choisie en estimant une fonction de valeur. Le DDPG et son successeur, le TD3, sont des algorithmes Actor-Critic @sonmez2024survey @chen2025survey.

==== DDPG (Deep Deterministic Policy Gradient)

Le DDPG est un algorithme Acteur-Critique "off-policy" conçu pour fonctionner dans des espaces d'actions continus @amendola2024drone. Il s'inspire du Deep Q-Network (DQN) en utilisant un "replay buffer" pour stocker les transitions passées et des réseaux cibles ("target networks") pour stabiliser l'apprentissage de l'acteur et du critique @azar2021drone.

Les applications du DDPG dans le contrôle des UAVs sont variées mais présentent des résultats mitigés. Rodriguez et al. (cité dans @sonmez2024survey) ont utilisé avec succès le DDPG pour l'atterrissage sur une plateforme mobile, atteignant des taux de succès de 90 % pour les scénarios lents et de 78 % pour les scénarios rapides. Oubbati et al. (cité dans @chen2025survey) ont également rapporté que le DDPG offre une amélioration significative des performances par rapport aux algorithmes basés sur la valeur et une meilleure adaptabilité aux changements du nombre de drones. Cependant, une étude de Jiang et Song (cité dans @sonmez2024survey) a révélé que le DDPG n'a pas réussi à aboutir à des atterrissages réussis dans leur configuration expérimentale, soulignant une potentielle instabilité. 

En effet, bien que performant dans des environnements simulés simples, le DDPG souffre d'une instabilité d'entraînement élevée due à sa sensibilité extrême aux hyperparamètres et à un biais de surestimation des valeurs Q. Dans le cadre du transfert vers le réel, ces instabilités se traduisent souvent par un manque de robustesse face aux bruits de capteurs ou aux perturbations externes.

Pour pallier ce problème, des variantes comme le DPG-IC (Deterministic Policy Gradient-Integral Compensator) ont été développées pour réduire l'erreur en régime permanent et explicitement "combler le fossé entre le modèle simplifié et la dynamique de vol réelle" (Wang et al., cité dans @sonmez2024survey).

==== TD3 (Twin Delayed DDPG)

L'algorithme Twin Delayed Deep Deterministic Policy Gradient (TD3) constitue une évolution majeure du DDPG, conçue spécifiquement pour pallier le biais de surestimation des fonctions de valeur (Q-valeurs) inhérent aux méthodes de gradient de politique déterministe. Pour stabiliser l'apprentissage, le TD3 introduit trois mécanismes fondamentaux : l'emploi de réseaux critiques jumeaux (Twin Critics), dont la valeur minimale est retenue pour limiter la surévaluation ; la mise à jour différée de la politique et des réseaux cibles par rapport aux réseaux critiques ; et le lissage de la politique cible via l'ajout de bruit aux actions cibles @chen2025survey. 

En tant qu'architecture Acteur-Critique @sonmez2024survey, le TD3 démontre une efficacité opérationnelle là où des modèles plus simples échouent. À cet égard, l'étude comparative de Jiang et Song (citée dans @sonmez2024survey) sur l'atterrissage de multirotors souligne que le TD3 parvient à accomplir la mission dans des conditions où le DDPG s'avère incapable de converger vers une solution viable. Cependant, cette performance accrue implique des contreparties techniques : une durée d'entraînement plus conséquente ainsi qu'une fluidité de mouvement réduite lors de l'exécution. Cette moindre précision gestuelle est vraisemblablement imputable au bruit de régularisation intrinsèque à l'algorithme, révélant ainsi un compromis structurel entre la fiabilité de la réussite de la tâche et la qualité de l'exécution motrice.

==== PPO (Proximal Policy Optimization)

L’algorithme Proximal Policy Optimization (PPO) s’est imposé comme une référence dans la littérature académique, qui, contrairement aux méthodes précédentes, fonctionne sur un principe « on-policy ». Sa large adoption s’explique par un équilibre optimal entre une relative simplicité d'implémentation et une robustesse accrue lors de la phase d'entraînement @amendola2024drone. Le cœur de son fonctionnement repose sur l’optimisation d’une fonction objectif de substitution, conçue pour réguler l’amplitude des mises à jour des paramètres. En intégrant un mécanisme de troncature (clipping), le PPO restreint les variations brusques de la politique d'une itération à l'autre, évitant ainsi les instabilités numériques et garantissant une convergence plus fluide vers la solution optimale @amendola2024drone.

Dans le domaine des véhicules aériens sans pilote (UAV), le PPO a démontré des capacités de contrôle particulièrement performantes face à des dynamiques de vol complexes. Les travaux de Kooi et Babuška (cités dans @sonmez2024survey) illustrent cette efficacité lors de manœuvres d’atterrissage autonome sur des surfaces inclinées, surpassant les standards algorithmiques existants. Par ailleurs, Hu et Wang (cités dans @sonmez2024survey) ont exploité une variante avancée du PPO pour la régulation de vitesse d’un quadrotor, prouvant une supériorité en termes de précision et de robustesse vis-à-vis des contrôleurs traditionnels de type PID (Proportionnel-Intégral-Dérivé). Enfin, la polyvalence de cet algorithme a été confirmée par son application réussie au contrôle longitudinal et latéral de drones hybrides, capables de gérer la complexité inhérente à ces systèmes multi-états @azar2021drone.

==== Synthèse

#{
  show table.cell: set text(size: 8pt)
  
table(
  columns: 4,
  table.header([], [*DDPG*], [*TD3*], [*PPO*]),
[*Type d'algorithme*], [Off-policy (Hors stratégie)], [Off-policy (Hors stratégie)], [On-policy (Sous stratégie)],
[*Famille / Approche*], [Actor-Critic], [Actor-Critic], [Policy-Gradient / Actor-Critic],
[*Espace d'action*], [Continu], [Continu], [Discret ou Continu],
[*Politique*], [Déterministe], [Déterministe], [Stochastique],
[*Mécanisme clé*], [Utilise un replay buffer et des réseaux cibles pour stabiliser l'apprentissage], [Apprend deux fonctions Q dites jumelles et retarde la mise à jour de la politique pour réduire la surestimation], [Utilise une fonction objectif "clipped" (tronquée) pour limiter la taille des mises à jour et assurer la stabilité],
[*Efficacité de l'échantillonnage*  (Réutilisation des données passées)], [Élevée], [Élevée], [Modérée],
[*Stabilité de l'entraînement*], [Peut être instable et sensible aux hyperparamètres], [Plus stable que DDPG (corrige le biais de surestimation)], [Élevée (grâce aux mises à jour contraintes)],
[*Complexité de l'algorithme*], [Élevée (plusieurs réseaux neuronaux)], [Élevée (ajoute des mécanismes au DDPG)], [Modérée (plus simple à implémenter et régler)],
[*Résultats obtenus sur des drones*], [Bon pour le vol stationnaire (hovering), mais peut osciller], [Réussit là où DDPG peut échouer, mais apprentissage parfois plus long], [Contrôle d'attitude précis, moins d'oscillations, atterrissage cohérent]
)
}

Le PPO constitue généralement la solution préférentielle pour la recherche appliquée sur les drones multirotors. 
Bien que le TD3 offre une efficacité d'échantillonnage supérieure (nécessitant moins d'interactions simulées), la sécurité d'entraînement et la fiabilité du transfert Sim-to-Real offertes par le PPO en font l'algorithme le plus plébiscité pour garantir un taux de succès élevé lors du déploiement physique.
Quant au DDPG, il reste pertinent pour les tâches en espaces d'actions continus en raison de son efficacité en termes d'échantillons, mais son déploiement réussi exige une expertise significative et des stratégies hybrides pour garantir la robustesse dans le monde réel.


=== Quel est l'impact de l'apprentissage par curriculum sur la vitesse de convergence et la robustesse des politiques en DRL ? <Q1.2>

L'apprentissage par curriculum (CL), formellement théorisé par Bengio et al. (cité dans @JMLR:v21:20-212), se définit comme une stratégie d'entraînement inspirée des processus cognitifs humains et animaux. Contrairement à l'approche stochastique traditionnelle consistant à présenter les données de manière aléatoire, le CL organise l'entraînement selon une complexité croissante. Cette approche, qualifiée de "start small", guide le modèle depuis des exemples élémentaires vers l'ensemble complet des données ou des tâches @wang2021survey.

Dans notre contexte des problèmes d'optimisation pour les systèmes autonomes UAV, cette méthode influence positivement deux vecteurs critiques :

* Guidage de l'optimisation :* En simplifiant les tâches initiales, le CL lisse la complexité du problème et guide les paramètres vers une solution optimale plutôt que vers un optimum local. En RL, cette progression est cruciale : elle pallie le problème des récompenses rares (sparse rewards) en fournissant un feedback intermédiaire nécessaire à l'apprentissage @portelas2020automaticcurriculumlearningdeep.

*Robustesse et réduction du bruit* : En privilégiant initialement les données propres et à haute confiance, le modèle acquiert une structure de base robuste avant d'être confronté aux données bruitées ou aberrantes. Cette stratégie limite le sur-apprentissage sur des artefacts et améliore significativement la généralisation lors du transfert @electronics12071676.

==== Catégorisation des techniques de CL

Les méthodologies de CL s'articulent autour d'un cadre comprenant un Évaluateur de Difficulté et un Planificateur d'Entraînement. La littérature distingue deux familles principales : les méthodes prédéfinies et les méthodes automatiques.

====  Approches Prédéfinies (Predefined CL)

Ces méthodes reposent sur une expertise humaine a priori pour fixer la mesure de la difficulté et le calendrier d'entraînement avant le processus d'apprentissage.

- *Métriques Heuristiques* : La difficulté est quantifiée via des caractéristiques intrinsèques aux données, telles que la complexité visuelle ou le bruit dans l'image @portelas2020automaticcurriculumlearningdeep.
- *Planification Statique* : L'introduction des données suit des fonctions mathématiques (linéaires, racines) ou des stratégies par étapes ("Baby Steps"), augmentant progressivement la fraction de données difficiles @wang2021survey. Bien que simple, cette approche souffre d'une rigidité qui peut ne pas s'aligner avec la progression réelle du modèle.

==== Approches Automatiques

Ces techniques génèrent le curriculum dynamiquement, souvent en rétroaction avec les performances du modèle, offrant une adaptabilité supérieure.

- *Self-Paced Learning (SPL)* : Le modèle agit comme son propre instructeur en utilisant la loss comme proxy de la difficulté. Les échantillons à faible perte sont privilégiés initialement @wang2021survey. Des variantes comme le Self-paced Learning with Diversity (SPLD) intègrent des critères de diversité pour éviter le sur-apprentissage.
- *Transfer Teacher* : Un modèle teacher pré-entraîné évalue la difficulté des échantillons pour le modèle student, fournissant une mesure de difficulté stable @wang2021survey.
- *RL Teacher* : Un agent de deep RL distinct apprend à sélectionner les données optimales pour maximiser la vitesse d'apprentissage de l'étudiant. Bien que coûteuse en calcul, cette méthode permet de découvrir des curricula non intuitifs @electronics12071676.

==== Stratégies spécifiques au deep RL

Pour les agents autonomes (tels que les UAV), des techniques spécifiques ont été développées pour structurer l'exploration et l'apprentissage :

- *Prioritized Experience Replay (PER)* : le PER priorise le rejeu des transitions ayant une forte erreur de différence temporelle, focalisant l'agent sur les expériences surprenantes pour accélérer la convergence @portelas2020automaticcurriculumlearningdeep.
- *Génération de Curriculum Inverse (Reverse Curriculum)* : Pour les tâches à but précis, Florensa et al (cité dans @esser2022guided) suggèrent d'initialiser l'entraînement proche du but, puis d'éloigner progressivement les états de départ.
- *Goal GANs* : Utilisation de réseaux antagonistes génératifs pour proposer des objectifs adaptés au niveau actuel de l'agent @JMLR:v21:20-212.
- *Self-Play* : Dans les environnements compétitifs, l'agent s'entraîne contre des versions antérieures de lui-même, créant un curriculum émergent naturel @JMLR:v21:20-212.

==== Synthèse Comparative et Impact

Le choix de la stratégie de curriculum influence directement le compromis entre le coût computationnel, la stabilité de l'entraînement et la capacité de transfert vers des environnements réels. Le tableau ci-dessous synthétise les caractéristiques des différentes approches identifiées.

#figure({
  show table.cell: set text(size: 8pt)
  table(
    columns: (20%, 1fr, 1fr, 1fr),
    align: horizon,
    
    [*Caractéristique*], [*Curriculum Prédéfini*], [*Self-Paced Learning (SPL)*], [*RL Teacher & Méthodes RL Spécifiques*],
    
    [Principe Directeur], [Expertise humaine et heuristiques fixes.], [Auto-évaluation via la Loss.], [Interaction dynamique (Agent enseignant) ou propriétés de l'environnement (Buts).],
    
    [Mesure de Difficulté], [Statique : Basée sur des attributs a priori (ex: bruit, complexité).], [Automatique : Faible perte = facile ; Forte perte = difficile.], [Émergente : TD-error (PER), distance au but (Reverse), compétence adverse (Self-play).],
    
    [Adaptabilité], [Faible. Ne s'adapte pas aux progrès du modèle en temps réel.], [Élevée. Le curriculum évolue selon la capacité du modèle à minimiser la perte.], [Très élevée. Le curriculum est entièrement piloté par la performance ou l'état de l'agent.],
    
    [Stabilité & Robustesse], [Variable. Dépend de la pertinence de l'expertise humaine.], [Améliore la robustesse au bruit (ignore les outliers initialement).], [Très stable. Le PER et le Reverse Curriculum stabilisent la convergence dans les espaces complexes.],
    
    [Coût de Calcul], [Très faible.], [Faible à moyen (calculs de perte supplémentaires).], [Élevé (entraînement d'un second agent) à modéré (gestion du buffer pour PER).],
    
    [Cas d'Usage Idéal], [Connaissance métier forte disponible ; contraintes de calcul strictes.], [Données bruitées ; scénarios sans connaissance a priori.], [Problèmes de contrôle complexes (UAV), récompenses rares, environnements compétitifs.]
  )},
  caption: [Tableau Comparatif des Stratégies de Curriculum Learning],
)

==== Conclusion : Implications pour les Systèmes UAV

L'analyse de l'état de l'art démontre que l'apprentissage par curriculum n'est pas une simple optimisation d'hyperparamètres, mais une méta-stratégie fondamentale pour la robustesse des politiques en DRL.

Pour des applications de type UAV, où la fidélité de la simulation et la sûreté sont primordiales, les méthodes de génération de Curriculum Inverse et de Prioritized Experience Replay semblent offrir les gains les plus significatifs en matière de vitesse de convergence. Parallèlement, l'approche Self-Paced Learning peut s'avérer pertinente pour le traitement des données sensorielles bruitées, favorisant un transfert plus sûr des politiques apprises vers le monde réel.


== Quelles techniques permettent de réduire le Reality Gap ?

=== Comment quantifier les biais de simulation et évaluer la fidélité d'un environnement virtuel en amont du déploiement physique ? <Q2.1>

==== Les Fondements de la Modélisation Haute-Fidélité pour les Drones

La création d'une simulation fidèle en amont du déploiement repose sur une modélisation rigoureuse des multiples aspects de la dynamique du drone. La qualité et la complétude de ces modèles physiques et sensoriels constituent la première ligne de défense contre le biais de simulation. Plus le modèle initial est capable de capturer les phénomènes physiques complexes, moins le transfert vers le monde réel sera problématique. Cette section décompose les éléments fondamentaux de cette modélisation.

La dynamique d'un drone est typiquement représentée comme un corps rigide à 6 degrés de liberté (DoF), soumis à la gravité, aux forces et aux couples générés par ses actionneurs @bauersfeld2021bem @hanover2024autonomous. Ce modèle cinématique constitue le squelette sur lequel s'ajoutent les modèles plus complexes des forces externes.

Pour les applications à faible vitesse, un modèle aérodynamique quadratique est souvent suffisant. Il postule que la poussée et le couple d'un rotor sont simplement proportionnels au carré de sa vitesse de rotation @bauersfeld2021bem @hanover2024autonomous. Cependant, cette simplification s'avère rapidement insuffisante lors de manœuvres agiles à haute vitesse. Elle néglige des effets critiques, notamment l'influence de la vitesse de l'air entrant sur la poussée générée par les rotors @bauersfeld2021bem.

Pour surmonter ces limites, des approches basées sur des principes physiques plus fins sont nécessaires. La théorie du "Blade-Element-Momentum" (BEM) est une de ces approches. Elle modélise les forces et les couples en intégrant les contributions de chaque élément infinitésimal de pale de rotor, permettant ainsi de prendre en compte de manière explicite les effets de la vitesse de l'air relative sur la performance aérodynamique @bauersfeld2021bem.

La performance d'un drone est directement liée à la réponse de ses moteurs et à la tension fournie par sa batterie. Une modélisation précise de la dynamique des moteurs et des caractéristiques de décharge de la batterie est cruciale, car ces éléments influencent directement la vitesse de rotation réelle des hélices et, par conséquent, les forces et couples réellement produits @bauersfeld2021bem. De même, les moteurs doivent être modélisés comme des systèmes du premier ordre pour capturer leur constante de temps de réponse @foehn2022agilicious.

Un simulateur haute-fidélité doit également modéliser les imperfections des capteurs embarqués, tels que les caméras et les unités de mesure inertielle (IMU). Des phénomènes comme le bruit des capteurs, les biais de mesure et les vibrations à haute fréquence induites par les moteurs peuvent introduire des erreurs significatives dans l'estimation de l'état du drone, affectant la performance des algorithmes de contrôle et de navigation @bauersfeld2021bem. Les vibrations à haute fréquence induites par les hélices constituent la source majeure d'erreur, provoquant des effets d'aliasing sur les mesures de l'IMU et du flou de mouvement (motion blur) sur les images de la caméra. Une simulation robuste doit donc intégrer ces caractéristiques de bruit et de biais pour valider efficacement les algorithmes de navigation @hanover2024autonomous.

==== Approches pour l'Amélioration de la Fidélité en Amont

Pour pallier les limites des modèles analytiques classiques, la littérature récente propose des méthodologies sophistiquées visant à réduire le fossé de réalité (*reality gap*). Ces approches se divisent en trois axes : la modélisation hybride, l'intégration matérielle (HIL) et la correction en temps réel, validées par des benchmarks rigoureux.

L'approche "NeuroBEM" illustre la fusion entre principes physiques et apprentissage automatique pour maximiser la généralisation. Elle combine la théorie *Blade-Element-Momentum* (BEM) pour les forces aérodynamiques prédominantes avec un réseau de neurones profond chargé de prédire les dynamiques résiduelles complexes (interactions rotor-rotor, effets parasites).  Cette méthode permet de réduire l'erreur de prédiction de plus de 50 % par rapport aux modèles purement physiques, offrant une fidélité accrue pour des manœuvres agressives sans nécessiter d'ajustements spécifiques à chaque trajectoire @bauersfeld2021bem.

La plateforme *Agilicious* propose une alternative consistant à intégrer le véhicule physique dans la boucle de simulation (*Hardware-in-the-Loop* ou HIL). Plutôt que de modéliser imparfaitement la dynamique, le drone vole dans un espace de capture de mouvement tout en interagissant avec un environnement virtuel photoréaliste.
Cette architecture permet de simuler des perturbations perceptuelles extrêmes et difficiles à modéliser analytiquement, telles que le flou de mouvement (*motion blur*), la distorsion, ou des conditions environnementales comme le vent et la pluie, tout en conservant la dynamique réelle et les mesures proprioceptives du drone @foehn2022agilicious.

Contrairement à la recherche d'un modèle global parfait, l'approche par jumeau numérique (*Digital Twin*) vise une correction locale et tâche-spécifique. En alignant rigoureusement les paramètres physiques du modèle virtuel sur le réel (*Model matching*), le système utilise la simulation parallèle pour rectifier en temps réel les erreurs de l'algorithme causées par le bruit du monde réel (occlusions, éclairage variable), agissant ainsi comme un mécanisme actif de transfert *Sim-to-Real* @liu2022twin.

Enfin, des simulateurs comme *FlightGoggles* ou *Flightmare* sont couplés à des jeux de données réels (tels que *Blackbird* ou *UZH-FPV Drone Racing Dataset*) pour quantifier précisément l'écart entre la dynamique simulée et la réalité. Ces benchmarks permettent d'évaluer des politiques de contrôle qui n'ont pas nécessairement été entraînées sur le simulateur de test, introduisant ainsi une étape de validation Sim-to-Sim. En effet, pour des raisons d'efficacité computationnelle, l'entraînement s'effectue souvent sur des moteurs physiques simplifiés et hautement parallélisables, avant d'être transféré vers ces environnements haute-fidélité pour une vérification rigoureuse préalable au déploiement réel @hanover2024autonomous.

==== Méthodologies de Quantification de la Fidélité (Validation Sim-to-Real)

L'évaluation de la performance prédictive en boucle ouverte constitue la première ligne de validation. Cette méthode isole la capacité du simulateur à reproduire les forces et couples aérodynamiques enregistrés dans des jeux de données de test, sans nécessiter de nouveaux vols. La fidélité est alors quantifiée par l'erreur quadratique moyenne (RMSE) entre la dynamique prédite par le modèle et la vérité terrain mesurée, permettant d'identifier les biais de modélisation physique avant l'intégration du contrôleur @bauersfeld2021bem.

Pour capturer les interactions dynamiques complexes, la validation s'étend à la simulation en boucle fermée sur trajectoires de référence. Cette approche consiste à "rejouer" des missions agressives issues de benchmarks établis (telles que des vols à 60 km/h sous accélérations de 4g) au sein de l'environnement virtuel. La métrique de référence devient ici la RMSE positionnelle : une corrélation étroite entre l'erreur de suivi simulée (par exemple 0,32 m) et l'erreur historique réelle atteste que le simulateur reproduit fidèlement les limitations du système et les perturbations environnementales @foehn2022agilicious.

Enfin, dans le paradigme des jumeaux numériques, la validation repose sur l'alignement paramétrique rigoureux (Model Matching) et l'évaluation du taux de succès de la tâche. La fidélité de l'environnement n'est pas uniquement jugée sur la physique pure, mais sur sa capacité à prédire la réussite d'une mission (telle que la préhension robotique). Un taux de réussite en simulation corrélé aux performances attendues dans le réel permet ainsi de certifier l'environnement comme un mécanisme fiable de transfert Sim-to-Real @liu2022twin.

==== Synthèse

#{
  show table.cell: set text(size: 8pt)
  table(
  columns: 5, 
  table.header([], [*Modélisation Hybride*], [*Jumeau Numérique*], [*Évaluation en Boucle Fermée*], [*Évaluation de la Généralisation*]),   
  [*Principe Fondamental*], [Fusion d'un modèle physique et d'un réseau de neurones pour prédire les dynamiques résiduelles.], [Alignement paramétrique rigoureux et simulation parallèle pour corriger les erreurs en temps réel.], [Simulation complète de la mission (contrôle + dynamique) pour comparer la trajectoire virtuelle à la réelle.], [Validation sur des jeux de données standardisés ou des scénarios non vus lors de l'entraînement.],

  [*Objectif Prioritaire*], [Améliorer la précision prédictive (forces/couples) pour des manœuvres inédites.], [Maximiser le succès d'une tâche spécifique via un transfert Sim-to-Real actif.], [Vérifier la stabilité du système et les limites de performance avant le déploiement physique.], [Quantifier objectivement le "Reality Gap" et certifier la robustesse des algorithmes.],

  [*Métrique de Quantification*], [Erreur Quadratique Moyenne sur les forces et les couples.], [Taux de succès de la tâche.], [Erreur de suivi de position sur la trajectoire.], [Performance relative sur Benchmarks.],

  [*Rôle des Données Réelles*], [Servent à l'entraînement du réseau pour capturer les effets non modélisés.], [Utilisées pour la calibration initiale et la synchronisation en ligne.], [Servent de vérité terrain pour valider la fidélité de la simulation a posteriori.], [Agissent comme un filtre de validation final pour éviter le sur-apprentissage.]
)}

=== Quelles sont les approches prédominantes permettant d'assurer la robustesse du transfert Sim2Real pour les systèmes robotiques aériens ? <Q2.2>

L'utilisation du DRL pour le contrôle de drones se heurte systématiquement au problème du Reality Gap. Ce phénomène se traduit par une chute drastique des performances lorsque la politique, entraînée dans un simulateur comme IsaacSim ou Gazebo, est déployée sur le système physique. Selon la taxonomie établie par Salvato et al. @salvato2021crossing, ce fossé résulte de trois divergences majeures : 
- Le Biais de Dynamique : Les écarts entre les moteurs physiques (ODE, PhysX) et la réalité aérodynamique (turbulences, effet de sol, réponse moteur).

- Le Biais de Perception : La différence entre le rendu graphique "parfait" du simulateur et les images réelles bruitées, floues ou mal éclairées.

- Le Biais Temporel et Stochastique : Les latences de communication, le bruit des capteurs et les perturbations environnementales non modélisables.

L'analyse de la littérature récente entre 2020 à 2025 nous permet d'identifier trois stratégies prédominantes pour sécuriser ce transfert :
- l'adaptation statistique par randomisation,
- l'adaptation par fidélité du modèle, 
- et l'adaptation architecturale.

==== L'Approche Statistique : Le Domain Randomization (DR)
Le Domain Randomization est l'approche la plus répandue dans la littérature, elle consiste à accepter l'imperfection du simulateur et à entraîner l'agent sur une large distribution de paramètres physiques et visuels. L'hypothèse sous-jacente est que si l'agent apprend à être robuste à une grande variété de physiques simulées, la réalité ne sera perçue que comme une variation supplémentaire de la simulation.

Cette approche est particulièrement critique pour les systèmes basés sur la vision embarquée. Polvara et al. (2020) @polvara2020sim ont démontré l'efficacité de cette méthode pour l'atterrissage autonome d'un quadrotor sur un marqueur. En randomisant massivement les textures du sol, l'éclairage et la position du marqueur en simulation, ils ont ainsi forcé le réseau de neurones à extraire des caractéristiques visuelles invariantes. 
Leurs résultats montrent une augmentation du taux de succès réel de 28% (sans randomisation) à 91% (avec randomisation).
Par ailleurs, pour gérer la complexité de la tâche, les auteurs introduisent une architecture séquentielle, SDQN,  pour "Sequential Deep Q-Networks". Cette approche baptisée "Divide-and-Conquer" sépare la phase d'approche de la phase de descente verticale, isolant ainsi les erreurs de perception et empêchant leur propagation, ce qui stabilise significativement le transfert.

==== L'Approche par Fidélité : System Identification et Modélisation

À l'opposé de la randomisation massive, une seconde école de pensée soutient que la réduction du Reality Gap passe par une modélisation extrêmement fidèle des composants critiques du drone, rendant la randomisation superflue pour certaines tâches.

Cette approche est défendue par Kooi et Babuška (2021) @kooi2021inclined, qui parviennent à réaliser des atterrissages complexes sur des plans inclinés avec un nano-drone Crazyflie 2.1 sans recourir au Domain Randomization. 
Leur contribution majeure réside dans l'identification précise de la chaîne d'actionneurs : en modélisant fidèlement la réponse des contrôleurs PID internes et les délais moteurs (identifiés à environ 33ms), ils obtiennent un simulateur suffisamment proche du réel pour un transfert direct. Cette étude met en évidence une limitation du Domain Randomization. 
Pour des tâches de contrôle dynamique pur à haute fréquence, randomiser la physique peut parfois conduire à des politiques trop conservatrices, là où un modèle fidèle permet des manœuvres plus agressives et précises.

==== L'Approche Architecturale et Temporelle

Le Reality Gap n'est pas uniquement spatial ou physique, il est aussi temporel. Les systèmes robotiques réels, en particulier ceux pilotés via des middlewares comme ROS 2, souffrent de latences de communication et de traitement qui sont souvent absentes ou constantes en simulation.

===== Gestion de la latence 
Malmir et al. (2023) @malmir2023diarel s'attaquent spécifiquement à ce problème via leur méthode DiAReL.
Ils démontrent que les architectures classiques (Markoviennes) échouent dès que le délai dépasse 40ms, une valeur fréquente sur les liens radio chargés. Leur solution repose sur l'Augmentation d'État (State Augmentation), consistant à fournir au réseau de neurones un historique glissant des $N$ dernières actions et observations. Cette "mémoire à court terme" permet à la politique d'inférer implicitement les délais du système et de compenser la latence, rétablissant la stabilité du contrôle.

===== Architectures Coopératives
Pour les phases de vol où la dynamique change brutalement comme l'effet de sol (ground effect) juste avant l'atterrissage), un seul réseau global peine souvent à généraliser. 
Wu et al. (2022) @wu2022two proposent alors une architecture modulaire dite "Coopérative". Ils découplent le problème en deux politiques distinctes : 
- une Task Policy, entraînée pour la navigation générale, 
- et une Gap Policy, un module résiduel léger dont le seul but est d'apprendre à compenser les erreurs dynamiques fines (friction, contact) lors du transfert. 
Cette séparation permet d'ajuster le comportement final sans détériorer les capacités de navigation acquises.

==== Quantification de la Sûreté et Diagnostic
Une tendance émergente notée dans les travaux les plus récents (2024-2025) est le passage d'une validation empirique ("ça marche") à une validation plus formelle ou diagnostique ("c'est sûr").

Sangeerth et Jagtap (2025) @sangeerth2025quantification introduisent le concept de Neural Simulation Gap Function. Au lieu de traiter l'erreur de simulation comme un bruit inconnu, ils entraînent un réseau de neurones pour apprendre explicitement la fonction d'erreur $ f_"réel"(x) - f_"sim"(x) $. Cette approche hybride permet d'utiliser des outils mathématiques (constantes de Lipschitz) pour borner l'erreur de trajectoire maximale, offrant des garanties de sécurité cruciales pour le déploiement autonome.

Sur le plan méthodologique, Coursey et al. (2024) @coursey2024quantifying proposent de dépasser la simple métrique du taux de succès. Ils utilisent la divergence de Jensen-Shannon, une mesure statistique quantifiant la similarité entre deux distributions de probabilités. Ils l'utilisent pour comparer les distributions de données simulées et réelles. Cette analyse fine permet de diagnostiquer a posteriori quelle variable physique est responsable de l'échec (par exemple, une dérive inattendue sur l'axe de lacet/yaw), guidant ainsi les ingénieurs pour affiner le simulateur plutôt que de ré-entraîner l'agent à l'aveugle.


==== Spécificités des Systèmes Collaboratifs
Enfin, le transfert Sim2Real revêt une complexité additionnelle dans le cadre de projets impliquant l'interaction physique et visuelle entre plusieurs agents distincts, comme c'est le cas dans cette étude. Contrairement au cas mono-agent, le Reality Gap se double ici d'un problème de non-stationnarité induite : les erreurs de modélisation de l'un des robots modifient l'environnement perçu par l'autre, rendant les politiques apprises en simulation obsolètes.

Dans leurs travaux sur les systèmes multi-UAV, Shi et al. (2023) @shi2023marl formalisent ce défi comme un problème de Jeux de Markov Partiellement Observables (POMDP). Ils démontrent que les algorithmes standards (comme DDPG ou MADDPG classique) échouent lors du transfert réel car ils supposent que l'état des autres agents est parfaitement connu et fiable. Or, dans la réalité, la position et la vitesse du robot partenaire sont bruitées et soumises à des dynamiques de friction ou de glissement inconnues du simulateur.

Pour pallier cette incertitude, les auteurs établissent la nécessité d'utiliser des architectures R-MADDPG (Recurrent Multi-Agent Deep Deterministic Policy Gradient). L'intégration de réseaux récurrents (type RNN ou LSTM) dans les couches cachées de l'acteur et du critique permet à chaque agent de :

Construire une représentation interne de la dynamique réelle de son partenaire, basée sur l'historique des observations récentes (mémoire temporelle) ;

Discerner les intentions du partenaire malgré le bruit des capteurs, en filtrant les incohérences momentanées dues au transfert.

De plus, Shi et al. préconisent une modularisation stricte Perception-Contrôle. Au lieu d'une politique "bout-en-bout" (pixels vers moteurs), ils séparent le module de vision (qui traite le gap visuel) du module de décision (qui traite le gap dynamique via le RNN). Cette architecture permet d'isoler les incertitudes visuelles de la plateforme mobile afin qu'elles ne déstabilisent pas la boucle de contrôle collaborative du drone.

==== Synthèse

#{
  show table.cell: set text(size: 8pt)
  

  table(
    columns: 6,
    [*Approche*],
    [*Principe*],
    [*Avantages*],
    [*Limites*],
    [*Verdict & Cas d'Usage*],
    [*Articles Clés*],


    [Domain Randomization],
    [Entraîner sur une large distribution \  d'environnements simulés.],
    [\- Robustesse Visuelle \ - Généralisation (Zero-shot)],
    [ \- Conservatisme (Lenteur) \ - Irréalisme physique],
    [Indispensable pour la Vision et milieux non structurés.],
    [@polvara2020sim\ @salvato2021crossing],

    [System Identification],
    [Minimiser le Gap en alignant le modèle mathématique sur le réel.],
    [\- Performance (Agilité) \ - Efficacité (Peu de data)],
    [ \- Coût Ingénierie\ - Fragilité matérielle],
    [Privilégié pour le Contrôle Dynamique fin (Moteurs).],
    [@kooi2021inclined],

    [Architecturale\ (Modularité)],
    [Doter l'agent d'une mémoire (RNN) ou découpler les modules.],
    [\- Immunité Latence \ - Multi-Agents (Collab)],
    [\- Complexité (R-MADDPG) \ - Opacité (Black Box)],
    [Requis pour ROS 2 et interactions complexes.],
    [@malmir2023diarel\ @shi2023marl\ @wu2022two],

    [Diagnostique (Sécurité)],
    [Quantifier l'erreur via divergence ou apprentissage de l'erreur.],
    [\- Garanties Sûreté \ - Explicabilité (Diagnostic)],
    [\- Passif (Post-mortem) \ - Coût de calcul],
    [Bonus pour la Certification et l'analyse de sécurité.],
    [@sangeerth2025quantification\ @coursey2024quantifying],
  )
}

#pagebreak()

= Conclusion
L'objectif de cet état de l'art était d'identifier les composants méthodologiques permettant de fiabiliser une chaîne de contrôle « End-to-End » pour l'atterrissage autonome d'un nano-drone sur une plateforme mobile. L'analyse de la littérature récente (2020-2025) apporte des réponses structurées aux quatre questions de recherche formulées, déclinées selon deux axes : le choix des architectures algorithmiques et des stratégies d'apprentissage en Deep Reinforcement Learning, et les techniques de réduction du Reality Gap.

Sur l'architecture algorithmique optimale, l'analyse comparative @amendola2024drone @azar2021drone @chen2025survey @sonmez2024survey révèle que le PPO (Proximal Policy Optimization) constitue le choix privilégié pour la robotique aérienne. Bien que le TD3 offre une efficacité d'échantillonnage supérieure, la stabilité d'entraînement et la fiabilité du transfert Sim-to-Real du PPO en font l'algorithme le plus adapté aux nano-drones comme le Crazyflie 2.1+ @kooi2021inclined. 
Le DDPG reste toutefois pertinent pour des tâches spécifiques, mais nécessite une expertise significative pour garantir la robustesse en conditions réelles.

Concernant l'apprentissage par curriculum, son impact est significatif et positif sur la vitesse de convergence et la robustesse des politiques @electronics12071676 @esser2022guided @JMLR:v21:20-212 @wang2021survey @portelas2020automaticcurriculumlearningdeep. Les gains observés atteignent jusqu'à 70% de réduction du temps d'entraînement, avec une amélioration notable de la robustesse grâce au mécanisme de « denoising » qui se concentre initialement sur des données simples. Pour une tâche complexe comme l'atterrissage sur plateforme mobile, la décomposition en sous-tâches (détection, approche, descente, compensation du mouvement) permet d'accélérer la convergence et d'améliorer la stabilité du système.

Sur la quantification des biais de simulation, quatre approches complémentaires émergent @hanover2024autonomous @bauersfeld2021bem @foehn2022agilicious @liu2022twin : la modélisation hybride (physique + réseau de neurones), le Hardware-in-the-Loop, les jumeaux numériques, et la validation Sim-to-Sim via benchmarks standardisés. Les métriques établies incluent l'erreur quadratique moyenne (RMSE) sur les forces et couples, l'erreur de suivi de position, et le taux de succès de la tâche.

Concernant le transfert Sim2Real, l'analyse @salvato2021crossing @polvara2020sim @kooi2021inclined @malmir2023diarel @wu2022two @sangeerth2025quantification @coursey2024quantifying @shi2023marl identifie quatre stratégies prédominantes dont l'efficacité dépend du type de biais ciblé. Le Domain Randomization est indispensable pour la vision embarquée (taux de succès passant de 28% à 91% @polvara2020sim), tandis que le System Identification est privilégié pour le contrôle dynamique fin. L'augmentation d'état (historique d'actions) résout les problèmes de latence au-delà de 40ms @malmir2023diarel, critiques pour les communications ROS 2. Pour les systèmes collaboratifs, les architectures récurrentes (R-MADDPG) sont nécessaires pour gérer la non-stationnarité induite par les erreurs de modélisation croisées entre agents @shi2023marl.
