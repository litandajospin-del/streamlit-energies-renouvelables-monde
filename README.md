# streamlit-energies-renouvelables-monde

# Tableau de Bord de la Production Mondiale d'Énergie Renouvelable

**Projet Data Visualisation**  
Université de Montpellier  
Master 2 MBFA parcours SIEF

**URL du Tableau de Bord :** https://app-energies-renouvelables-monde.streamlit.app/)  
**Technologies :** Streamlit, Plotly, Pandas

---

## Table des Matières

1. [Aperçu du Projet](#aperçu-du-projet)
2. [Récit Data Story](#récit-data-story)
3. [Informations sur les Données](#informations-sur-les-données)
4. [Fonctionnalités & Visualisations](#fonctionnalités--visualisations)

---

## Aperçu du Projet <a name="aperçu-du-projet"></a>

**Nom du Tableau de Bord :** Production Mondiale d'Énergie Renouvelable - Analytics Avancés  
**Source des Données :** ourworldindata.org  
**URL du Tableau de Bord :** https://app-energies-renouvelables-monde.streamlit.app/  
**Technologies :** Python, Streamlit, Plotly, Pandas

### Énoncé du Problème

**Question Centrale :** Comment le paysage mondial des énergies renouvelables a-t-il évolué entre les pays et les types d'énergie, et qu'est-ce que cela révèle sur la voie vers la neutralité carbone ?

**Public Cible :**

- Décideurs politiques en matière d'énergie et responsables gouvernementaux  
- Administrateurs régionaux prenant des décisions d'investissement en infrastructures  
- Organisations environnementales suivant les engagements climatiques mondiaux  
- Analystes et chercheurs du secteur énergétique  
- Citoyens intéressés par la transition énergétique mondiale

**Points Clés à Retenir :**

- Disparités de production révélant où les investissements en infrastructure sont nécessaires  
- Composition du mix énergétique montrant la domination persistante de l'hydroélectricité  
- Tendances temporelles démontrant l'expansion rapide de l'éolien et la croissance modérée du solaire  
- Avantages géographiques (montagnes, côtes, ensoleillement) influençant les spécialisations  
- Recommandations stratégiques pour accélérer le déploiement des énergies renouvelables

---

## Récit Data Story <a name="récit-data-story"></a>

**Modèle Narratif :** Évolution Temporelle + Comparaison entre Pays

Ce tableau de bord suit un arc narratif structuré qui va de l'identification du problème à travers l'analyse jusqu'aux insights actionnables.

### 1. Accroche - Le Défi de la Neutralité Carbone

Le monde s'est engagé à atteindre la neutralité carbone d'ici 2050. Les énergies renouvelables doivent remplacer les combustibles fossiles dans la production d'électricité, les transports et le chauffage. Comprendre où la production renouvelable se produit, quelles technologies réussissent et où existent les lacunes détermine si cet objectif est réalisable.

Les enjeux sont élevés : l'échec signifie des émissions continues de carbone, des pénalités climatiques et une dépendance aux importations d'énergie. Le succès nécessite de comprendre des années de données de production à travers de nombreux pays pour identifier les modèles, prédire les goulets d'étranglement et allouer les ressources efficacement.

### 2. Contexte - Le Paysage Mondial

- Couverture Géographique : Plus de 100 pays suivis
- Période Temporelle : Données annuelles
- Sources d'Énergie Suivies :
  - Hydroélectricité (barrages, rivières)
  - Énergie éolienne (turbines terrestres)
  - Énergie solaire photovoltaïque (panneaux, fermes)
  - Total des énergies renouvelables

La géographie mondiale crée des avantages naturels : régions montagneuses pour l'hydroélectricité, plaines côtières pour l'éolien, territoires ensoleillés pour le solaire.

### 3. Insights Clés

**Disparités Géographiques :**
- Certains pays dominent la production grâce à des avantages géographiques spécifiques
- Les pays développés montrent des mix énergétiques plus diversifiés
- Les pays en développement dépendent souvent d'une seule source principale

**Évolution Temporelle :**
- L'énergie éolienne connaît la croissance la plus rapide ces dernières années
- Le solaire photovoltaïque se développe progressivement avec la baisse des coûts
- L'hydroélectricité montre une stabilité relative mais une vulnérabilité climatique
- L'inégalité entre pays persiste dans l'adoption des technologies

**Modèles de Mix Énergétique :**
- L'hydroélectricité domine à l'échelle mondiale
- La plupart des pays se spécialisent dans un ou deux types d'énergie
- Les coûts technologiques baissent pour l'éolien et le solaire
- L'infrastructure de réseau limite l'intégration dans certaines régions

### 4. Implications et Recommandations

**Pour les Décideurs Politiques :**
- Développer des lignes de transmission connectant les régions à fort potentiel
- Établir des incitations financières pour les régions en retard
- Diversifier le mix énergétique pour réduire la dépendance climatique
- Accélérer le développement des énergies complémentaires

**Pour les Investisseurs :**
- Opportunités de croissance dans les régions sous-utilisées
- Potentiel d'expansion solaire dans les régions ensoleillées
- Projets éoliens offshore offrant des avantages d'échelle
- Solutions de stockage d'énergie critiques pour les sources intermittentes

---

## Informations sur les Données <a name="informations-sur-les-données"></a>

### Source

**Jeu de Données :** Production Annuelle d'Électricité Renouvelable  
**Éditeur :** Our World in Data  
**Licence :** Données ouvertes  
**Fréquence de Mise à Jour :** Annuelle

### Caractéristiques du Jeu de Données

- Format : Excel (.xlsx)
- Taille : Données de plus de 100 pays sur plusieurs années
- Encodage : UTF-8
- Valeurs Manquantes : Gérées avec des stratégies de remplissage
- Couverture Géographique : Mondiale avec codes ISO des pays

### Colonnes de Données

| Nom de Colonne | Description | Type | Unités |
|---|---|---|---|
| Country | Nom du pays | String | - |
| Code | Code ISO du pays | String | - |
| Year | Année de mesure | Integer | Année |
| Hydro generation - TWh | Production hydroélectrique | Float | TWh |
| Solar generation - TWh | Production solaire | Float | TWh |
| Wind generation - TWh | Production éolienne | Float | TWh |

### Nettoyage & Validation des Données

**Étapes Réalisées :**

1. **Chargement :** Fichier Excel avec encodage UTF-8
2. **Valeurs Manquantes :**
   - Colonnes numériques : remplies avec 0 (indiquant aucune production)
   - Colonnes de texte : conservées telles quelles
3. **Transformation des Données :**
   - Renommage des colonnes pour la cohérence
   - Conversion des types de données
   - Calcul du total mondial par agrégation des pays
4. **Validation :**
   - Vérification des valeurs négatives
   - Confirmation de la cohérence des noms de pays
   - Vérification de la complétude de la plage d'années
5. **Ingénierie des Caractéristiques :**
   - Création de la variable production_totale_twh
   - Calcul des totaux par pays et par année
   - Préparation des données pour la visualisation

**Hypothèses & Mises en Garde :**
- Données manquantes interprétées comme production nulle
- Focus sur les trois principales sources renouvelables
- Données annuelles ne capturant pas la variabilité saisonnière

---

## Fonctionnalités & Visualisations <a name="fonctionnalités--visualisations"></a>

### Onglet 1 : Vue Globale

**Visualisations Géographiques Interactives**

- **Carte Choroplèthe Mondiale**
  - Intensité de production par pays avec codes ISO
  - Infobulles avec valeurs de production
  - Échelle de couleurs : Viridis (contraste élevé)
  - Curseur d'année pour l'exploration temporelle

**Tableaux de Bord Métriques**
- 5 KPIs principaux mis à jour en temps réel
- Croissance mondiale calculée automatiquement
- Statistiques synthétiques sur la période analysée

### Onglet 2 : Analyse par Pays

**Analyse Détailée par Nation**

- **Sélection Interactive du Pays :** Choix parmi tous les pays disponibles
- **Statistiques Complètes :** Totaux, moyennes, maximums, minimums
- **Graphiques de Tendance :** Évolution temporelle de chaque source
- **Mix Énergétique :** Répartition des sources pour l'année la plus récente
- **Détails par Source :** Analyse spécifique hydro/éolien/solaire

### Onglet 3 : Comparaison entre Pays

**Analyse Comparative Avancée**

- **Comparaison Multi-Pays :** Jusqu'à 10 pays simultanément
- **Types de Graphiques :** Barres groupées ou empilées
- **Sélection d'Énergies :** Filtrage par type de source
- **Tableaux de Données :** Valeurs absolues et pourcentages
- **Analyse des Pourcentages :** Détection des énergies dominantes

### Fonctionnalités Avancées

**Treemap de Distribution Mondiale**
- Vue hiérarchique Monde → Pays → Types d'Énergie
- Zoom interactif par clic
- Encodage couleur par intensité de production

**Analyse Filtrée**
- Filtres multi-critères : années, pays, types d'énergie
- Visualisations dynamiques s'adaptant aux filtres
- Export des données filtrées

**Insights Automatisés**
- Détection des leaders de production
- Analyse de la dominance énergétique
- Recommandations stratégiques basées sur les données

### Filtres de la Barre Latérale

**Exploration Dynamique des Données**

- Curseur de Plage d'Années : Sélection de période temporelle
- Sélection Multi-Pays : Focus sur zones géographiques
- Sélection Multi-Énergies : Filtrage par sources spécifiques
- Mises à Jour en Temps Réel : Tous les graphiques répondent instantanément

### Métriques du Tableau de Bord

**Indicateurs Clés de Performance**

- Production Totale (TWh)
- Nombre de Pays Analysés
- Types d'Énergie Suivis
- Production Annuelle Moyenne
- Années Couvertes
- Taux de Croissance (%)

---

## Carnet de Bord du Projet

Ce journal retrace l'avancement du projet "Production d'Énergies Renouvelables dans le Monde", de la phase de conception à l'implémentation finale du tableau de bord Streamlit.

### Phase Initiale : Définition et Préparation (Semaine 1)
| Date | Tâche Principale | Problèmes Rencontrés / Défis | Solutions Apportées |
|---|---|---|---|
| Jour 1-2 | Cadrage du Projet & Choix des Indicateurs | Déficit d'expertise (Auto-Critique) : Difficulté à identifier immédiatement les indicateurs clés de performance (KPIs) pertinents pour une analyse de la transition énergétique mondiale. | Recherche Analytique : Lecture d'articles spécialisés (IRENA, AIE, Our World in Data) pour établir les indicateurs fondamentaux (Croissance annuelle, Mix énergétique, Production cumulée). |
| Jour 3 | Acquisition et Nettoyage du Dataset | Problème de cohérence (Étape critique) : Détection d'erreurs dans le fichier Excel (modern-renewable-energy-consumption.xlsx), notamment des valeurs 0.00 ou NaN dans la ligne 'World', ce qui rendait les KPIs mondiaux inutilisables. | Ingénierie des données : Implémentation d'une logique de recalcul systématique dans la fonction nettoyer_et_preparer_donnees. La ligne 'World' est désormais agrégée par sommation de tous les pays, garantissant l'intégrité des métriques mondiales. |
| Jour 4 | Structure du Code et Modélisation | Surcharge de l'exemple : L'exemple initial (France) contenait des éléments trop complexes ou non applicables (coordonnées régionales, fonctions 3D spécifiques). | Simplification Modulaire : Abandon des fonctions non pertinentes et adoption d'une structure modulaire simple (Chargement → Préparation → Visualisation), rendant le code plus lisible et adapté aux objectifs |

### Phase de Développement : Visualisation et Problèmes Techniques (Semaine 2)
| Date | Tâche Principale | Problèmes Rencontrés / Défis | Solutions Apportées |
|---|---|---|---|
| Jour 5 | Implémentation de la Carte Choroplèthe | Problème de géolocalisation : Manque des coordonnées géographiques pour chaque pays pour la cartographie | Solution Plotly : Utilisation de la librairie Plotly Express avec la colonne code_iso (ISO-3). Plotly gère les polygones frontaliers en interne, contournant la nécessité de fournir des fichiers GeoJSON manuellement. |
| Jour 6 | Développement de l'Analyse Détaillée (Onglet 2) | Répétition du code : Nécessité d'afficher les tendances (Hydro, Solaire, Éolien) individuellement et de calculer les stats (Moyenne, Max) pour chacun. | Factorisation : Création de la fonction générique creer_graphe_tendance qui accepte le nom de la colonne comme argument, réduisant la taille du code et facilitant l'ajout de futures sources d'énergie. |
| Jour 7 | Création du Mix et de la Comparaison | Incohérence des données : Erreur ValueError ou KeyError lors de l'utilisation de df.melt ou px.bar due à des problèmes de majuscules (pays vs Pays). | Normalisation : Correction du code pour uniformiser la casse des colonnes utilisées dans les graphiques Plotly (ex. : df_sources.rename(columns={'pays': 'Pays'})). |

### Phase Finale : Valorisation des Résultats et Expérience Utilisateur
| Date | Tâche Principale | Problèmes Rencontrés / Défis | Solutions Apportées |
|---|---|---|---|
| Jour 8-9 | Finalisation de l'Ergonomie et de la Navigation Applicative | Dépendance des widgets : Le calcul des KPIs dépendait de variables non encore définies (annee_carte), causant un NameError au lancement du script. | Réorganisation du flux : Déplacement des calculs de KPIs dépendant des sliders après la définition des sliders Streamlit, assurant une exécution séquentielle correcte du script. |
| Jour 10 | Amélioration de l'Analyse Périodique | Amélioration de l'interprétation : Nécessité de montrer la robustesse des données au-delà de la simple tendance. | Ajout de Métriques Avancées : Intégration du calcul des statistiques pour la période sélectionnée (Total cumulé, Maximum/Minimum avec l'année du record), enrichissant la partie interprétative du rapport. |
| Jour 11 | Documentation du Rapport | Objectif : Rédiger un README.md et un carnet de bord | Synthèse : Traduction et adaptation du modèle académique de README.md pour refléter les défis et succès spécifiques au projet mondial. |


