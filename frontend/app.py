import os
from typing import Dict, Any, List, Optional

import httpx
import streamlit as st


st.set_page_config(page_title="QnA Agent UI", layout="centered")


def get_base_url() -> str:
    return st.session_state.get("base_url") or os.getenv("API_BASE_URL", "http://localhost:8000")


def api_client() -> httpx.Client:
    timeout = httpx.Timeout(10.0, read=30.0)
    return httpx.Client(timeout=timeout)


def init_session_state():
    st.session_state.setdefault("base_url", get_base_url())
    st.session_state.setdefault("workflow_id", None)
    st.session_state.setdefault("run_id", None)
    st.session_state.setdefault("last_prompt", None)
    st.session_state.setdefault("current_state", [])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("poll", True)


def has_processing_states(states: List[Dict[str, Any]]) -> bool:
    for s in states:
        if s.get("state") not in ("concluido", "prompt"):
            return True
    return False


def render_state(states: List[Dict[str, Any]], last_prompt: Optional[str]):
    if not states:
        st.info("Sem estado em processamento.")
        return

    # Mostrar se o primeiro item (o prompt) confere com o último enviado
    prompt_ok = False
    first = states[0]
    if first.get("state") == "prompt":
        prompt_ok = (last_prompt is None) or (first.get("content") == last_prompt)

    with st.container(border=True):
        st.write("Estado atual da execução:")
        if prompt_ok:
            st.caption("Monitorando o prompt atual enviado.")
        else:
            st.caption("Aviso: o estado não corresponde ao último prompt enviado nesta sessão.")

        for s in states:
            content = s.get("content")
            state = s.get("state")
            if state == "prompt":
                continue
            icon = "🟡" if state != "concluido" else "🟢"
            st.write(f"{icon} {content} — {state}")


def main():
    init_session_state()

    st.title("QnA Agent - Temporal")

    if st.button("Refresh"): st.rerun()

    # Config API base URL
    # st.session_state.base_url = st.text_input("API Base URL", value=get_base_url())

    # Start or show workflow info
    if not st.session_state.workflow_id:
        st.subheader("Start Workflow")
        query = st.text_input("Initial query", value="")
        top_k = st.number_input("Top K", min_value=1, max_value=50, value=3, step=1)
        start = st.button("Start", type="primary")
        if start:
            if not query.strip():
                st.error("Please enter the initial query.")
            else:
                try:
                    with api_client() as c:
                        resp = c.post(f"{get_base_url()}/workflows/start", json={"query": query, "top_k": int(top_k)})
                        resp.raise_for_status()
                        data = resp.json()
                        print(data)
                        st.session_state.workflow_id = data.get("workflow_id")
                        st.session_state.run_id = data.get("run_id")
                        st.success(f"Workflow started: {st.session_state.workflow_id}")
                except httpx.HTTPError as e:
                    st.error(f"Failed to start workflow: {e}")
    else:
        st.subheader("Workflow")
        st.write(f"ID: {st.session_state.workflow_id}")

        # Poll status
        try:
            with api_client() as c:
                r = c.get(f"{get_base_url()}/workflows/{st.session_state.workflow_id}/status")
                if r.status_code == 200:
                    latest = r.json().get("latest")
                    if isinstance(latest, dict):
                        st.session_state.current_state = latest.get("current_state", [])
                else:
                    st.warning("Could not get status.")
        except httpx.HTTPError:
            st.warning("API unavailable for status.")

        # Render current state
        render_state(st.session_state.current_state, st.session_state.last_prompt)

        blocked = has_processing_states(st.session_state.current_state)
        if blocked:
            st.info("Waiting for steps to complete before sending new prompt…")

        # Prompt input and send
        prompt = st.text_input("Your prompt", value="")
        col1, col2, col3 = st.columns(3)
        with col1:
            send = st.button("Send prompt", disabled=blocked or not prompt.strip())
        with col2:
            end = st.button("End conversation")
        with col3:
            show_hist = st.button("Show history")

        if send and prompt.strip():
            try:
                with api_client() as c:
                    r = c.post(
                        f"{get_base_url()}/workflows/{st.session_state.workflow_id}/prompt",
                        json={"prompt": prompt.strip()},
                    )
                    r.raise_for_status()
                    st.session_state.last_prompt = prompt.strip()
                    st.success("Prompt sent.")
            except httpx.HTTPError as e:
                st.error(f"Failed to send prompt: {e}")

        if end:
            try:
                with api_client() as c:
                    r = c.post(f"{get_base_url()}/workflows/{st.session_state.workflow_id}/end")
                    r.raise_for_status()
                    st.success("Conversation ended.")
            except httpx.HTTPError as e:
                st.error(f"Failed to end conversation: {e}")

        if show_hist:
            try:
                with api_client() as c:
                    r = c.get(f"{get_base_url()}/workflows/{st.session_state.workflow_id}/history")
                    r.raise_for_status()
                    data = r.json()
                    st.session_state.history = data.get("history", [])
            except httpx.HTTPError as e:
                st.error(f"Could not get history: {e}")

        if st.session_state.history:
            st.subheader("History")
            for m in st.session_state.history:
                st.write(f"[{m.get('actor')}] {m.get('content')}")

    # Auto refresh while running
    if st.session_state.workflow_id:
        st.rerun()


if __name__ == "__main__":
    main()
