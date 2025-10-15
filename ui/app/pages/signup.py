import streamlit as st
import requests
import json
from typing import Optional

def main():
    st.title("🚀 Sign Up - FastCV Beta")
    st.write("Create your account to access the FastCV application")
    
    # Backend API configuration
    API_BASE_URL = "http://localhost:8000/api/v1"
    
    # Create signup form
    with st.form("signup_form"):
        st.subheader("Create Account")
        
        # Full name field (optional)
        full_name = st.text_input(
            "Full Name (Optional)",
            placeholder="Enter your full name",
            help="This field is optional"
        )
        
        # Email field
        email = st.text_input(
            "Email Address *",
            placeholder="Enter your email address",
            help="This will be your username for login"
        )
        
        # Password field
        password = st.text_input(
            "Password *",
            type="password",
            placeholder="Enter your password",
            help="Password must be between 8-40 characters"
        )
        
        # Confirm password field
        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Confirm your password"
        )
        
        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must agree to the terms to create an account"
        )
        
        # Submit button
        submitted = st.form_submit_button("Create Account", type="primary")
        
        if submitted:
            # Validate form
            validation_errors = validate_signup_form(email, password, confirm_password, agree_terms)
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Prepare data for API call
                signup_data = {
                    "email": email,
                    "password": password,
                    "full_name": full_name if full_name.strip() else None
                }
                
                # Show loading spinner
                with st.spinner("Creating your account..."):
                    try:
                        # Make API call to backend
                        response = requests.post(
                            f"{API_BASE_URL}/users/signup",
                            json=signup_data,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            # Success
                            user_data = response.json()
                            st.success("🎉 Account created successfully!")
                            st.balloons()
                            
                            # Display user information
                            st.info(f"Welcome {user_data.get('full_name', 'User')}! Your account has been created.")
                            st.write(f"**Email:** {user_data.get('email')}")
                            st.write(f"**User ID:** {user_data.get('id')}")
                            
                            # Option to go to login or home
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Go to Home"):
                                    st.switch_page("pages/home.py")
                            with col2:
                                if st.button("Login Now"):
                                    st.info("Please use the login page to access your account")
                                    
                        elif response.status_code == 400:
                            # User already exists or validation error
                            error_data = response.json()
                            st.error(f"❌ {error_data.get('detail', 'Registration failed')}")
                            
                        else:
                            # Other server errors
                            st.error(f"❌ Server error: {response.status_code}")
                            try:
                                error_data = response.json()
                                st.error(f"Details: {error_data.get('detail', 'Unknown error')}")
                            except:
                                st.error(f"Response: {response.text}")
                                
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to the server. Please make sure the backend is running on http://localhost:8000")
                    except requests.exceptions.Timeout:
                        st.error("❌ Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    # Add some helpful information
    st.divider()
    st.subheader("Account Information")
    st.info("""
    **Password Requirements:**
    - Must be between 8 and 40 characters
    - Choose a strong password for security
    
    **After Signup:**
    - You can use your email and password to log in
    - Your account will be active immediately
    - Contact support if you need assistance
    """)
    
    # Link to login page
    st.write("Already have an account?")
    if st.button("Sign In Instead"):
        st.info("Please use the login page to access your existing account")

def validate_signup_form(email: str, password: str, confirm_password: str, agree_terms: bool) -> list[str]:
    """Validate the signup form and return list of error messages"""
    errors = []
    
    # Email validation
    if not email or not email.strip():
        errors.append("Email address is required")
    elif "@" not in email or "." not in email:
        errors.append("Please enter a valid email address")
    
    # Password validation
    if not password or not password.strip():
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) > 40:
        errors.append("Password must be no more than 40 characters long")
    
    # Confirm password validation
    if not confirm_password or not confirm_password.strip():
        errors.append("Please confirm your password")
    elif password != confirm_password:
        errors.append("Passwords do not match")
    
    # Terms agreement validation
    if not agree_terms:
        errors.append("You must agree to the Terms of Service and Privacy Policy")
    
    return errors

if __name__ == "__main__":
    main()
