# api_config.py
import streamlit as st
import google.generativeai as genai
from streamlit_elements import elements, mui, html
import time

CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
/* ... (paste all your CSS styles here) ... */
</style>
"""

def configure_api():
    """Configure the Gemini API with tech-themed UI"""
    st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)
    
    # Tech-themed API key dialog
    @st.dialog("🔐 API Gateway Configuration")
    def api_key_dialog():
        with elements("cyber_dialog"):
            mui.Box(
                # ... (paste all your dialog code here) ...
            )

    # Floating tech button
    if st.button("🔌 API Config", help="Configure API connection"):
        api_key_dialog()

    # API status indicator
    api_key = st.session_state.get("api_key", "")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Test the connection
            with st.spinner("🔄 Validating API credentials..."):
                model = genai.GenerativeModel('gemini-2.0-flash')
                model.generate_content("Test connection")
            
            st.success(f"✅ Secure connection established | v1.4.2 | {time.strftime('%H:%M:%S')}")
            st.markdown(
                f"""
                <div class="cyber-terminal" style="margin-top: 0.5rem;">
                    <div style="display: flex; align-items: center;">
                        <span>API STATUS:</span>
                        <span class="cyber-status cyber-status-active">ACTIVE</span>
                    </div>
                    <div style="margin-top: 0.5rem;">Endpoint: <code>genai.googleapis.com/v1beta</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            return True
        except Exception as e:
            st.error(f"🔴 Connection failed: {str(e)}")
            st.session_state.pop("api_key", None)
            return False
    else:
        st.markdown(
            """
            <div class="cyber-terminal">
                <div style="display: flex; align-items: center;">
                    <span>API STATUS:</span>
                    <span style="background-color: rgba(255,50,50,0.2); color: #f44; padding: 0.2rem 0.5rem; border-radius: 3px; margin-left: 0.5rem;">INACTIVE</span>
                </div>
                <div style="margin-top: 0.5rem;">Authentication required to enable AI features</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return False