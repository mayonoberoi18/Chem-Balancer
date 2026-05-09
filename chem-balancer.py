import streamlit as st
import sympy as sp
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from collections import defaultdict
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Chemistry Balancer",
    page_icon="⚗️",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}

.main-title {
    text-align:center;
    font-size:60px;
    font-weight:bold;
    color:white;
}

.sub-title {
    text-align:center;
    color:#dddddd;
    font-size:20px;
    margin-bottom:20px;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    margin-top:15px;
    box-shadow:0px 0px 15px rgba(0,0,0,0.3);
}

.result {
    text-align:center;
    font-size:35px;
    font-weight:bold;
    color:#00ffcc;
}

.step {
    background: rgba(0,0,0,0.25);
    padding:12px;
    border-radius:12px;
    margin-top:10px;
}

.tip {
    background: rgba(0,255,200,0.1);
    padding:12px;
    border-radius:12px;
    margin-top:10px;
}

.stButton > button {
    width:100%;
    height:55px;
    border-radius:15px;
    border:none;
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    font-size:20px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">⚗️Chemistry Balancer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">NCERT + JEE Chemical Equation Solver</div>',
    unsafe_allow_html=True
)

# =========================================================
# PERIODIC TABLE
# =========================================================

ATOMIC_MASS = {
    'H': 1.008,
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'Na': 22.99,
    'Mg': 24.305,
    'Al': 26.982,
    'P': 30.974,
    'S': 32.06,
    'Cl': 35.45,
    'K': 39.098,
    'Ca': 40.078,
    'Mn': 54.938,
    'Fe': 55.845,
    'Cu': 63.546,
    'Zn': 65.38,
    'Ag': 107.87,
    'I': 126.90,
    'Ba': 137.33,
    'Au': 196.97,
    'Pb': 207.2
}

VALID_ELEMENTS = set(ATOMIC_MASS.keys())

# =========================================================
# FORMULA PARSER
# =========================================================

def parse_formula(formula):

    tokens = re.findall(r'[A-Z][a-z]?|\(|\)|\d+', formula)

    stack = [defaultdict(int)]

    i = 0

    while i < len(tokens):

        token = tokens[i]

        # OPEN BRACKET
        if token == '(':
            stack.append(defaultdict(int))

        # CLOSE BRACKET
        elif token == ')':

            group = stack.pop()

            multiplier = 1

            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                multiplier = int(tokens[i + 1])
                i += 1

            for element, count in group.items():
                stack[-1][element] += count * multiplier

        # ELEMENT
        elif re.match(r'[A-Z][a-z]?', token):

            element = token
            count = 1

            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                count = int(tokens[i + 1])
                i += 1

            stack[-1][element] += count

        i += 1

    return dict(stack[0])

# =========================================================
# VALIDATION
# =========================================================

def validate_formula(formula):

    elements = re.findall(r'[A-Z][a-z]?', formula)

    for element in elements:
        if element not in VALID_ELEMENTS:
            return False

    return True

# =========================================================
# GET ELEMENTS
# =========================================================

def get_elements(compounds):

    elements = set()

    for compound in compounds:
        parsed = parse_formula(compound)
        elements.update(parsed.keys())

    return sorted(elements)

# =========================================================
# BALANCER
# =========================================================

def balance_equation(eq):

    eq = eq.replace("=", "->")
    eq = eq.replace("→", "->")
    eq = eq.replace(" ", "")

    if "->" not in eq:
        raise ValueError("Equation must contain ->")

    left_side, right_side = eq.split("->")

    left = left_side.split("+")
    right = right_side.split("+")

    compounds = left + right

    # VALIDATE
    for compound in compounds:

        if not validate_formula(compound):
            raise ValueError(f"Invalid compound: {compound}")

    elements = get_elements(compounds)

    matrix = []

    for element in elements:

        row = []

        # LEFT SIDE
        for compound in left:
            row.append(parse_formula(compound).get(element, 0))

        # RIGHT SIDE
        for compound in right:
            row.append(-parse_formula(compound).get(element, 0))

        matrix.append(row)

    matrix = sp.Matrix(matrix)

    nullspace = matrix.nullspace()

    if not nullspace:
        raise ValueError("Unable to balance equation")

    solution = nullspace[0]

    lcm = sp.lcm([term.q for term in solution])

    coeffs = [abs(int(term * lcm)) for term in solution]

    gcd = abs(sp.gcd(coeffs))

    coeffs = [c // gcd for c in coeffs]

    left_coeffs = coeffs[:len(left)]
    right_coeffs = coeffs[len(left):]

    balanced_left = " + ".join(
        f"{coef if coef != 1 else ''}{compound}"
        for coef, compound in zip(left_coeffs, left)
    )

    balanced_right = " + ".join(
        f"{coef if coef != 1 else ''}{compound}"
        for coef, compound in zip(right_coeffs, right)
    )

    balanced_equation = balanced_left + " → " + balanced_right

    return balanced_equation, coeffs, left, right

def detect_reaction(eq):

    eq = eq.replace(" ", "")

    left_side, right_side = eq.split("->")

    reactants = left_side.split("+")
    products = right_side.split("+")

    # =====================================================
    # DECOMPOSITION
    # One reactant -> multiple products
    # =====================================================

    if len(reactants) == 1 and len(products) > 1:
        return "🧨 Decomposition Reaction"

    # =====================================================
    # COMBUSTION
    # Hydrocarbon + O2 -> CO2 + H2O
    # =====================================================

    hydrocarbon = False

    for compound in reactants:

        if "C" in compound and "H" in compound:
            hydrocarbon = True

    if (
        hydrocarbon
        and "O2" in reactants
        and any("CO2" in p for p in products)
        and any("H2O" in p for p in products)
    ):
        return "🔥 Combustion Reaction"

    # =====================================================
    # SINGLE DISPLACEMENT
    # =====================================================

    if len(reactants) == 2 and len(products) == 2:
        return "⚔️ Displacement Reaction"

    # =====================================================
    # NEUTRALIZATION
    # =====================================================

    acids = ["HCl", "H2SO4", "HNO3"]

    bases = ["NaOH", "KOH", "Ca(OH)2"]

    if (
        any(acid in reactants for acid in acids)
        and any(base in reactants for base in bases)
    ):
        return "⚗️ Neutralization Reaction"

    # =====================================================
    # REDOX
    # =====================================================

    redox_agents = [
        "KMnO4",
        "K2Cr2O7",
        "HNO3"
    ]

    if any(agent in eq for agent in redox_agents):
        return "⚡ Redox Reaction"

    # =====================================================
    # PRECIPITATION
    # =====================================================

    precipitates = [
        "PbI2",
        "AgCl",
        "BaSO4"
    ]

    if any(ppt in products for ppt in precipitates):
        return "🌧️ Precipitation Reaction"

    # =====================================================
    # DEFAULT
    # =====================================================

    return "⚛️ General Chemical Reaction"

# =========================================================
# MOLAR MASS
# =========================================================

def calculate_molar_mass(compound):

    parsed = parse_formula(compound)

    total = 0

    for element, count in parsed.items():
        total += ATOMIC_MASS.get(element, 0) * count

    return round(total, 3)

# =========================================================
# STEP EXPLANATION
# =========================================================

def generate_steps(coeffs):

    steps = [

        "Step 1: Write the unbalanced chemical equation.",

        "Step 2: Count atoms of each element on both sides.",

        "Step 3: Create algebraic equations for each element.",

        "Step 4: Solve the equations using matrix method.",

        f"Step 5: Final balanced coefficients = {coeffs}",

        "Step 6: Verify that atoms are equal on both sides."
    ]

    return steps

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Settings")

mode = st.sidebar.selectbox(
    "Select Mode",
    ["NCERT", "JEE", "Advanced"]
)

# =========================================================
# INPUT SECTION
# =========================================================

st.markdown("""
<div class="card">

<h3>✍️ Enter Chemical Equation</h3>

Examples:

• Fe + O2 -> Fe2O3

• Pb(NO3)2 + KI -> PbI2 + KNO3

• KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2

</div>
""", unsafe_allow_html=True)

user_eq = st.text_input(
    "Chemical Equation",
    "Pb(NO3)2 + KI -> PbI2 + KNO3"
)

# =========================================================
# BALANCE BUTTON
# =========================================================

if st.button("⚡ BALANCE EQUATION"):

    try:

        # BALANCE
        balanced, coeffs, left, right = balance_equation(user_eq)

        compounds = left + right

        reaction_type = detect_reaction(user_eq)

        # RESULT
        st.markdown(f"""
        <div class="card">
            <div class="result">
                ✅ {balanced}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # REACTION TYPE
        st.markdown(f"""
        <div class="card">
            <h3>{reaction_type}</h3>
        </div>
        """, unsafe_allow_html=True)

        # PROGRESS BAR
        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.003)
            progress.progress(i + 1)

        # =========================================================
        # STEP EXPLANATION
        # =========================================================

        st.markdown("""
        <div class="card">
            <h2>📘 Step-by-Step Explanation</h2>
        </div>
        """, unsafe_allow_html=True)

        steps = generate_steps(coeffs)

        for step in steps:
            st.markdown(f"""
            <div class="step">
                {step}
            </div>
            """, unsafe_allow_html=True)

        # =========================================================
        # DETAILED ATOM ANALYSIS
        # =========================================================

        st.markdown("""
        <div class="card">
            <h2>📊 Detailed Atom Analysis</h2>
        </div>
        """, unsafe_allow_html=True)

        detailed_rows = []

        for compound in compounds:

            parsed = parse_formula(compound)

            for element, count in parsed.items():

                detailed_rows.append({

                    "Compound": compound,
                    "Element": element,
                    "Atoms Present": count,
                    "Atomic Mass": ATOMIC_MASS.get(element, "Unknown")
                })

        detailed_df = pd.DataFrame(detailed_rows)

        st.dataframe(
            detailed_df,
            use_container_width=True
        )

        st.success(
            "✅ This table shows all elements, atom counts, and atomic masses."
        )

        # =========================================================
        # BAR GRAPH
        # =========================================================

        fig = px.bar(
            detailed_df,
            x="Compound",
            y="Atoms Present",
            color="Element",
            title="Element Distribution in Compounds"
        )

        fig.update_layout(template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)

        # =========================================================
        # MOLAR MASS TABLE
        # =========================================================

        st.markdown("""
        <div class="card">
            <h2>⚖️ Molar Mass Analysis</h2>
        </div>
        """, unsafe_allow_html=True)

        mass_data = []

        for compound in compounds:

            mass_data.append({
                "Compound": compound,
                "Molar Mass": calculate_molar_mass(compound)
            })

        mass_df = pd.DataFrame(mass_data)

        st.dataframe(
            mass_df,
            use_container_width=True
        )

        # =========================================================
        # PIE CHART
        # =========================================================

        pie = go.Figure(
            data=[
                go.Pie(
                    labels=mass_df["Compound"],
                    values=mass_df["Molar Mass"]
                )
            ]
        )

        pie.update_layout(
            title="Molar Mass Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(pie, use_container_width=True)

        # =========================================================
        # SUMMARY
        # =========================================================

        st.markdown("""
        <div class="card">
            <h2>🧾 Final Summary</h2>
        </div>
        """, unsafe_allow_html=True)

        summary_df = pd.DataFrame({

            "Property": [
                "Reaction Type",
                "Total Reactants",
                "Total Products",
                "Total Compounds",
                "Mode"
            ],

            "Value": [
                reaction_type,
                len(left),
                len(right),
                len(compounds),
                mode
            ]
        })

        st.table(summary_df)

        # =========================================================
        # CHEMISTRY TIP
        # =========================================================

        st.markdown("""
        <div class="tip">

        💡 <b>Chemistry Tip:</b><br><br>

        Balance metals first,
        then non-metals,
        then oxygen,
        and hydrogen at the end.

        </div>
        """, unsafe_allow_html=True)

    except Exception as e:

        st.error(f"❌ Error: {e}")

# =========================================================
# PRACTICE QUESTIONS
# =========================================================

st.markdown("""
<div class="card">
<h2>🧠 Practice Equations</h2>
</div>
""", unsafe_allow_html=True)

practice_questions = [

    "Fe + O2 -> Fe2O3",

    "Al + HCl -> AlCl3 + H2",

    "Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O",

    "Pb(NO3)2 + KI -> PbI2 + KNO3",

    "C2H6 + O2 -> CO2 + H2O",

    "S + HNO3 -> H2SO4 + NO2 + H2O"
]

for q in practice_questions:
    st.code(q)

# =========================================================
# FOOTER
# =========================================================

st.markdown("""

<br><br>

<center>

⚗️Chemistry Solver

<br><br>

Made by Mayon Oberoi

</center>

""", unsafe_allow_html=True)
