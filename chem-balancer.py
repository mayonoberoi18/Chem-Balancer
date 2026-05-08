import streamlit as st

    if uploaded:
        extracted = ocr_extract(uploaded)
        st.success(f'Extracted: {extracted}')
        user_eq = extracted

elif input_mode == 'Voice':
    if st.button('🎤 Start Voice Input'):
        user_eq = voice_input()
        st.success(user_eq)

# ---------------- SOLVER ----------------
if st.button('⚡ Solve Equation'):

    if user_eq:

        try:
            balanced, coeffs = algebraic_balance(user_eq)

            reaction_type = detect_type(user_eq)

            st.markdown(
                f'<div class="card big">✅ {balanced}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="card">🧪 Reaction Type: <b>{reaction_type}</b></div>',
                unsafe_allow_html=True
            )

            # Animation
            st.markdown(
                '<div class="card"><b>⚛️ Atom Balancing Animation</b></div>',
                unsafe_allow_html=True
            )

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            # Teacher Steps
            st.markdown(
                '<div class="card"><b>📘 NCERT Style Explanation</b></div>',
                unsafe_allow_html=True
            )

            steps = generate_teacher_steps(user_eq, coeffs)

            for s in steps:
                st.markdown(
                    f'<div class="step">{s}</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f'Error: {e}')

# ---------------- FOOTER ----------------
st.markdown(
    '<br><center>Made with ❤️ using Streamlit</center>',
    unsafe_allow_html=True
)
