import streamlit as st
            # Atom Tables
            all_compounds = left + right

            atom_data = []

            for compound in all_compounds:

                parsed = parse_formula(compound)

                for element, count in parsed.items():
                    atom_data.append([
                        compound,
                        element,
                        count
                    ])

            df = pd.DataFrame(atom_data, columns=['Compound', 'Element', 'Atoms'])

            st.markdown(
                '''
                <div class="card">
                    📊 Atom Count Table
                </div>
                ''',
                unsafe_allow_html=True
            )

            st.dataframe(df, use_container_width=True)

            # Visualization
            fig = px.bar(
                df,
                x='Compound',
                y='Atoms',
                color='Element',
                title='Element Distribution'
            )

            fig.update_layout(template='plotly_dark')

            st.plotly_chart(fig, use_container_width=True)

            # Tips
            st.markdown(
                '''
                <div class="card">
                    💡 <b>NCERT Tip:</b><br><br>
                    Balance the rarest element first,
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

# ---------------- FOOTER ----------------
st.markdown(
    '''
    <br><br>
    <center>
        ⚗️ Ultimate Streamlit Chemistry Solver
    </center>
    ''',
    unsafe_allow_html=True
)
