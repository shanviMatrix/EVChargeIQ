from pathlib import Path
import base64
import streamlit as st


def show_splash():

    if st.session_state.get("splash_shown", False):
        return

    st.session_state["splash_shown"] = True

    project_root = Path(__file__).resolve().parents[2]
    logo_path = project_root / "assets" / "evchargeiq_logo.jpg"

    if not logo_path.is_file():
        st.warning(f"EVChargeIQ logo not found: {logo_path}")
        return

    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    st.html(f"""
        <div class="evqi-splash">
            <div class="evqi-brand">

                <img
                    class="evqi-logo"
                    src="data:image/jpeg;base64,{logo_base64}"
                    alt="EVChargeIQ"
                />

                <div class="evqi-tagline">
                    INDIA'S EV INFRASTRUCTURE INTELLIGENCE
                </div>

                <div class="evqi-loader">
                    <div class="evqi-loader-fill"></div>
                </div>

            </div>
        </div>
    """)
