import streamlit as st
import requests

st.title("Chat with Jackie")
# initialize session state for session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = None

user_input = st.text_input("You:", "")

if st.button("Send"):
        # Send the user input to the backend
        payload = {"prompt": user_input, "session_id": st.session_state.session_id}
        print("Sending payload:", payload)  # Debugging print statement
        response = requests.post("http://localhost:8000/generate/",
                                 json={"prompt": user_input, "session_id": st.session_state.session_id})
        result = response.json()

        # Check if the necessary keys are in the result
        if "session_id" not in result or "response" not in result:
            st.error("Invalid response from server.")
        else:
            # Update session id
            st.session_state.session_id = result["session_id"]
            # Display the response from the backend
            st.text_area("Jackie:", value=result["response"], height=200)

