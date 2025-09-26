import streamlit as st
import requests

A_text = """L'ingénieur aime bien résoudre des problèmes en utilisant la méthode scientifique et le raisonnement logique. 
Il est dans la réflexion et est capable de conceptualiser des notions abstraites. C'est une personnalité plutôt introvertie qui aime analyser et savoir.\n
***Points de force*** : compilent les faits, analysent, argumentent rationnellement, formulent des théories, mesurent précisément, résolvent les problèmes logiquement, 
raisonnent, comprennent les éléments techniques, analysent avec l’esprit critique, travaillent à partir de chiffres, de statistiques, et sont précis."""

B_text = """Le cartographe est prudent et organisé. Il a des habitudes bien précises et respecte soigneusement les règles.
Il planifie méticuleusement ce qui doit être fait et se retrouve bien dans les tâches administratif ou son souci du détail est sa fiabilité est valorisé.\n
***Points de force*** : remarquent les défauts, approchent les problèmes pratiquement, vont jusqu’au bout des choses, développent des plans détaillés et des procédures, et envisagent les problèmes sous l’angle du planning."""

C_text = """Le barde aime le contact humain. Il est empathique, relationnel et amicale. Il est expressif et communique bien avec les autres.\n
***Points de force*** : comprennent les difficultés relationnelles, anticipent le ressenti des autres, comprennent intuitivement le ressenti des autres, perçoivent des éléments non verbaux issus du stress, engendrent l’enthousiasme, persuadent, concilient, enseignent, partagent, comprennent les éléments émotionnels, prennent en compte les valeurs."""

D_text = """L'inventeur est un aventurier avec une imagination débordante qui rêve éveillé. C'est un visionnaire qui a toujours des idées très originales.
C'est aussi un revel qui aime bien prendre des risques et se projeter.\n
***Points de force*** : Lisent les signes du changement, voient les choses globalement, reconnaissent les nouvelles possibilités, tolèrent l’ambiguïté, intègrent les idées et les concepts, défient les règles établies, synthétisent les éléments divers en un nouveau tout, inventent des solutions nouvelles, résolvent les problèmes de manière intuitive, intègrent en simultané différents inputs."""


# Define your result_filename and global_results_filename
#result_filename = "results.txt"
#global_results_filename = "global_results.txt"
icon = "Favicon_2x.ico"

#post to database
DATABASE_URL = st.secrets["DATABASE_URL"]
DATABASE_API_KEY = st.secrets["DATABASE_API_KEY"]

def get_organizations_from_database():
    url = f"{DATABASE_URL}/rest/v1/organizations"
    headers = {
        "apikey": DATABASE_API_KEY,
        "Authorization": f"Bearer {DATABASE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            orgs = response.json()
            
            if not orgs:
                st.warning("No organizations found in database")
                return []
            
            names = [org['name'] for org in orgs if org.get("status") == "ongoing"]
            return names
        else:
            st.warning(f"Failed to fetch organizations: {response.status_code}")
            return []
    except Exception as e:
        st.warning(f"Error fetching organizations: {e}")
        return []


def fetch_results_from_database():
    url = f"{DATABASE_URL}/rest/v1/hermann_teams"
    headers = {
        "apikey": DATABASE_API_KEY,
        "Authorization": f"Bearer {DATABASE_API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "select": "user,organisation"
    }
    response = requests.get(url, headers=headers, params=params)
    #print(response.status_code, response.text)
    response.raise_for_status()
    return response.json()

def update_user_evaluation(user, orga, evaluations):
    """
    Updates the 'evaluation' jsonb column for a given user and organisation,
    assuming the row already exists in the Supabase table.
    """
    url = f"{DATABASE_URL}/rest/v1/hermann_teams?user=eq.{user}&organisation=eq.{orga}"
    headers = {
        "apikey": DATABASE_API_KEY,
        "Authorization": f"Bearer {DATABASE_API_KEY}",  # Use service role or user access token
        "Content-Type": "application/json",
        "Prefer": "return=representation"  # For debugging and confirmation
    }
    
    data = {
        "evaluation": evaluations  # Dictionary object to be stored in jsonb
    }

    response = requests.patch(url, headers=headers, json=data)

    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception:
        print("No JSON response body.")

    response.raise_for_status()
    return response

try:
    st.image('Banniere argios.svg', use_container_width=True)
except:
    st.image('Banniere argios.png', use_container_width=True)

st.set_page_config(layout='wide', page_icon=icon, page_title='Les autres selon moi')
st.title=("Comment je perçois les autres")

#st.header("Rappel des quatres Quadrants")
rappel = st.checkbox("Montre moi les 4 quadrants")
if rappel:
    st.header("Quadrant A - L'ingénieur")
    inge_col1, inge_col2 = st.columns(2)
    with inge_col1:
        st.image('Inge.png', width=300)
    with inge_col2:
        st.subheader("Analytique")
        st.write(A_text)
    st.header("Quadrant B - Cartographe")
    carto_col1, carto_col2 = st.columns(2)
    with carto_col1:
        st.image('carto.png', width=300)
    with carto_col2:
        st.subheader("Séquentiel")
        st.write(B_text)
    st.header("Quadrant C - Barde")
    barde_col1, barde_col2 = st.columns(2)
    with barde_col1:
        st.image('bard.png', width=300)
    with barde_col2:
        st.subheader("Interpersonnel")
        st.write(C_text)
    st.header("Quadrant D - Inventeur")
    artisti_col1, artisti_col2 = st.columns(2)
    with artisti_col1:
        st.image('artistii.png', width=300)
    with artisti_col2:
        st.subheader("Imaginative")
        st.write(D_text)

data = fetch_results_from_database()

list_of_orga = get_organizations_from_database()

orga = st.selectbox("L'id du test", list_of_orga)
user_list = [item["user"] for item in data if item["organisation"] == orga]
user = st.selectbox("Votre pseudo (utilisé pour le test)", user_list)

if "start_eval" not in st.session_state:
    st.session_state.start_eval = False
if st.button("Commencer l'évaluation"):
    st.session_state.start_eval = True
if st.session_state.start_eval:

    filtered_data = [entry for entry in data if entry["user"] != user]
    colleagues = [entry for entry in filtered_data if entry["organisation"] == orga]

    colleagues_list = [item["user"] for item in colleagues]

    # Use session_state to persist scores and evaluation state
    if "other_scores" not in st.session_state:
        st.session_state.other_scores = {}
    if "evaluated" not in st.session_state:
        st.session_state.evaluated = set()

    selected_view = st.sidebar.radio("Choisir une personne :", colleagues_list)
    eval_sent = False

    # Show sliders for the selected colleague only
    st.header(f"Quelle est selon vous le profil de : {selected_view}")
    A_other = st.slider("Quadrant A - Ingénieur", min_value=0, max_value=4, step=1, key=f"A_{selected_view}")
    B_other = st.slider("Quadrant B - Cartographe", min_value=0, max_value=4, step=1, key=f"B_{selected_view}")
    C_other = st.slider("Quadrant C - Barde", min_value=0, max_value=4, step=1, key=f"C_{selected_view}")
    D_other = st.slider("Quadrant D - Inventeur", min_value=0, max_value=4, step=1, key=f"D_{selected_view}")

    # Only allow submission if not already evaluated
    if selected_view not in st.session_state.evaluated:
        if st.button(f"Soumettre l'évaluation pour {selected_view}"):
            st.session_state.other_scores[f"A_{selected_view}"] = A_other
            st.session_state.other_scores[f"B_{selected_view}"] = B_other
            st.session_state.other_scores[f"C_{selected_view}"] = C_other
            st.session_state.other_scores[f"D_{selected_view}"] = D_other
            st.session_state.evaluated.add(selected_view)
            st.success(f"Évaluation pour {selected_view} enregistrée !")
    else:
        st.info(f"Évaluation pour {selected_view} déjà enregistrée.")

    eval_count = len(st.session_state.evaluated)
    st.sidebar.write(f"Évaluations complétées : {eval_count} / {len(colleagues_list)}")

    if eval_count == len(colleagues_list):
        st.success("Vous avez évalué tous vos collègues ! Vous pouvez maintenant soumettre vos évaluations.")
        if st.button("Soumettre mes évaluations"):
            if user and orga:
                try:
                    update_user_evaluation(user, orga, st.session_state.other_scores)
                    st.success("Évaluations enregistrées avec succès !")
                    eval_sent = True
                except requests.exceptions.HTTPError as e:
                    st.error(f"Erreur lors de la mise à jour : {e}")
            else:
                st.warning("Veuillez renseigner votre pseudo et l'ID du test.")

    if eval_sent:
        st.balloons()
        st.info("Vous avez terminé votre évaluation 🤗. Merci beaucoup ! Vous pouvez fermer cette fenêtre.")
