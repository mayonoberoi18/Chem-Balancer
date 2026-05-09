import streamlit as st
import sympy as sp
import re
from PIL import Image
import pytesseract
import time
import plotly.graph_objects as go
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="⚗️ GOD MODE Chemical Balancer",
    page_icon="⚗️",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:white;
}

.main-title{
    text-align:center;
    font-size:60px;
    font-weight:bold;
    color:#ffffff;
}

.sub{
    text-align:center;
    font-size:20px;
    color:#dddddd;
    margin-bottom:20px;
}

.card{
    background:rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    margin-top:15px;
    box-shadow:0px 0px 20px rgba(0,0,0,0.4);
}

.step{
    background:rgba(0,0,0,0.35);
    padding:12px;
    border-radius:12px;
    margin-top:10px;
}

.result{
    text-align:center;
    font-size:34px;
    font-weight:bold;
    color:#00ffcc;
}

.small{
    color:#cccccc;
}

.stButton > button{
    width:100%;
    height:55px;
    border:none;
    border-radius:15px;
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    font-size:18px;
    font-weight:bold;
}

.stTextInput input{
    border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">⚗️ GOD MODE Chemical Equation Balancer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub">Ultra Pro NCERT Chemistry Solver • OCR • Smart Detection • Algebraic Engine</div>',
    unsafe_allow_html=True
)

# ---------------- ADVANCED FORMULA PARSER ----------------
def parse_formula(formula):

    tokens = re.findall(r'[A-Z][a-z]?|\(|\)|\d+', formula)

    stack = [{}]

    i = 0

    while i < len(tokens):

        token = tokens[i]

        if token == '(':
            stack.append({})

        elif token == ')':

            top = stack.pop()

            multiplier = 1

            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                multiplier = int(tokens[i + 1])
                i += 1

            for element, count in top.items():
                stack[-1][element] = stack[-1].get(element, 0) + count * multiplier

        elif re.match(r'[A-Z][a-z]?', token):

            element = token

            count = 1

            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                count = int(tokens[i + 1])
                i += 1

            stack[-1][element] = stack[-1].get(element, 0) + count

        i += 1

    return stack[0]

# ---------------- GET ELEMENTS ----------------
def get_elements(compounds):

    elements = set()

    for compound in compounds:
        elements.update(parse_formula(compound).keys())

    return sorted(elements)

# ---------------- BALANCER ----------------
def algebraic_balance(eq):

    eq = eq.replace('=', '->')
    eq = eq.replace('→', '->')
    eq = eq.replace(' ', '')

    if '->' not in eq:
        raise ValueError('Equation must contain ->')

    left_side, right_side = eq.split('->')

    left = left_side.split('+')
    right = right_side.split('+')

    compounds = left + right

    elements = get_elements(compounds)

    matrix = []

    for element in elements:

        row = []

        for compound in left:
            row.append(parse_formula(compound).get(element, 0))

        for compound in right:
            row.append(-parse_formula(compound).get(element, 0))

        matrix.append(row)

    matrix = sp.Matrix(matrix)

    nullspace = matrix.nullspace()

    if not nullspace:
        raise ValueError("Cannot balance equation")

    solution = nullspace[0]

    lcm = sp.lcm([term.q for term in solution])

    coeffs = [abs(int(term * lcm)) for term in solution]

    gcd = abs(sp.gcd(coeffs))

    coeffs = [c // gcd for c in coeffs]

    left_coeffs = coeffs[:len(left)]
    right_coeffs = coeffs[len(left):]

    balanced_left = ' + '.join(
        f'{coef if coef != 1 else ""}{compound}'
        for coef, compound in zip(left_coeffs, left)
    )

    balanced_right = ' + '.join(
        f'{coef if coef != 1 else ""}{compound}'
        for coef, compound in zip(right_coeffs, right)
    )

    balanced_equation = balanced_left + ' → ' + balanced_right

    return balanced_equation, coeffs, left, right

# ---------------- REACTION TYPE ----------------
def detect_type(eq):

    if "O2" in eq:
        return "🔥 Combustion Reaction"

    if "NO3" in eq or "KMnO4" in eq:
        return "⚡ Redox Reaction"

    if "HCl" in eq or "H2SO4" in eq:
        return "🧪 Acid Reaction"

    if "+" in eq and "->" in eq:
        return "⚛️ General Chemical Reaction"

    return "❓ Unknown Reaction"

# ---------------- NCERT EXPLANATION ----------------
def generate_steps(eq, coeffs, method):

    steps = []

    if method == "ABCD Algebraic Method":

        steps.append("Step 1: Write the unbalanced equation.")

        steps.append("Step 2: Assign variables A, B, C... to compounds.")

        steps.append("Step 3: Count atoms on both sides.")

        steps.append("Step 4: Form equations for each element.")

        steps.append("Step 5: Solve equations algebraically.")

        steps.append(f"Step 6: Final coefficient set = {coeffs}")

    else:

        steps.append("Step 1: Start balancing metals first.")

        steps.append("Step 2: Balance non-metals.")

        steps.append("Step 3: Balance oxygen atoms.")

        steps.append("Step 4: Balance hydrogen atoms.")

        steps.append(f"Step 5: Final coefficient set = {coeffs}")

    return steps

# ---------------- OCR ----------------
def extract_text(uploaded):

    image = Image.open(uploaded)

    text = pytesseract.image_to_string(image)

    text = text.replace('=', '->')
    text = text.replace('→', '->')

    return text.strip()

# ---------------- VISUALIZATION ----------------
def atom_chart(compounds, coeffs):

    labels = []
    values = []

    for compound, coeff in zip(compounds, coeffs):

        parsed = parse_formula(compound)

        total_atoms = sum(parsed.values()) * coeff

        labels.append(compound)
        values.append(total_atoms)

    fig = go.Figure(
        data=[go.Bar(
            x=labels,
            y=values
        )]
    )

    fig.update_layout(
        title="Atom Distribution",
        template="plotly_dark",
        height=400
    )

    return fig

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

method = st.sidebar.selectbox(
    "Choose Method",
    [
        "ABCD Algebraic Method",
        "Hit & Trial Method"
    ]
)

theme = st.sidebar.selectbox(
    "Chemistry Mode",
    [
        "NCERT Student",
        "Advanced Chemistry",
        "Exam Preparation"
    ]
)

# ---------------- INPUT ----------------
input_mode = st.radio(
    "Choose Input Method",
    [
        "Text Input",
        "Image OCR"
    ]
)

user_eq = ""

if input_mode == "Text Input":

    user_eq = st.text_input(
        "Enter Chemical Equation",
        "S + HNO3 -> H2SO4 + NO2 + H2O"
    )

elif input_mode == "Image OCR":

    uploaded = st.file_uploader(
        "Upload Equation Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded:

        extracted = extract_text(uploaded)

        st.success(f"Extracted Equation: {extracted}")

        user_eq = extracted

# ---------------- SOLVE ----------------
if st.button("⚡ BALANCE EQUATION"):

    if user_eq:

        try:

            balanced, coeffs, left, right = algebraic_balance(user_eq)

            reaction_type = detect_type(user_eq)

            st.markdown(
                f'''
                <div class="card">
                    <div class="result">
                        ✅ {balanced}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

            st.markdown(
                f'''
                <div class="card">
                    🧪 <b>Reaction Type:</b> {reaction_type}
                </div>
                ''',
                unsafe_allow_html=True
            )

            # Progress Animation
            st.markdown(
                '''
                <div class="card">
                    ⚛️ Balancing atoms...
                </div>
                ''',
                unsafe_allow_html=True
            )

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            # Steps
            st.markdown(
                '''
                <div class="card">
                    📘 Step-by-Step NCERT Explanation
                </div>
                ''',
                unsafe_allow_html=True
            )

            steps = generate_steps(user_eq, coeffs, method)

            for step in steps:

                st.markdown(
                    f'''
                    <div class="step">
                        {step}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            # Visualization
            st.markdown(
                '''
                <div class="card">
                    📊 Atom Visualization
                </div>
                ''',
                unsafe_allow_html=True
            )

            compounds = left + right

            fig = atom_chart(compounds, coeffs)

            st.plotly_chart(fig, use_container_width=True)

            # Chemistry Tips
            st.markdown(
                '''
                <div class="card">
                    💡 Chemistry Tip:
                    <br><br>
                    Always balance metals first,
                    then non-metals,
                    oxygen,
                    and hydrogen at last.
                </div>
                ''',
                unsafe_allow_html=True
            )

        except Exception as e:

            st.error(f"❌ Error: {e}")

    else:

        st.warning("Please enter a valid chemical equation.")

# ---------------- FOOTER ----------------
st.markdown(
    """
    <br><br>
    <center class="small">
        ⚗️ GOD MODE Chemistry Solver • Streamlit Edition
    </center>
    """,
    unsafe_allow_html=True
)
