import streamlit as st
import sympy as sp
import re
from PIL import Image
import pytesseract
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Next Level Chemical Balancer",
    page_icon="⚗️",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color: white;
}

.main-title {
    text-align:center;
    font-size:55px;
    font-weight:bold;
    color:white;
    margin-bottom:10px;
}

.subtitle {
    text-align:center;
    color:#d1d1d1;
    font-size:18px;
    margin-bottom:30px;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    margin-top:15px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
}

.step {
    background: rgba(0,0,0,0.35);
    padding:12px;
    border-radius:12px;
    margin-top:10px;
}

.result {
    text-align:center;
    font-size:30px;
    font-weight:bold;
    color:#00ffcc;
}

.stButton>button {
    width:100%;
    border-radius:12px;
    height:50px;
    font-size:18px;
    font-weight:bold;
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    border:none;
}

.stButton>button:hover {
    transform:scale(1.02);
    transition:0.2s;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">⚗️ Next Level Chemical Balancer</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Balance chemical equations using ABCD or Hit & Trial methods</div>',
    unsafe_allow_html=True
)

# ---------------- PARSER ----------------
def parse_formula(formula):
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)

    composition = {}

    for element, count in matches:
        count = int(count) if count else 1

        if element in composition:
            composition[element] += count
        else:
            composition[element] = count

    return composition

# ---------------- GET ELEMENTS ----------------
def get_elements(compounds):
    elements = set()

    for compound in compounds:
        elements.update(parse_formula(compound).keys())

    return sorted(elements)

# ---------------- ALGEBRAIC METHOD ----------------
def algebraic_balance(equation):

    left_side, right_side = equation.split("->")

    left_compounds = [x.strip() for x in left_side.split("+")]
    right_compounds = [x.strip() for x in right_side.split("+")]

    compounds = left_compounds + right_compounds

    elements = get_elements(compounds)

    matrix = []

    for element in elements:

        row = []

        for compound in left_compounds:
            row.append(parse_formula(compound).get(element, 0))

        for compound in right_compounds:
            row.append(-parse_formula(compound).get(element, 0))

        matrix.append(row)

    matrix = sp.Matrix(matrix)

    nullspace = matrix.nullspace()

    solution = nullspace[0]

    lcm = sp.lcm([term.q for term in solution])

    coefficients = [abs(int(term * lcm)) for term in solution]

    left_coefficients = coefficients[:len(left_compounds)]
    right_coefficients = coefficients[len(left_compounds):]

    balanced_left = " + ".join(
        f"{coef if coef != 1 else ''}{compound}"
        for coef, compound in zip(left_coefficients, left_compounds)
    )

    balanced_right = " + ".join(
        f"{coef if coef != 1 else ''}{compound}"
        for coef, compound in zip(right_coefficients, right_compounds)
    )

    balanced_equation = balanced_left + " → " + balanced_right

    return balanced_equation, coefficients

# ---------------- REACTION TYPE ----------------
def detect_reaction_type(eq):

    if "O2" in eq:
        return "Combustion Reaction"

    elif "NO3" in eq or "KMnO4" in eq:
        return "Redox Reaction"

    elif "+" in eq and "->" in eq:
        return "General Chemical Reaction"

    else:
        return "Unknown Reaction"

# ---------------- STEP GENERATOR ----------------
def generate_steps(eq, coeffs, method):

    steps = []

    if method == "ABCD Method":

        steps.append("Step 1: Write the unbalanced equation.")

        steps.append("Step 2: Assign variables A, B, C... to all compounds.")

        steps.append("Step 3: Count atoms of each element on both sides.")

        steps.append("Step 4: Form algebraic equations.")

        steps.append("Step 5: Solve the equations.")

        steps.append(f"Step 6: Final coefficient set = {coeffs}")

    else:

        steps.append("Step 1: Start balancing one element at a time.")

        steps.append("Step 2: Balance metals first.")

        steps.append("Step 3: Balance non-metals.")

        steps.append("Step 4: Balance oxygen and hydrogen at last.")

        steps.append(f"Step 5: Final coefficient set = {coeffs}")

    return steps

# ---------------- OCR ----------------
def extract_equation_from_image(uploaded_image):

    image = Image.open(uploaded_image)

    text = pytesseract.image_to_string(image)

    return text.strip()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

method = st.sidebar.selectbox(
    "Choose Balancing Method",
    ["ABCD Method", "Hit & Trial Method"]
)

# ---------------- INPUT MODE ----------------
input_mode = st.radio(
    "Choose Input Mode",
    ["Text Input", "Image OCR"]
)

equation = ""

# ---------------- TEXT INPUT ----------------
if input_mode == "Text Input":

    equation = st.text_input(
        "Enter Chemical Equation",
        "S + HNO3 -> H2SO4 + NO2 + H2O"
    )

# ---------------- IMAGE OCR ----------------
elif input_mode == "Image OCR":

    uploaded_file = st.file_uploader(
        "Upload Equation Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        extracted = extract_equation_from_image(uploaded_file)

        st.success(f"Extracted Equation: {extracted}")

        equation = extracted

# ---------------- SOLVE BUTTON ----------------
if st.button("⚡ Balance Equation"):

    if equation:

        try:

            balanced_equation, coeffs = algebraic_balance(equation)

            reaction_type = detect_reaction_type(equation)

            # RESULT
            st.markdown(
                f'''
                <div class="card">
                    <div class="result">
                        ✅ {balanced_equation}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

            # REACTION TYPE
            st.markdown(
                f'''
                <div class="card">
                    🧪 <b>Reaction Type:</b> {reaction_type}
                </div>
                ''',
                unsafe_allow_html=True
            )

            # PROGRESS ANIMATION
            st.markdown(
                '''
                <div class="card">
                    ⚛️ Balancing Atoms...
                </div>
                ''',
                unsafe_allow_html=True
            )

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            # STEPS
            st.markdown(
                '''
                <div class="card">
                    📘 Step-by-Step Solution
                </div>
                ''',
                unsafe_allow_html=True
            )

            steps = generate_steps(equation, coeffs, method)

            for step in steps:

                st.markdown(
                    f'''
                    <div class="step">
                        {step}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

        except Exception as e:

            st.error(f"Error: {e}")

    else:

        st.warning("Please enter a chemical equation.")

# ---------------- FOOTER ----------------
st.markdown(
    """
    <br><br>
    <center>
        Made with ❤️ using Streamlit
    </center>
    """,
    unsafe_allow_html=True
)
