import streamlit as st
import requests

A_text_fr = """L'ingénieur aime bien résoudre des problèmes en utilisant la méthode scientifique et le raisonnement logique. 
Il est dans la réflexion et est capable de conceptualiser des notions abstraites. C'est une personnalité plutôt introvertie qui aime analyser et savoir.\n
***Points de force*** : compilent les faits, analysent, argumentent rationnellement, formulent des théories, mesurent précisément, résolvent les problèmes logiquement, 
raisonnent, comprennent les éléments techniques, analysent avec l'esprit critique, travaillent à partir de chiffres, de statistiques, et sont précis."""

B_text_fr = """Le cartographe est prudent et organisé. Il a des habitudes bien précises et respecte soigneusement les règles.
Il planifie méticuleusement ce qui doit être fait et se retrouve bien dans les tâches administratif ou son souci du détail est sa fiabilité est valorisé.\n
***Points de force*** : remarquent les défauts, approchent les problèmes pratiquement, vont jusqu'au bout des choses, développent des plans détaillés et des procédures, et envisagent les problèmes sous l'angle du planning."""

C_text_fr = """Le barde aime le contact humain. Il est empathique, relationnel et amicale. Il est expressif et communique bien avec les autres.\n
***Points de force*** : comprennent les difficultés relationnelles, anticipent le ressenti des autres, comprennent intuitivement le ressenti des autres, perçoivent des éléments non verbaux issus du stress, engendrent l'enthousiasme, persuadent, concilient, enseignent, partagent, comprennent les éléments émotionnels, prennent en compte les valeurs."""

D_text_fr = """L'inventeur est un aventurier avec une imagination débordante qui rêve éveillé. C'est un visionnaire qui a toujours des idées très originales.
C'est aussi un rebel qui aime bien prendre des risuqes et se projeter.\n
***Points de force*** : Lisent les signes du changement, voient les choses globalement, reconnaissent les nouvelles possibilités, tolèrent l'ambiguïté, intègrent les idées et les concepts, défient les règles établies, synthétisent les éléments divers en un nouveau tout, inventent des solutions nouvelles, résolvent les problèmes de manière intuitive, intègrent en simultané différents inputs."""

A_text_en = """The Engineer enjoys solving problems using scientific methods and logical reasoning.
They reflect deeply and can conceptualize abstract ideas. Often introverted, they like to analyze and understand.\n
***Strengths***: compile facts, analyze, argue rationally, form theories, perform precise measurements, solve problems logically, 
reason using critical thinking, understand technical matters, work with numbers and statistics."""

B_text_en = """The Cartographer is careful and organized, with well-defined habits and strong respect for rules.
They plan meticulously and thrive in administrative tasks where attention to detail and reliability are valued.\n
***Strengths***: notice defects, take practical approaches, follow through, develop detailed plans and procedures, and think in terms of schedules."""

C_text_en = """The Bard thrives on human connection: empathetic, relational, and friendly. Expressive and a strong communicator.\n
***Strengths***: understand relational challenges, anticipate others' feelings, read nonverbal stress cues, generate enthusiasm, persuade, reconcile, teach, share, consider emotional factors and values."""

D_text_en = """The Inventor is an adventurous visionary with a vivid imagination and original ideas.
They challenge conventions and like to take risks and project into the future.\n
***Strengths***: read signs of change, see the big picture, spot new possibilities, tolerate ambiguity, integrate ideas and concepts, challenge established rules, synthesize diverse inputs, invent new solutions, solve problemns using intuition, integrate inputs simultaneously."""


# Define your result_filename and global_results_filename
#result_filename = "results.txt"
#global_results_filename = "global_results.txt"
icon = "Favicon_2x.ico"
# Inject external CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#post to database
DATABASE_URL = st.secrets["DATABASE_URL"]
DATABASE_API_KEY = st.secrets["DATABASE_API_KEY"]

# Language state and URL sync helpers
def tr(fr: str, en: str) -> str:
    return en if st.session_state.get('lang', 'fr') == 'en' else fr

def update_url():
    st.query_params.update({
        'user': st.session_state.user,
        'orga': st.session_state.orga,
        'lang': st.session_state.lang,
    })

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

# Language toggle UI
lang_toggle = st.toggle('English', value=st.session_state.get('lang', 'fr') == 'en')
if lang_toggle and st.session_state.get('lang') != 'en':
    st.session_state.lang = 'en'
    st.rerun()
elif (not lang_toggle) and st.session_state.get('lang') != 'fr':
    st.session_state.lang = 'fr'
    st.rerun()

try:
    st.image('bannière e-diagnostic profiler.svg', use_container_width=True)
except:
    st.image('bannière e-diagnostic profiler.png', use_container_width=True)

data = fetch_results_from_database()

list_of_orga = get_organizations_from_database()

orga = st.selectbox(tr("L'id du test","the id of the test"), list_of_orga)
user_list = [item["user"] for item in data if item["organisation"] == orga]
user = st.selectbox(tr("Votre pseudo (utilisé pour le test)","The user name (chosen for the previous test)"), user_list)

st.set_page_config(layout='wide', page_icon=icon, page_title='Les autres selon moi')

#st.header("Rappel des quatres Quadrants")
rappel = st.checkbox(tr("Montre moi les 4 quadrants", "Show me the 4 quadrants"))
if rappel:
    st.header(tr("Quadrant A - L'ingénieur", "Quadrant A - The Engineer"))
    inge_col1, inge_col2 = st.columns(2)
    with inge_col1:
        st.image('Inge.png', width=300)
    with inge_col2:
        st.subheader(tr("Analytique", "Analytical"))
        st.write(tr(A_text_fr, A_text_en))
    st.header(tr("Quadrant B - Cartographe", "Quadrant B - The Cartographer"))
    carto_col1, carto_col2 = st.columns(2)
    with carto_col1:
        st.image('carto.png', width=300)
    with carto_col2:
        st.subheader(tr("Séquentiel", "Sequential"))
        st.write(tr(B_text_fr, B_text_en))
    st.header(tr("Quadrant C - Barde", "Quadrant C - The Bard"))
    barde_col1, barde_col2 = st.columns(2)
    with barde_col1:
        st.image('bard.png', width=300)
    with barde_col2:
        st.subheader(( tr("Interpersonnel", "Interpersonal")))
        st.write(tr(C_text_fr, C_text_en))
    st.header(tr("Quadrant D - Inventeur", "Quadrant D - The Inventor"))
    artisti_col1, artisti_col2 = st.columns(2)
    with artisti_col1:
        st.image('artistii.png', width=300)
    with artisti_col2:
        st.subheader(tr("Imaginative", "Imaginative"))
        st.write(tr(D_text_fr, D_text_en))


if "start_eval" not in st.session_state:
    st.session_state.start_eval = False
if st.button(tr("Commencer l'évaluation", "Start the evaluation")):
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

    selected_view = st.sidebar.radio(tr("Choisir une personne :", "Choose a person:"), colleagues_list)
    eval_sent = False

    # Show sliders for the selected colleague only
    st.header(tr(f"Quelle est selon vous le profil de : {selected_view}", f"What do you think is the profile of: {selected_view}"))
    A_other = st.slider(tr("Quadrant A - Ingénieur", "Quadrant A - The Engineer"), min_value=0, max_value=4, step=1, key=f"A_{selected_view}")
    B_other = st.slider(tr("Quadrant B - Cartographe", "Quadrant B - The Cartographer"), min_value=0, max_value=4, step=1, key=f"B_{selected_view}")
    C_other = st.slider(tr("Quadrant C - Barde", "Quadrant C - The Bard"), min_value=0, max_value=4, step=1, key=f"C_{selected_view}")
    D_other = st.slider(tr("Quadrant D - Inventeur", "Quadrant D - The Inventor"), min_value=0, max_value=4, step=1, key=f"D_{selected_view}")

    # Only allow submission if not already evaluated
    if selected_view not in st.session_state.evaluated:
        if st.button(tr(f"Soumettre l'évaluation pour {selected_view}", f"Submit evaluation for {selected_view}")):
            st.session_state.other_scores[f"A_{selected_view}"] = A_other
            st.session_state.other_scores[f"B_{selected_view}"] = B_other
            st.session_state.other_scores[f"C_{selected_view}"] = C_other
            st.session_state.other_scores[f"D_{selected_view}"] = D_other
            st.session_state.evaluated.add(selected_view)
            st.success(tr(f"Évaluation pour {selected_view} enregistrée !", f"Evaluation for {selected_view} is recorded!"))
    else:
        st.info((tr(f"Vous avez déjà évalué {selected_view}.", f"You have already evaluated {selected_view}.")))

    eval_count = len(st.session_state.evaluated)
    st.sidebar.write(tr(f"Évaluations complétées : {eval_count} / {len(colleagues_list)}", f"Completed evaluations: {eval_count} / {len(colleagues_list)}"))

    if eval_count == len(colleagues_list):
        st.success(tr("Vous avez évalué tous vos collègues ! Vous pouvez maintenant soumettre vos évaluations.", "You have evaluated all your colleagues! You can now submit your evaluations."))
        if st.button(tr("Soumettre mes évaluations", "Submit my evaluations")):
            if user and orga:
                try:
                    update_user_evaluation(user, orga, st.session_state.other_scores)
                    st.success(tr("Évaluations enregistrées avec succès !", "Evaluations successfully recorded!"))
                    eval_sent = True
                except requests.exceptions.HTTPError as e:
                    st.error(f"Erreur lors de la mise à jour : {e}")
            else:
                st.warning(tr("Veuillez renseigner votre pseudo et l'ID du test.", "Please provide your user name and the test ID."))

    if eval_sent:
        st.balloons()
        st.info(tr("Vous avez terminé votre évaluation 🤗. Merci beaucoup ! Vous pouvez fermer cette fenêtre.", "You have finished the evaluation, you can now close this window."))
