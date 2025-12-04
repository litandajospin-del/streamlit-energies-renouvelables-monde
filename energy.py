import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

# --- CONFIGURATION INITIALE DE LA PAGE ---

st.set_page_config(
    page_title="Production Énergétique Mondiale - Tableau de Bord",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Masquer le pied de page Streamlit
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# Style personnalisé
st.markdown("""
<style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(135deg, #1f7e3f 0%, #4caf50 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5em;
    }
    .subtitle {
        font-size: 1.3em;
        color: #2e7d32;
        margin-bottom: 2em;
        font-weight: 500;
    }
    .hook {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 2em;
        border-radius: 0.8em;
        border-left: 5px solid #1f7e3f;
        margin-bottom: 2em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #1a1a1a;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1.5em;
        border-radius: 0.8em;
        border-left: 4px solid #4caf50;
        margin: 1em 0;
    }
    .insight-box {
        background-color: #fff3e0;
        padding: 1.5em;
        border-radius: 0.8em;
        border-left: 4px solid #ff9800;
        margin: 1em 0;
    }
    h2 {
        color: #1f7e3f;
        border-bottom: 2px solid #4caf50;
        padding-bottom: 0.5em;
    }
    h3 {
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE CHARGEMENT ET NETTOYAGE DES DONNÉES ---

@st.cache_data
def charger_donnees():
    """Charge les données de production d'énergie renouvelable à partir du fichier Excel."""
    try:
        chemin_fichier = 'modern-renewable-energy-consumption.xlsx' 
        df = pd.read_excel(chemin_fichier)
        return df
    except FileNotFoundError:
        st.error(f"❌ Erreur: Le fichier {chemin_fichier} n'a pas été trouvé. Veuillez vérifier le nom ou le chemin.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        return None

@st.cache_data
def nettoyer_et_preparer_donnees(df):
    """
    Nettoie, renomme, convertit les colonnes et RECALCULE le total mondial 
    en sommant tous les pays pour garantir des KPIs non nuls.
    """
    if df is None:
        return None
    
    # 1. Renommer les colonnes et convertir les types
    # La colonne "Autres renouvelables" est retirée du renommage
    df_nettoye = df.rename(columns={
        'Country': 'pays', 'Code': 'code_iso', 'Year': 'annee',
        'Hydro generation - TWh': 'hydro_twh', 'Solar generation - TWh': 'solaire_twh',
        'Wind generation - TWh': 'eolien_twh',
    }, errors='ignore').copy()
    
    df_nettoye['annee'] = pd.to_numeric(df_nettoye['annee'], errors='coerce').astype('Int64')
    
    # Définir les colonnes de production uniquement avec les colonnes confirmées (Hydro, Solaire, Éolien)
    colonnes_production = ['hydro_twh', 'solaire_twh', 'eolien_twh']
    
    # On filtre les colonnes existantes au cas où une source soit totalement absente
    colonnes_production_existantes = [col for col in colonnes_production if col in df_nettoye.columns]
    
    for col in colonnes_production_existantes:
        df_nettoye[col] = pd.to_numeric(df_nettoye[col], errors='coerce')
        
    # Créer une colonne de production totale
    df_nettoye['production_totale_twh'] = df_nettoye[colonnes_production_existantes].sum(axis=1)
    
    # Nettoyer les lignes essentielles
    df_nettoye = df_nettoye.dropna(subset=['code_iso', 'annee']).copy()
    
    # 4. CRÉATION DU TOTAL MONDIAL PAR CALCUL 
    df_pays_seuls = df_nettoye[df_nettoye['pays'] != 'World'].copy()
    
    # Préparer le dictionnaire d'agrégation pour le total mondial
    aggregation_dict = {col: 'sum' for col in colonnes_production_existantes}
    aggregation_dict['production_totale_twh'] = 'sum'
    
    df_mondial_calcule = df_pays_seuls.groupby('annee').agg(aggregation_dict).reset_index()
    
    df_mondial_calcule['pays'] = 'World'
    df_mondial_calcule['code_iso'] = 'WLD'
    
    # Concaténation
    df_nettoye = df_nettoye[df_nettoye['pays'] != 'World'].copy()
    df_final = pd.concat([df_nettoye, df_mondial_calcule], ignore_index=True)
    
    return df_final

# --- FONCTIONS DE VISUALISATION PLOTLY ---

@st.cache_data
def creer_carte_mondiale(df_filtre, annee_selectionnee):
    """Crée une carte choroplèthe de la production totale par pays pour une année donnée."""
    df_annee = df_filtre[df_filtre['annee'] == annee_selectionnee]
    df_carte = df_annee.groupby(['pays', 'code_iso'])['production_totale_twh'].sum().reset_index()
    df_carte = df_carte[df_carte['pays'] != 'World']
    
    fig = px.choropleth(df_carte, locations="code_iso", locationmode='ISO-3', color="production_totale_twh",
                        hover_name="pays", color_continuous_scale=px.colors.sequential.Viridis,
                        title=f"Production Totale d'Énergies Renouvelables dans le Monde ({annee_selectionnee})",
                        labels={'production_totale_twh': 'Production Totale (TWh)'})
    fig.update_geos(showframe=False, showcoastlines=False, showland=True, landcolor="lightgray", projection_type="natural earth")
    fig.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})
    return fig

@st.cache_data
def creer_graphe_tendance(df_filtre, pays_selectionne, colonne_data, titre, couleur):
    """Crée un graphique linéaire générique pour une colonne spécifique (Hydro, Solar, etc.) d'un pays."""
    
    df_pays = df_filtre[df_filtre['pays'] == pays_selectionne].sort_values('annee')
    
    if colonne_data not in df_pays.columns:
        return None
    
    fig = px.line(df_pays,
                  x='annee',
                  y=colonne_data,
                  markers=True,
                  title=f"{titre} pour {pays_selectionne}",
                  labels={colonne_data: 'Production (TWh)', 'annee': 'Année'},
                  color_discrete_sequence=[couleur]
                 )
    
    fig.update_layout(hovermode="x unified", template='plotly_white')
    return fig

@st.cache_data
def creer_mix_energie_pays(df_filtre, pays_selectionne, annee_max):
    """Crée un graphique à barres montrant le mix énergétique d'un pays pour l'année la plus récente."""
    
    df_mix_line = df_filtre[(df_filtre['pays'] == pays_selectionne) & 
                            (df_filtre['annee'] == annee_max)]
    
    if df_mix_line.empty: return None
    
    # Sélectionner toutes les colonnes de TWh (UNIQUEMENT Hydro, Solaire, Eolien)
    colonnes_twh = ['hydro_twh', 'solaire_twh', 'eolien_twh']
    colonnes_twh_existantes = [col for col in colonnes_twh if col in df_mix_line.columns]
    
    df_mix = df_mix_line[colonnes_twh_existantes].T.reset_index()
    df_mix.columns = ['type_energie', 'production_twh']
    
    # Nettoyer les noms et définir les couleurs
    couleurs_map = {'Hydro': '#2196f3', 'Solaire': '#ff9800', 'Eolien': '#4caf50'}
    df_mix['type_energie'] = df_mix['type_energie'].str.replace('_twh', '').str.title()
    df_mix = df_mix[df_mix['production_twh'] > 0]
    
    if df_mix.empty: return None
    
    fig = px.bar(df_mix, x='type_energie', y='production_twh', color='type_energie',
                  title=f"Mix Énergétique Renouvelable au {pays_selectionne} en {annee_max}",
                  labels={'production_twh': 'Production (TWh)', 'type_energie': 'Type d\'Énergie'},
                  color_discrete_map={k.title(): v for k, v in couleurs_map.items()})
    
    fig.update_layout(template='plotly_white')
    return fig

@st.cache_data
def creer_comparaison_pays(df, pays_selectionnes, annee_comparaison, energies_selectionnees, type_graphique="group"):
    """Crée un graphique en colonnes pour comparer les pays selon les types d'énergie sélectionnés."""
    
    # Filtrer les données
    df_comparaison = df[(df['pays'].isin(pays_selectionnes)) & 
                        (df['annee'] == annee_comparaison)].copy()
    
    if df_comparaison.empty:
        return None, None
    
    # Préparer les données pour le graphique
    data_list = []
    data_list_pourcent = []
    
    for index, row in df_comparaison.iterrows():
        # Calculer le total pour ce pays
        total_pays = 0
        valeurs_energies = {}
        
        for energie in energies_selectionnees:
            if energie in row and pd.notna(row[energie]):
                valeur = row[energie] if row[energie] > 0 else 0
                valeurs_energies[energie] = valeur
                total_pays += valeur
            else:
                valeurs_energies[energie] = 0
        
        # Ajouter les données absolues
        for energie in energies_selectionnees:
            valeur = valeurs_energies[energie]
            # Convertir le nom de l'énergie pour l'affichage
            nom_energie = energie.replace('_twh', '').title()
            data_list.append({
                'Pays': row['pays'],
                'Type d\'énergie': nom_energie,
                'Production (TWh)': valeur,
                'Pourcentage (%)': (valeur / total_pays * 100) if total_pays > 0 else 0
            })
        
        # Ajouter les données en pourcentage
        for energie in energies_selectionnees:
            valeur = valeurs_energies[energie]
            pourcentage = (valeur / total_pays * 100) if total_pays > 0 else 0
            nom_energie = energie.replace('_twh', '').title()
            data_list_pourcent.append({
                'Pays': row['pays'],
                'Type d\'énergie': nom_energie,
                'Pourcentage (%)': pourcentage,
                'Production (TWh)': valeur
            })
    
    if not data_list:
        return None, None
    
    df_plot = pd.DataFrame(data_list)
    df_plot_pourcent = pd.DataFrame(data_list_pourcent)
    
    # Définir les couleurs par type d'énergie
    couleurs_map = {'Hydro': '#2196f3', 'Solaire': '#ff9800', 'Eolien': '#4caf50'}
    
    # Créer le graphique selon le type choisi
    if type_graphique == "empile":
        barmode = "stack"
        title = f"Comparaison des pays en {annee_comparaison} - Barres Empilées (TWh)"
        
        # Créer un deuxième graphique avec les pourcentages
        title_pourcent = f"Répartition des énergies par pays en {annee_comparaison} - Parts (%)"
        
        fig = px.bar(df_plot, 
                     x='Pays', 
                     y='Production (TWh)', 
                     color='Type d\'énergie',
                     barmode=barmode,
                     title=title,
                     color_discrete_map=couleurs_map,
                     labels={'Production (TWh)': 'Production (TWh)'},
                     hover_data=['Pourcentage (%)'])
        
        # Créer un graphique pour les pourcentages
        fig_pourcent = px.bar(df_plot_pourcent, 
                              x='Pays', 
                              y='Pourcentage (%)', 
                              color='Type d\'énergie',
                              barmode='stack',
                              title=title_pourcent,
                              color_discrete_map=couleurs_map,
                              labels={'Pourcentage (%)': 'Part (%)'},
                              hover_data=['Production (TWh)'])
        
        fig_pourcent.update_layout(
            xaxis_title="Pays",
            yaxis_title="Part (%)",
            template='plotly_white',
            hovermode="x unified",
            legend_title="Type d'énergie",
            yaxis=dict(ticksuffix="%", range=[0, 100])
        )
        
        return fig, fig_pourcent
        
    else:
        barmode = "group"
        title = f"Comparaison des pays en {annee_comparaison} - Barres Groupées"
        
        fig = px.bar(df_plot, 
                     x='Pays', 
                     y='Production (TWh)', 
                     color='Type d\'énergie',
                     barmode=barmode,
                     title=title,
                     color_discrete_map=couleurs_map,
                     labels={'Production (TWh)': 'Production (TWh)'})
        
        fig.update_layout(
            xaxis_title="Pays",
            yaxis_title="Production (TWh)",
            template='plotly_white',
            hovermode="x unified",
            legend_title="Type d'énergie"
        )
        
        return fig, None

@st.cache_data
def creer_tableau_pourcentages(df, pays_selectionnes, annee_comparaison, energies_selectionnees):
    """Crée un tableau des pourcentages pour chaque pays et chaque type d'énergie."""
    
    # Filtrer les données
    df_comparaison = df[(df['pays'].isin(pays_selectionnes)) & 
                        (df['annee'] == annee_comparaison)].copy()
    
    if df_comparaison.empty:
        return None
    
    # Préparer les données pour le tableau
    tableau_data = []
    
    for index, row in df_comparaison.iterrows():
        pays = row['pays']
        total_pays = 0
        valeurs = {}
        
        # Récupérer les valeurs
        for energie in energies_selectionnees:
            if energie in row and pd.notna(row[energie]):
                valeur = row[energie] if row[energie] > 0 else 0
                valeurs[energie] = valeur
                total_pays += valeur
            else:
                valeurs[energie] = 0
        
        # Calculer les pourcentages
        pourcentages = {}
        for energie in energies_selectionnees:
            pourcentage = (valeurs[energie] / total_pays * 100) if total_pays > 0 else 0
            nom_energie = energie.replace('_twh', '').title()
            pourcentages[nom_energie] = pourcentage
        
        # Ajouter une ligne au tableau
        ligne = {'Pays': pays, 'Total (TWh)': total_pays}
        ligne.update(pourcentages)
        tableau_data.append(ligne)
    
    if not tableau_data:
        return None
    
    df_tableau = pd.DataFrame(tableau_data)
    
    # Trier par total décroissant
    df_tableau = df_tableau.sort_values('Total (TWh)', ascending=False)
    
    return df_tableau

@st.cache_data
def creer_tableau_valeurs_absolues(df, pays_selectionnes, annee_comparaison, energies_selectionnees):
    """Crée un tableau des valeurs absolues pour chaque pays et chaque type d'énergie."""
    
    # Filtrer les données
    df_comparaison = df[(df['pays'].isin(pays_selectionnes)) & 
                        (df['annee'] == annee_comparaison)].copy()
    
    if df_comparaison.empty:
        return None
    
    # Préparer les données pour le tableau
    tableau_data = []
    
    for index, row in df_comparaison.iterrows():
        pays = row['pays']
        total_pays = 0
        valeurs = {}
        
        # Récupérer les valeurs
        for energie in energies_selectionnees:
            if energie in row and pd.notna(row[energie]):
                valeur = row[energie] if row[energie] > 0 else 0
                valeurs[energie] = valeur
                total_pays += valeur
            else:
                valeurs[energie] = 0
        
        # Ajouter une ligne au tableau
        ligne = {'Pays': pays, 'Total (TWh)': total_pays}
        for energie in energies_selectionnees:
            nom_energie = energie.replace('_twh', '').title()
            ligne[nom_energie] = valeurs[energie]
        
        tableau_data.append(ligne)
    
    if not tableau_data:
        return None
    
    df_tableau = pd.DataFrame(tableau_data)
    
    # Trier par total décroissant
    df_tableau = df_tableau.sort_values('Total (TWh)', ascending=False)
    
    return df_tableau

@st.cache_data
def creer_treemap_distribution(df):
    """Crée un Treemap montrant la distribution de la part énergétique par pays."""
    
    # Filtrer les données pour l'année la plus récente
    annee_max = df['annee'].max()
    df_annee = df[df['annee'] == annee_max].copy()
    
    # Préparer les données pour le treemap - nous avons besoin de fondre les colonnes d'énergie
    colonnes_energie = ['hydro_twh', 'solaire_twh', 'eolien_twh']
    colonnes_energie_existantes = [col for col in colonnes_energie if col in df_annee.columns]
    
    # Créer une version fondue du dataframe pour avoir une colonne type_energie
    id_vars = ['pays', 'code_iso', 'annee', 'production_totale_twh']
    df_fondu = df_annee.melt(
        id_vars=id_vars,
        value_vars=colonnes_energie_existantes,
        var_name='type_energie',
        value_name='production_twh'
    )
    
    # Nettoyer les noms des types d'énergie
    df_fondu['type_energie'] = df_fondu['type_energie'].str.replace('_twh', '').str.title()
    
    # Filtrer les lignes avec production positive
    df_fondu = df_fondu[df_fondu['production_twh'] > 0]
    
    # Créer la structure hiérarchique : Racine -> Pays -> Types d'Énergie
    etiquette_racine = 'Monde'
    
    # Préparer les listes d'étiquettes et de parents
    etiquettes = [etiquette_racine]
    parents = ['']
    valeurs = [df_fondu['production_twh'].sum()]
    
    # Ajouter les pays comme niveau intermédiaire
    for pays in df_fondu['pays'].unique():
        if pays != 'World':  # Exclure World pour éviter la duplication
            etiquettes.append(pays)
            parents.append(etiquette_racine)
            total_pays = df_fondu[df_fondu['pays'] == pays]['production_twh'].sum()
            valeurs.append(total_pays)
    
    # Ajouter les types d'énergie sous les pays
    for pays in df_fondu['pays'].unique():
        if pays != 'World':
            for type_energie in df_fondu[df_fondu['pays'] == pays]['type_energie'].unique():
                etiquettes.append(f"{type_energie}")
                parents.append(pays)
                valeur = df_fondu[(df_fondu['pays'] == pays) & 
                                  (df_fondu['type_energie'] == type_energie)]['production_twh'].sum()
                valeurs.append(valeur)
    
    fig = go.Figure(go.Treemap(
        labels=etiquettes,
        parents=parents,
        values=valeurs,
        marker=dict(colorscale='Greens', cmid=np.median(valeurs)),
        hovertemplate='<b>%{label}</b><br>Production: %{value:,.0f} TWh<extra></extra>',
        textinfo="label+value"
    ))
    
    fig.update_layout(
        title=f"Distribution de l'Énergie Renouvelable par Pays ({annee_max})",
        height=600,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    return fig

# --------------------------------------------------------------------------------
# LOGIQUE PRINCIPALE DE L'APPLICATION
# --------------------------------------------------------------------------------

# CHARGEMENT DES DONNÉES
with st.spinner("Chargement des données..."):
    df_brut = charger_donnees()
    df_principal = nettoyer_et_preparer_donnees(df_brut)

if df_principal is None or df_principal.empty:
    st.error("❌ Le jeu de données est vide après le nettoyage. Veuillez vérifier le contenu de votre fichier Excel.")
    st.stop()

# PRÉPARATION DES VALEURS CLÉS GLOBALES
annees_disponibles = sorted(df_principal['annee'].unique())
pays_disponibles = sorted([p for p in df_principal['pays'].unique() if p != 'World'])
annee_max = df_principal['annee'].max()
annee_min = df_principal['annee'].min()

# --- DÉFINITION DES WIDGETS STREAMLIT (SIDEBAR) ---

st.sidebar.header("Contrôles Globaux")

annee_carte = st.sidebar.select_slider(
    "Année de Référence (Carte et Métriques)",
    options=annees_disponibles,
    value=annee_max
)

# --- AFFICHAGE DU CONTENU ---

# TITRES PRINCIPAUX
st.markdown("""
<div class="main-title">
    Production d'Énergies Renouvelables dans le Monde
</div>
<div class="subtitle">
    Visualisation Interactive de la Transition Mondiale vers les Énergies Renouvelables
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hook">
    <h3>Le Défi : Cartographier la Transition Énergétique Mondiale</h3>
    <p><strong>Question Centrale :</strong> Les pays peuvent-ils atteindre un développement équilibré des énergies renouvelables tout en maintenant la stabilité du réseau ?</p>
    <p>D'ici 2050, le monde doit atteindre la neutralité carbone. Le succès dépend de la compréhension de l'endroit où l'énergie renouvelable est produite, des technologies dominantes et des lacunes existantes. Ce tableau de bord révèle des années de données de production mondiales pour répondre à la question : où en sommes-nous, et où devons-nous investir ensuite ?</p>
    <p><strong>Ce que vous découvrirez :</strong></p>
    <ul>
        <li>Les leaders mondiaux de la production</li>
        <li>L'évolution du mix énergétique au fil du temps</li>
        <li>Les avantages géographiques moteurs du déploiement des énergies renouvelables</li>
        <li>Les priorités d'investissement pour la prochaine décennie</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- SECTION DES MÉTRIQUES CLÉS (KPIs) ---

st.header("Aperçu Mondial 📊")

col1, col2, col3, col4, col5 = st.columns(5)

# Calcul des métriques mondiales
df_mondial = df_principal[df_principal['pays'] == 'World'].copy()

if df_mondial.empty or df_mondial['annee'].empty:
    prod_min_annee = 0
    prod_max_annee = 0
    prod_mondiale_annee_ref = 0
    prod_moyenne_annuelle = 0
else:
    annee_mondiale_min = df_mondial['annee'].min()
    annee_mondiale_max = df_mondial['annee'].max()
    
    prod_min_annee = df_mondial[df_mondial['annee'] == annee_mondiale_min]['production_totale_twh'].values[0]
    prod_max_annee = df_mondial[df_mondial['annee'] == annee_mondiale_max]['production_totale_twh'].values[0]
    
    prod_ref_serie = df_mondial[df_mondial['annee'] == annee_carte]['production_totale_twh']
    prod_mondiale_annee_ref = prod_ref_serie.values[0] if prod_ref_serie.size > 0 else 0
    
    prod_moyenne_annuelle = df_mondial['production_totale_twh'].mean()

taux_croissance_mondiale = 0
if prod_min_annee > 0 and prod_max_annee > 0:
    taux_croissance_mondiale = ((prod_max_annee / prod_min_annee) - 1) * 100
    
nb_pays_analyses = len(pays_disponibles) 
nb_types_energie = 3 
annees_couvertes = annee_max - annee_min + 1

with col1:
    st.metric(
        label=f"Production totale (TWh) - {annee_carte}",
        value=f"{prod_mondiale_annee_ref:,.0f}".replace(',', ' '),
        delta=f"Croissance de {taux_croissance_mondiale:,.1f} % (Total)" if taux_croissance_mondiale != 0 else None
    )

with col2:
    st.metric(label="Pays analysés", value=f"{nb_pays_analyses}")

with col3:
    st.metric(label="Types d'énergie suivis", value=f"{nb_types_energie} sources")

with col4:
    if pd.isna(prod_moyenne_annuelle):
        valeur_moyenne_affichage = "N/A"
    else:
        valeur_moyenne_affichage = f"{prod_moyenne_annuelle:,.0f}".replace(',', ' ')
    st.metric(label=f"Moyenne annuelle (TWh) - Total", value=valeur_moyenne_affichage)

with col5:
    st.metric(label="Années couvertes", value=f"{annees_couvertes} ans ({annee_min} - {annee_max})")

# --- CARTE MONDIALE ---
st.header("Carte de Production Mondiale 🌍")

st.markdown(f"""
**Objectif :** Identifier les pays qui contribuent le plus à la production mondiale d'énergies renouvelables en **{annee_carte}**. 
Les pays grisés n'ont pas de données pour cette année dans le jeu de données.
""")

fig_carte = creer_carte_mondiale(df_principal, annee_carte)
st.plotly_chart(fig_carte, use_container_width=True)

st.divider()

# --- ONGLETS POUR ANALYSE ET COMPARAISON ---
tab1, tab2 = st.tabs(["📈 Analyse Pays", "⚖️ Comparaison"])

with tab1:
    st.header("Analyse par Pays 📈")
    
    # Sélection du pays (sans World)
    pays_selectionne_options = pays_disponibles
    
    col_select_pays, col_select_periode = st.columns([1, 2])
    
    with col_select_pays:
        pays_selectionne = st.selectbox(
            "Sélectionner un Pays",
            options=pays_selectionne_options,
            index=0 if pays_disponibles else 0,
            key="pays_analyse"
        )
    
    if pays_selectionne:
        # Sélection de la période d'analyse
        with col_select_periode:
            col_periode1, col_periode2 = st.columns(2)
            
            with col_periode1:
                annee_debut = st.selectbox(
                    "Année de début",
                    options=annees_disponibles,
                    index=0,
                    key="annee_debut_analyse"
                )
            
            with col_periode2:
                annee_fin = st.selectbox(
                    "Année de fin",
                    options=annees_disponibles,
                    index=len(annees_disponibles)-1,
                    key="annee_fin_analyse"
                )
        
        # S'assurer que l'année de fin est >= année de début
        if annee_debut > annee_fin:
            st.warning("L'année de fin doit être supérieure ou égale à l'année de début.")
            annee_fin = annee_debut
        
        # Filtrer les données pour le pays et la période sélectionnés
        df_pays_periode = df_principal[(df_principal['pays'] == pays_selectionne) & 
                                       (df_principal['annee'] >= annee_debut) & 
                                       (df_principal['annee'] <= annee_fin)].copy()
        
        if not df_pays_periode.empty:
            # Calcul des statistiques pour la période
            total_periode = df_pays_periode['production_totale_twh'].sum()
            moyenne_periode = df_pays_periode['production_totale_twh'].mean()
            max_periode = df_pays_periode['production_totale_twh'].max()
            min_periode = df_pays_periode['production_totale_twh'].min()
            annee_max_periode = df_pays_periode.loc[df_pays_periode['production_totale_twh'].idxmax(), 'annee']
            annee_min_periode = df_pays_periode.loc[df_pays_periode['production_totale_twh'].idxmin(), 'annee']
            
            # Calcul par type d'énergie
            stats_energies = {}
            for energie in ['hydro_twh', 'solaire_twh', 'eolien_twh']:
                if energie in df_pays_periode.columns:
                    stats_energies[energie] = {
                        'total': df_pays_periode[energie].sum(),
                        'moyenne': df_pays_periode[energie].mean(),
                        'max': df_pays_periode[energie].max(),
                        'min': df_pays_periode[energie].min()
                    }
            
            # Afficher les statistiques
            st.subheader(f"Statistiques pour {pays_selectionne} ({annee_debut}-{annee_fin})")
            
            # Métriques principales
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            with col_met1:
                st.metric(
                    label="Production totale (TWh)",
                    value=f"{total_periode:,.0f}".replace(',', ' ')
                )
            
            with col_met2:
                st.metric(
                    label="Moyenne annuelle (TWh)",
                    value=f"{moyenne_periode:,.0f}".replace(',', ' ')
                )
            
            with col_met3:
                st.metric(
                    label=f"Maximum ({annee_max_periode})",
                    value=f"{max_periode:,.0f}".replace(',', ' ')
                )
            
            with col_met4:
                st.metric(
                    label=f"Minimum ({annee_min_periode})",
                    value=f"{min_periode:,.0f}".replace(',', ' ')
                )
            
            # Exemple pour une année spécifique
            st.subheader("Exemple pour une année spécifique")
            annee_exemple = st.select_slider(
                "Sélectionner une année pour voir le détail",
                options=sorted(df_pays_periode['annee'].unique()),
                value=annee_fin,
                key="annee_exemple_analyse"
            )
            
            df_annee_exemple = df_pays_periode[df_pays_periode['annee'] == annee_exemple].iloc[0]
            
            total_annee_exemple = 0
            energies_details = []
            energies_details_pourcent = []
            valeurs_energies = {}
            
            for energie_col, energie_nom in [('hydro_twh', 'Hydro'), ('solaire_twh', 'Solaire'), ('eolien_twh', 'Éolien')]:
                if energie_col in df_annee_exemple and pd.notna(df_annee_exemple[energie_col]):
                    valeur = df_annee_exemple[energie_col]
                    valeurs_energies[energie_nom] = valeur
                    total_annee_exemple += valeur
                    energies_details.append(f"{energie_nom}: {valeur:,.0f} TWh")
            
            # Calculer les pourcentages
            if total_annee_exemple > 0:
                for energie_nom, valeur in valeurs_energies.items():
                    pourcentage = (valeur / total_annee_exemple) * 100
                    energies_details_pourcent.append(f"{energie_nom}: {pourcentage:.1f}%")
            
            st.info(f"**En {annee_exemple}, {pays_selectionne} a produit un total de {total_annee_exemple:,.0f} TWh d'énergies renouvelables.**")
            st.write("**Détail en TWh:** " + " | ".join(energies_details))
            
            if energies_details_pourcent:
                st.write("**Répartition (%):** " + " | ".join(energies_details_pourcent))
            
            # Graphiques de tendance
            st.subheader("Évolution au fil du temps")
            
            col_tendance, col_mix = st.columns(2)
            
            with col_tendance:
                fig_tendance = creer_graphe_tendance(df_pays_periode, pays_selectionne, 'production_totale_twh',
                                                    f"Tendance de la Production Totale Renouvelable au {pays_selectionne}",
                                                    '#1f7e3f')
                if fig_tendance:
                    st.plotly_chart(fig_tendance, use_container_width=True)
            
            with col_mix:
                fig_mix = creer_mix_energie_pays(df_pays_periode, pays_selectionne, annee_fin)
                if fig_mix:
                    st.plotly_chart(fig_mix, use_container_width=True)
                else:
                    st.info(f"Aucune donnée de mix énergétique disponible pour l'année {annee_fin} dans ce pays.")
            
            # Détails par type d'énergie
            st.subheader("Statistiques détaillées par type d'énergie")
            
            if stats_energies:
                cols_energie = st.columns(len(stats_energies))
                
                for idx, (energie_col, stats) in enumerate(stats_energies.items()):
                    energie_nom = energie_col.replace('_twh', '').title()
                    with cols_energie[idx]:
                        st.markdown(f"**{energie_nom}**")
                        st.write(f"Total: {stats['total']:,.0f} TWh")
                        st.write(f"Moyenne: {stats['moyenne']:,.0f} TWh/an")
                        st.write(f"Max: {stats['max']:,.0f} TWh")
                        st.write(f"Min: {stats['min']:,.0f} TWh")
            
            # Graphiques individuels par type d'énergie
            st.subheader("Évolution détaillée des sources d'énergie")
            
            # 🔹 Hydro
            st.markdown("##### 🌊 Production d'hydroélectricité (TWh)")
            fig_hydro = creer_graphe_tendance(df_pays_periode, pays_selectionne, "hydro_twh",
                                            "Production d'hydroélectricité", '#2196f3')
            if fig_hydro:
                st.plotly_chart(fig_hydro, use_container_width=True)
            else:
                st.info("Données d'hydroélectricité non disponibles pour ce pays.")
            
            # 🔹 Wind
            st.markdown("##### 🌬️ Production d'énergie éolienne (TWh)")
            fig_eolien = creer_graphe_tendance(df_pays_periode, pays_selectionne, "eolien_twh",
                                            "Production d'énergie éolienne", '#4caf50')
            if fig_eolien:
                st.plotly_chart(fig_eolien, use_container_width=True)
            else:
                st.info("Données d'énergie éolienne non disponibles pour ce pays.")
            
            # 🔹 Solar
            st.markdown("##### ☀️ Production d'énergie solaire (TWh)")
            fig_solaire = creer_graphe_tendance(df_pays_periode, pays_selectionne, "solaire_twh",
                                              "Production d'énergie solaire", '#ff9800')
            if fig_solaire:
                st.plotly_chart(fig_solaire, use_container_width=True)
            else:
                st.info("Données d'énergie solaire non disponibles pour ce pays.")
        else:
            st.warning(f"Aucune donnée disponible pour {pays_selectionne} sur la période {annee_debut}-{annee_fin}.")

with tab2:
    st.header("Comparaison entre Pays ⚖️")
    
    # Titre comme dans l'image
    st.markdown("### Production par Pays")
    
    # Container avec style similaire à l'image
    with st.container():
        col_config, col_graph = st.columns([1, 3])
        
        with col_config:
            st.markdown("#### Type de visualisation")
            
            # Cases à cocher pour le type de graphique
            type_graphique = st.radio(
                "",
                options=["Barres groupées", "Barres empilées"],
                index=0,
                key="type_graphique_comparaison",
                label_visibility="collapsed"
            )
            
            st.divider()
            
            # Sélection de l'année
            st.markdown("#### Année de comparaison")
            annee_comparaison = st.selectbox(
                "",
                options=annees_disponibles,
                index=len(annees_disponibles)-1,
                key="annee_comparaison",
                label_visibility="collapsed"
            )
            
            st.divider()
            
            # Sélection des énergies
            st.markdown("#### Types d'énergie")
            energies_comparaison = st.multiselect(
                "",
                options=['Hydro', 'Solaire', 'Éolien'],
                default=['Hydro', 'Solaire', 'Éolien'],
                key="energies_comparaison",
                label_visibility="collapsed"
            )
            
            st.divider()
            
            # Sélection des pays
            st.markdown("#### Pays à comparer")
            pays_comparaison = st.multiselect(
                "",
                options=pays_disponibles,
                default=pays_disponibles[:5] if len(pays_disponibles) >= 5 else pays_disponibles,
                key="pays_comparaison",
                label_visibility="collapsed"
            )
        
        with col_graph:
            if pays_comparaison and energies_comparaison:
                # Convertir le type de graphique
                type_graph = "group" if type_graphique == "Barres groupées" else "empile"
                
                # Convertir les noms d'énergie en noms de colonnes
                energies_colonnes = []
                for energie in energies_comparaison:
                    if energie == 'Hydro':
                        energies_colonnes.append('hydro_twh')
                    elif energie == 'Solaire':
                        energies_colonnes.append('solaire_twh')
                    elif energie == 'Éolien':
                        energies_colonnes.append('eolien_twh')
                
                # Créer le graphique de comparaison
                fig_comparaison, fig_pourcent = creer_comparaison_pays(df_principal, pays_comparaison, annee_comparaison, energies_colonnes, type_graph)
                
                if fig_comparaison:
                    # Personnaliser le titre
                    if type_graph == "empile":
                        fig_comparaison.update_layout(
                            title=f"Production par Pays ({annee_comparaison}) - Valeurs Absolues",
                            title_font=dict(size=20, color='#2e7d32'),
                            height=500
                        )
                        
                        # Afficher le graphique des valeurs absolues
                        st.plotly_chart(fig_comparaison, use_container_width=True)
                        
                        # Afficher le graphique des pourcentages
                        if fig_pourcent:
                            fig_pourcent.update_layout(
                                title=f"Répartition des Énergies par Pays ({annee_comparaison}) - Parts Relatives",
                                title_font=dict(size=20, color='#2e7d32'),
                                height=500
                            )
                            st.plotly_chart(fig_pourcent, use_container_width=True)
                        
                        # AFFICHER LES TABLEAUX POUR BARRES EMPILÉES
                        
                        # Tableau des pourcentages
                        st.markdown("### Tableau des Pourcentages par Pays")
                        
                        # Créer le tableau des pourcentages
                        df_tableau_pourcent = creer_tableau_pourcentages(df_principal, pays_comparaison, annee_comparaison, energies_colonnes)
                        
                        if df_tableau_pourcent is not None:
                            # Formater les nombres
                            df_tableau_affichage = df_tableau_pourcent.copy()
                            
                            # Formater les pourcentages avec 1 décimale
                            for col in df_tableau_affichage.columns:
                                if col != 'Pays' and col != 'Total (TWh)':
                                    df_tableau_affichage[col] = df_tableau_affichage[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "0.0%")
                            
                            # Formater le total
                            df_tableau_affichage['Total (TWh)'] = df_tableau_affichage['Total (TWh)'].apply(lambda x: f"{x:,.1f}" if pd.notna(x) else "0.0")
                            
                            st.dataframe(df_tableau_affichage, use_container_width=True, hide_index=True)
                            
                            # Analyse des pourcentages
                            st.markdown("### Analyse des Pourcentages")
                            
                            # Trouver l'énergie dominante pour chaque pays
                            for index, row in df_tableau_pourcent.iterrows():
                                pays = row['Pays']
                                energies_pourcent = {}
                                
                                for energie in energies_comparaison:
                                    if energie in row:
                                        energies_pourcent[energie] = row[energie]
                                
                                if energies_pourcent:
                                    # Trouver l'énergie avec le plus grand pourcentage
                                    energie_dominante = max(energies_pourcent.items(), key=lambda x: x[1])
                                    
                                    # Trouver la deuxième énergie si elle existe
                                    energies_triees = sorted(energies_pourcent.items(), key=lambda x: x[1], reverse=True)
                                    
                                    if len(energies_triees) >= 2:
                                        energie_secondaire = energies_triees[1]
                                        st.write(f"**{pays}**: {energie_dominante[0]} ({energie_dominante[1]:.1f}%) est l'énergie dominante, suivie par {energie_secondaire[0]} ({energie_secondaire[1]:.1f}%)")
                                    else:
                                        st.write(f"**{pays}**: {energie_dominante[0]} ({energie_dominante[1]:.1f}%) est l'énergie dominante")
                        
                    else:
                        # POUR BARRES GROUPÉES
                        fig_comparaison.update_layout(
                            title=f"Production par Pays ({annee_comparaison})",
                            title_font=dict(size=20, color='#2e7d32'),
                            height=500
                        )
                        
                        # Afficher le graphique
                        st.plotly_chart(fig_comparaison, use_container_width=True)
                        
                        # AFFICHER LES TABLEAUX POUR BARRES GROUPÉES
                        
                        # Tableau des valeurs absolues
                        st.markdown("### Tableau des Valeurs Absolues (TWh)")
                        
                        # Créer le tableau des valeurs absolues
                        df_tableau_valeurs = creer_tableau_valeurs_absolues(df_principal, pays_comparaison, annee_comparaison, energies_colonnes)
                        
                        if df_tableau_valeurs is not None:
                            # Formater les nombres
                            df_tableau_valeurs_affichage = df_tableau_valeurs.copy()
                            for col in df_tableau_valeurs_affichage.columns:
                                if col != 'Pays':
                                    df_tableau_valeurs_affichage[col] = df_tableau_valeurs_affichage[col].apply(lambda x: f"{x:,.1f}" if pd.notna(x) else "0.0")
                            
                            st.dataframe(df_tableau_valeurs_affichage, use_container_width=True, hide_index=True)
                else:
                    st.info("Aucune donnée disponible pour la comparaison avec les paramètres sélectionnés.")
            else:
                st.info("Veuillez sélectionner au moins un pays et un type d'énergie pour afficher la comparaison.")

st.divider()

# --- SECTION : TREEMAP DE LA PART ÉNERGÉTIQUE MONDIALE ---

st.header("Treemap de la Distribution Énergétique Mondiale")
st.markdown("""
Cliquez sur les segments pour zoomer/dézoomer. Cette vue hiérarchique montre comment chaque type d'énergie 
contribue à la production mondiale et la répartition par pays au sein de chaque type d'énergie.
""")
fig_treemap = creer_treemap_distribution(df_principal)
st.plotly_chart(fig_treemap, use_container_width=True)

st.divider()

# --- SECTION : ANALYSE DÉTAILLÉE AVEC FILTRES ---

st.header("Analyse Filtrée et Exploration Détaillée")

with st.expander("Afficher les Filtres Avancés", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        plage_annee_detail = st.slider(
            "Sélectionner la Plage Annuelle",
            int(df_principal['annee'].min()),
            int(df_principal['annee'].max()),
            (int(df_principal['annee'].min()), int(df_principal['annee'].max())),
            key="annee_curseur_detaille"
        )
    
    with col2:
        pays_selectionne_detaille = st.multiselect(
            "Pays",
            sorted(pays_disponibles),
            default=sorted(pays_disponibles)[:5],
            key="pays_filtre_detaille"
        )
    
    with col3:
        energie_selectionnee_detaille = st.multiselect(
            "Types d'Énergie",
            ['Hydro', 'Solaire', 'Éolien'],
            default=['Hydro', 'Solaire', 'Éolien'],
            key="energie_filtre_detaille"
        )
    
    # Convertir les noms d'énergie en noms de colonnes
    energies_colonnes_detaille = []
    for energie in energie_selectionnee_detaille:
        if energie == 'Hydro':
            energies_colonnes_detaille.append('hydro_twh')
        elif energie == 'Solaire':
            energies_colonnes_detaille.append('solaire_twh')
        elif energie == 'Éolien':
            energies_colonnes_detaille.append('eolien_twh')
    
    # Appliquer les filtres
    df_filtre_detaille = df_principal[
        (df_principal['annee'] >= plage_annee_detail[0]) &
        (df_principal['annee'] <= plage_annee_detail[1]) &
        (df_principal['pays'].isin(pays_selectionne_detaille))
    ].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tendance de production
        donnees_tendance = df_filtre_detaille.groupby(['annee', 'pays']).agg({
            'production_totale_twh': 'sum'
        }).reset_index()
        
        fig_tendance = px.line(
            donnees_tendance,
            x='annee',
            y='production_totale_twh',
            color='pays',
            markers=True,
            title="Tendance de Production au Fil du Temps",
            labels={'production_totale_twh': 'Production (TWh)', 'annee': 'Année'}
        )
        st.plotly_chart(fig_tendance, use_container_width=True)
    
    with col2:
        # Comparaison des pays
        donnees_pays = df_filtre_detaille.groupby('pays').agg({
            'production_totale_twh': 'sum'
        }).reset_index().sort_values('production_totale_twh', ascending=True)
        
        fig_pays = px.bar(
            donnees_pays,
            x='production_totale_twh',
            y='pays',
            orientation='h',
            title="Production par Pays",
            labels={'production_totale_twh': 'Production (TWh)', 'pays': 'Pays'},
            color='production_totale_twh',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_pays, use_container_width=True)
    
    # Afficher la table de données filtrées
    if len(df_filtre_detaille) > 0:
        st.markdown("### Échantillon de Données Filtrées")
        colonnes_affichage = ['pays', 'annee', 'production_totale_twh'] + energies_colonnes_detaille
        colonnes_affichage = [col for col in colonnes_affichage if col in df_filtre_detaille.columns]
        
        st.dataframe(
            df_filtre_detaille[colonnes_affichage].sort_values(['pays', 'annee'], ascending=[True, False]),
            use_container_width=True,
            hide_index=True
        )

st.divider()

# --- SECTION : CONSTATS CLÉS ---

st.header("Constats Clés des Données")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Leaders de Production")
    
    # Calculer les leaders de production pour l'année la plus récente
    annee_recente = df_principal['annee'].max()
    df_recent = df_principal[df_principal['annee'] == annee_recente]
    
    pays_principaux = df_recent.groupby('pays')['production_totale_twh'].sum().nlargest(5)
    
    for i, (pays, prod) in enumerate(pays_principaux.items(), 1):
        if pays != 'World':
            total_mondial = df_recent[df_recent['pays'] == 'World']['production_totale_twh'].sum()
            pct = (prod / total_mondial * 100) if total_mondial > 0 else 0
            
            st.markdown(f"""
            <div class='success-box'>
            <strong>{i}. {pays}</strong><br>
            {prod:,.0f} TWh ({pct:.1f}% du total mondial)
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("**Constat :** Les cinq premiers pays génèrent une part significative de la production mondiale d'énergies renouvelables.")

with col2:
    st.markdown("#### Dominance du Type d'Énergie")
    
    # Calculer la répartition par type d'énergie pour l'année la plus récente
    energie_principale = {}
    for energie_col, energie_nom in [('hydro_twh', 'Hydro'), ('solaire_twh', 'Solaire'), ('eolien_twh', 'Éolien')]:
        if energie_col in df_recent.columns:
            total_energie = df_recent[energie_col].sum()
            energie_principale[energie_nom] = total_energie
    
    # Trier par production
    energie_principale_trie = dict(sorted(energie_principale.items(), key=lambda x: x[1], reverse=True))
    
    total_global = sum(energie_principale_trie.values())
    
    for i, (energie, prod) in enumerate(energie_principale_trie.items(), 1):
        pct = (prod / total_global * 100) if total_global > 0 else 0
        
        st.markdown(f"""
        <div class='insight-box'>
        <strong>{i}. {energie}</strong><br>
        {prod:,.0f} TWh ({pct:.1f}%)
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("**Constat :** L'énergie hydraulique domine encore largement la production mondiale d'énergies renouvelables.")

st.divider()

# --- SECTION : RECOMMANDATIONS STRATÉGIQUES ---

st.header("Priorités d'Investissement et Perspectives")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Diversifier le Mix Énergétique
    
    La domination de l'hydroélectricité dans de nombreux pays crée une dépendance aux précipitations. 
    Le changement climatique menace la fiabilité de cette source. Actions prioritaires :
    
    - Développer le stockage d'énergie pour les sources intermittentes
    - Investir dans les énergies complémentaires (solaire + éolien)
    - Moderniser les infrastructures hydroélectriques existantes
    """)

with col2:
    st.markdown("""
    ### Accélérer le Déploiement Solaire
    
    Le solaire photovoltaïque affiche un énorme potentiel non exploité dans de nombreuses régions. 
    Des obstacles subsistent dans les coûts initiaux et l'intégration au réseau. Actions prioritaires :
    
    - Subventions pour les installations résidentielles et commerciales
    - Développement de fermes solaires à grande échelle
    - Recherche sur l'efficacité des panneaux solaires
    """)

with col3:
    st.markdown("""
    ### Exploiter le Potentiel Éolien
    
    L'énergie éolienne montre la trajectoire de croissance la plus forte récemment. 
    Les régions côtières et de plaines offrent des conditions optimales. Actions prioritaires :
    
    - Rationaliser les processus d'approbation des parcs éoliens
    - Investir dans l'éolien offshore
    - Développer des réseaux de transmission dédiés
    """)

st.divider()

# --- PIED DE PAGE ---
st.markdown("""
---
### Informations sur le Tableau de Bord
**Source des Données :** ourworldindata.org - Production Annuelle d'Électricité Renouvelable  
**Technologies Utilisées :** Streamlit, Pandas, Plotly  
**Dernière Mise à Jour :** {update_date}
""".format(update_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))