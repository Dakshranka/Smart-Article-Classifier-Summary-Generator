import os
import streamlit as st
from smart_article_tool import analyze_and_save_article
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO

# Streamlit UI for the app
def main():
    # Custom CSS for modern, professional design
    st.markdown("""
        <style>
            /* General styling */
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #1e1e2f;
                color: #ffffff;
            }
            .stApp {
                background-color: #1e1e2f;
            }
            /* Sidebar styling */
            .css-1d391kg {
                background-color: #2a2a3d;
            }
            /* Header */
            .header {
                text-align: center;
                padding: 20px;
                background-color: #007bff;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                color: #ffffff;
            }
            /* Section headers */
            .section-header {
                font-size: 1.5em;
                font-weight: bold;
                color: #007bff;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 2px solid #007bff;
                padding-bottom: 5px;
            }
            /* Input fields */
            .stTextInput input {
                background-color: #2a2a3d;
                color: #ffffff;
                border: 1px solid #007bff;
                border-radius: 5px;
                padding: 10px;
            }
            /* Buttons */
            .stButton>button {
                background-color: #007bff;
                color: #ffffff;
                font-size: 16px;
                border-radius: 8px;
                padding: 12px 24px;
                transition: background-color 0.3s ease;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #005f73;
            }
            /* File uploader */
            .stFileUploader>div {
                background-color: #2a2a3d;
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 15px;
            }
            /* Text area */
            .stTextArea textarea {
                background-color: #2a2a3d;
                color: #ffffff;
                border: 1px solid #007bff;
                border-radius: 5px;
            }
            /* Alerts */
            .stAlert {
                border-radius: 8px;
                padding: 15px;
            }
            /* Containers */
            .section-container {
                background-color: #2a2a3d;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }
            /* Progress bar */
            .stProgress .st-bo {
                background-color: #007bff;
            }
            /* Download button alignment */
            .download-buttons {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
        </style>
        """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="header">
            <h1>Smart Article Tool</h1>
            <p>Classify, Summarize, and Download Articles with Ease</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.markdown("Select your input method and configure settings.")
    option = st.sidebar.selectbox("Input Method", ["Enter URL", "Upload File"], help="Choose to input an article URL or upload a .txt/.pdf file.")
    theme = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, help="Switch between dark and light themes (dark is default).")
    
    # Apply light theme if selected
    if theme == "Light":
        st.markdown("""
            <style>
                .stApp, body {
                    background-color: #f4f7f6;
                    color: #333333;
                }
                .css-1d391kg {
                    background-color: #ffffff;
                }
                .stTextInput input, .stTextArea textarea, .stFileUploader>div {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #007bff;
                }
                .section-container {
                    background-color: #e9ecef;
                    color: #333333;
                }
                .section-header {
                    color: #005f73;
                    border-bottom: 2px solid #005f73;
                }
            </style>
            """, unsafe_allow_html=True)

    # Main content
    st.info("Sites like ResearchGate or Digiday may block scraping or require login. Special characters (e.g., en dash) are handled automatically. If a URL fails, upload the article as a .txt/.pdf file.")

    # Input Section
    st.markdown("<div class='section-header'>Input Article</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        if option == "Enter URL":
            article_url = st.text_input("Paste the article URL here:", help="Enter a valid article URL. For restricted sites, consider uploading the content.")
            
            if st.button("Summarize Article"):
                if article_url:
                    progress_bar = st.progress(0)
                    progress_bar.progress(10)  # Start processing
                    with st.spinner("Fetching and processing article..."):
                        article_file_path, summary_file_path, extracted_text, summary, top_label, score, error = analyze_and_save_article(article_url, is_url=True)
                    
                    progress_bar.progress(50)  # Scraping complete
                    if error:
                        st.error(f"Failed to process the article: {error}")
                        if "403 Forbidden" in error or "Login or paywall" in error:
                            st.warning("This site (e.g., ResearchGate) may require login or restrict access. Try uploading the article content as a .txt or .pdf file.")
                        elif "Unable to extract" in error:
                            st.warning("Could not find the article content. The website may use JavaScript rendering or a unique structure (e.g., Digiday). Try uploading the article text or a different URL.")
                        elif "codec can't encode" in error.lower():
                            st.warning("The article contained special characters (e.g., en dash). This issue has been fixed; please try again.")
                        progress_bar.empty()
                        return
                    
                    progress_bar.progress(100)  # Processing complete
                    if article_file_path and summary_file_path:
                        st.success("Article processed successfully!")
                        
                        # Results Section
                        st.markdown("<div class='section-header'>Results</div>", unsafe_allow_html=True)
                        with st.container():
                            st.markdown("<div class='section-container'>", unsafe_allow_html=True)
                            st.subheader("Classification")
                            st.write(f"Category: {top_label} ({score}%)")
                            
                            st.subheader("Extracted Text Preview")
                            st.text_area("Extracted Text", extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text, height=200, help="Preview of the scraped or uploaded article text.")
                            
                            st.subheader("Generated Summary")
                            st.write(summary)
                            
                            # Download buttons
                            st.markdown("<div class='download-buttons'>", unsafe_allow_html=True)
                            with open(article_file_path, "rb") as article_file:
                                article_bytes = article_file.read()
                            with open(summary_file_path, "rb") as summary_file:
                                summary_bytes = summary_file.read()
                            
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button("Download Article PDF", article_bytes, file_name=f"article_{timestamp}.pdf", mime="application/pdf")
                            with col2:
                                st.download_button("Download Summary PDF", summary_bytes, file_name=f"summary_{timestamp}.pdf", mime="application/pdf")
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to process the article. Please check the URL and try again.")
                    progress_bar.empty()
                else:
                    st.warning("Please enter a valid URL.")

        elif option == "Upload File":
            uploaded_file = st.file_uploader("Choose an article file:", type=["txt", "pdf"], help="Upload a .txt or .pdf file containing the article content.")

            if uploaded_file is not None:
                if uploaded_file.type == "text/plain":
                    file_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                    st.subheader("File Content Preview")
                    st.text_area("File Content", file_content[:1000] + "..." if len(file_content) > 1000 else file_content, height=200)

                    if st.button("Summarize Uploaded Article"):
                        progress_bar = st.progress(0)
                        progress_bar.progress(10)
                        with st.spinner("Processing uploaded article..."):
                            article_file_path, summary_file_path, extracted_text, summary, top_label, score, error = analyze_and_save_article(file_content, is_url=False)
                        
                        progress_bar.progress(100)
                        if error:
                            st.error(f"Failed to process the article: {error}")
                            if "codec can't encode" in error.lower():
                                st.warning("The file contained special characters (e.g., en dash). This issue has been fixed; please try again.")
                            progress_bar.empty()
                            return
                        
                        if article_file_path and summary_file_path:
                            st.success("Article processed successfully!")
                            
                            # Results Section
                            st.markdown("<div class='section-header'>Results</div>", unsafe_allow_html=True)
                            with st.container():
                                st.markdown("<div class='section-container'>", unsafe_allow_html=True)
                                st.subheader("Classification")
                                st.write(f"Category: {top_label} ({score}%)")
                                
                                st.subheader("Generated Summary")
                                st.write(summary)
                                
                                st.markdown("<div class='download-buttons'>", unsafe_allow_html=True)
                                with open(article_file_path, "rb") as article_file:
                                    article_bytes = article_file.read()
                                with open(summary_file_path, "rb") as summary_file:
                                    summary_bytes = summary_file.read()
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button("Download Article PDF", article_bytes, file_name="uploaded_article.pdf", mime="application/pdf")
                                with col2:
                                    st.download_button("Download Summary PDF", summary_bytes, file_name="uploaded_article_summary.pdf", mime="application/pdf")
                                st.markdown("</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error("Failed to process the article. Please try again.")
                        progress_bar.empty()

                elif uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    full_text = ""
                    for page in reader.pages:
                        full_text += page.extract_text() or ""
                    
                    st.subheader("Extracted Text from PDF")
                    st.text_area("Extracted Text", full_text[:1000] + "..." if len(full_text) > 1000 else full_text, height=200)

                    if st.button("Summarize Uploaded Article"):
                        progress_bar = st.progress(0)
                        progress_bar.progress(10)
                        with st.spinner("Processing uploaded article..."):
                            article_file_path, summary_file_path, extracted_text, summary, top_label, score, error = analyze_and_save_article(full_text, is_url=False)
                        
                        progress_bar.progress(100)
                        if error:
                            st.error(f"Failed to process the article: {error}")
                            if "codec can't encode" in error.lower():
                                st.warning("The file contained special characters (e.g., en dash). This issue has been fixed; please try again.")
                            progress_bar.empty()
                            return
                        
                        if article_file_path and summary_file_path:
                            st.success("Article processed successfully!")
                            
                            # Results Section
                            st.markdown("<div class='section-header'>Results</div>", unsafe_allow_html=True)
                            with st.container():
                                st.markdown("<div class='section-container'>", unsafe_allow_html=True)
                                st.subheader("Classification")
                                st.write(f"Category: {top_label} ({score}%)")
                                
                                st.subheader("Generated Summary")
                                st.write(summary)
                                
                                st.markdown("<div class='download-buttons'>", unsafe_allow_html=True)
                                with open(article_file_path, "rb") as article_file:
                                    article_bytes = article_file.read()
                                with open(summary_file_path, "rb") as summary_file:
                                    summary_bytes = summary_file.read()
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button("Download Article PDF", article_bytes, file_name="uploaded_article.pdf", mime="application/pdf")
                                with col2:
                                    st.download_button("Download Summary PDF", summary_bytes, file_name="uploaded_article_summary.pdf", mime="application/pdf")
                                st.markdown("</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error("Failed to process the article. Please try again.")
                        progress_bar.empty()
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()