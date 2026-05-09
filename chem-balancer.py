import streamlit as st
import sympy as sp
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pytesseract
import time
from collections import defaultdict

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Ultimate Chemistry Balancer",
    page_icon="⚗️",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
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
    font-size:32px;
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
    font-size:18px;
    font-weight:bold;
}

</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# TITLES
# =========================================================
st.markdown(
    '<div class="main-title">⚗️ Ultimate Chemistry Balancer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">NCERT + JEE Style Chemical Equation Solver</div>',
    unsafe_allow_html=True
)

# =========================================================
# PERIODIC TABLE DATA
# =========================================================
ATOMIC_MASS = {
    'H': 1.008,
    'He': 4.0026,
    'Li': 6.94,
    'Be': 9.0122,
    'B': 10.81,
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'F': 18.998,
    'Na': 22.99,
    'Mg': 24.305,
    'Al': 26.982,
    'Si': 28.085,
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
# =========================================================
# PARSER
# =========================================================
def parse_formula(formula):

    tokens = re.findall(r'[A-Z][a-z]?|\(|\)|\d+', formula)

    stack = [defaultdict(int)]

    i = 0

    while i < len(tokens):

        token = tokens[i]

        if token == '(':

            stack.append(defaultdict(int))

        elif token == ')':

            top = stack.pop()

            multiplier = 1

            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                multiplier = int(tokens[i + 1])
                i += 1

            for element, count in top.items():
                stack[-1][element] += count * multiplier

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


def validate_equation(eq):

    if '->' not in eq and '=' not in eq and '→' not in eq:
        return False

    return True

# =========================================================
# ELEMENTS
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

    eq = eq.replace('=', '->')
    eq = eq.replace('→', '->')
    eq = eq.replace(' ', '')

    if not validate_equation(eq):
        raise ValueError('Equation must contain ->')

    left_side, right_side = eq.split('->')

    left = left_side.split('+')
    right = right_side.split('+')

    compounds = left + right

    for compound in compounds:
        if not validate_formula(compound):
            raise ValueError(f'Invalid compound: {compound}')

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
        raise ValueError('Unable to balance equation')

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

    balanced = balanced_left + ' → ' + balanced_right

    return balanced, coeffs, left, right

# =========================================================
# REACTION TYPE
# =========================================================
def detect_reaction(eq):

    if 'O2' in eq:
        return '🔥 Combustion Reaction'

    if 'HCl' in eq or 'H2SO4' in eq:
        return '🧪 Acid Reaction'

    if 'KMnO4' in eq or 'K2Cr2O7' in eq:
        return '⚡ Redox Reaction'

    if 'NaOH' in eq:
        return '⚗️ Neutralization Reaction'

    return '⚛️ General Chemical Reaction'

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
# STEP GENERATOR
# =========================================================
def generate_steps(coeffs, method):

    steps = []

    if method == 'ABCD Method':

        steps.append('Step 1: Write the unbalanced equation.')
        steps.append('Step 2: Assign variables A, B, C, D.')
        steps.append('Step 3: Count atoms of each element.')
        steps.append('Step 4: Form algebraic equations.')
        steps.append('Step 5: Solve using matrices.')
        steps.append(f'Step 6: Final coefficients = {coeffs}')

    else:

        steps.append('Step 1: Balance metals first.')
        steps.append('Step 2: Balance non-metals.')
        steps.append('Step 3: Balance oxygen atoms.')
        steps.append('Step 4: Balance hydrogen atoms.')
        steps.append(f'Step 5: Final coefficients = {coeffs}')

    return steps

# =========================================================
# VISUALIZATION
# =========================================================
def atom_dataframe(compounds):

    data = []

    for compound in compounds:

        parsed = parse_formula(compound)

        for element, count in parsed.items():
            data.append([
                compound,
                element,
                count
            ])

    return pd.DataFrame(
        data,
        columns=['Compound', 'Element', 'Atoms']
    )

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title('⚙️ Settings')

method = st.sidebar.selectbox(
    'Choose Method',
    ['ABCD Method', 'Hit & Trial Method']
)

mode = st.sidebar.selectbox(
    'Chemistry Mode',
    ['NCERT', 'JEE', 'Advanced']
)

# =========================================================
# INPUT SECTION
# =========================================================

st.markdown(
    '''
    <div class="card">
        <h3>✍️ Enter Chemical Equation</h3>
        <p>
        Examples:<br>
        • Fe + O2 -> Fe2O3<br>
        • Pb(NO3)2 + KI -> PbI2 + KNO3<br>
        • KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2
        </p>
    </div>
    ''',
    unsafe_allow_html=True
)

user_eq = st.text_input(
    'Chemical Equation',
    'Pb(NO3)2 + KI -> PbI2 + KNO3'
)

# =========================================================
# BALANCE BUTTON
# =========================================================
if st.button('⚡ BALANCE EQUATION'):

    if user_eq:

        try:

            balanced, coeffs, left, right = balance_equation(user_eq)

            reaction_type = detect_reaction(user_eq)

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

            # Progress
            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.005)
                progress.progress(i + 1)

            # Steps
            st.markdown(
                '''
                <div class="card">
                    📘 Step-by-Step Explanation
                </div>
                ''',
                unsafe_allow_html=True
            )

            steps = generate_steps(coeffs, method)

            for step in steps:
                st.markdown(
                    f'''
                    <div class="step">
                        {step}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            # Atom table
            st.markdown(
                '''
                <div class="card">
                    📊 Detailed Atom Analysis
                </div>
                ''',
                unsafe_allow_html=True
            )

            detailed_rows = []

            for compound in compounds:

                parsed = parse_formula(compound)

                for element, count in parsed.items():

                    detailed_rows.append({
                        'Compound': compound,
                        'Element': element,
                        'Number of Atoms': count,
                        'Atomic Mass': ATOMIC_MASS.get(element, 'Unknown')
                    })

            detailed_df = pd.DataFrame(detailed_rows)

            st.dataframe(
                detailed_df,
                use_container_width=True
            )

            st.success('✅ The table above shows every element present in each compound along with atom counts and atomic masses.')

            # Graph
            fig = px.bar(
                df,
                x='Compound',
                y='Atoms',
                color='Element',
                title='Element Distribution'
            )

            fig.update_layout(
                template='plotly_dark'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Molar masses
            st.markdown(
                '''
                <div class="card">
                    ⚖️ Molar Mass Calculator
                </div>
                ''',
                unsafe_allow_html=True
            )

            mass_data = []

            for compound in compounds:
                mass_data.append([
                    compound,
                    calculate_molar_mass(compound)
                ])

            mass_df = pd.DataFrame(
                mass_data,
                columns=['Compound', 'Molar Mass']
            )

            st.dataframe(mass_df, use_container_width=True)

            # Pie chart
            pie = go.Figure(
                data=[
                    go.Pie(
                        labels=mass_df['Compound'],
                        values=mass_df['Molar Mass']
                    )
                ]
            )

            pie.update_layout(
                template='plotly_dark',
                title='Molar Mass Distribution'
            )

            st.plotly_chart(pie, use_container_width=True)

            # Balanced Equation Summary
            st.markdown(
                '''
                <div class="card">
                    🧾 Final Summary
                </div>
                ''',
                unsafe_allow_html=True
            )

            summary_data = {
                'Property': [
                    'Reaction Type',
                    'Method Used',
                    'Number of Reactants',
                    'Number of Products',
                    'Total Compounds'
                ],
                'Value': [
                    reaction_type,
                    method,
                    len(left),
                    len(right),
                    len(compounds)
                ]
            }

            summary_df = pd.DataFrame(summary_data)

            st.table(summary_df)

            # Chemistry tips
            st.markdown(
                '''
                <div class="tip">
                    💡 Chemistry Tip:<br><br>
                    Balance rare elements first,
                    then metals,
                    then oxygen,
                    and hydrogen at the end.
                </div>
                ''',
                unsafe_allow_html=True
            )

        except Exception as e:

            st.error(f'❌ Error: {e}')

    else:

        st.warning('Please enter a valid equation.')

# =========================================================
# PRACTICE SECTION
# =========================================================
st.markdown(
    '''
    <div class="card">
        <h3>🧠 Practice Equations</h3>
    </div>
    ''',
    unsafe_allow_html=True
)

practice_questions = [
    'Fe + O2 -> Fe2O3',
    'Al + HCl -> AlCl3 + H2',
    'Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O',
    'Pb(NO3)2 + KI -> PbI2 + KNO3',
    'C2H6 + O2 -> CO2 + H2O',
    'KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2'
]

for q in practice_questions:
    st.code(q)

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    '''
    <br><br>
    <center>
        ⚗️ Ultimate Streamlit Chemistry Solver<br><br>
        Made by Mayon Oberoi
    </center>
    ''',
    unsafe_allow_html=True
)
