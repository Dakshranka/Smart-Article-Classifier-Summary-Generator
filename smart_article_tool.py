import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from transformers import pipeline
from fpdf import FPDF
import re
import spacy
from heapq import nlargest
import unicodedata

# Initialize the classifier and summarizer
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
summarizer = pipeline("summarization", model="google/pegasus-xsum")

# Load spaCy model for NLP tasks
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# Function to sanitize the filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Function to clean text for PDF compatibility
def clean_text_for_pdf(text):
    """Aggressively clean text to remove all non-ASCII characters and boilerplate"""
    # Normalize Unicode to ASCII, removing non-ASCII characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Remove boilerplate, expanded for journal terms and news snippets
    text = re.sub(
        r'(Advertisement|Sponsored|Subscribe Now|Sign Up|Log In|Follow Us|Share This|Related Posts|'
        r'Footer|Nav|Menu|Sidebar|Comment|Social Media|Home|About|Contact|Privacy Policy|'
        r'Terms of Use|Terms and Conditions|Login to view|BBC News|Published by|Journal of|'
        r'Copyright|All rights reserved|Posted on|Updated on|Share on|Read more|'
        r'Newsletter|Membership|Cookies|Accept|Decline|View Full Text).*?(?=\n|$)', 
        '', text, flags=re.IGNORECASE
    )
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Function to save text as PDF with improved formatting
def save_text_as_pdf(filename, title, text, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = sanitize_filename(filename)
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        print(f"⚠️ File already exists: {file_path}")
        return file_path
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Article Summary", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='L')
    pdf.ln(10)
    
    # Title
    pdf.set_font("Arial", 'B', 14)
    cleaned_title = clean_text_for_pdf(title)
    # Fix common title errors (e.g., bioethic -> bioethics)
    cleaned_title = re.sub(r'\bbioethic\b', 'bioethics', cleaned_title, flags=re.IGNORECASE)
    pdf.multi_cell(0, 10, txt=cleaned_title)
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", size=12)
    cleaned_text = clean_text_for_pdf(text)
    pdf.multi_cell(0, 10, txt=cleaned_text)
    
    pdf.output(file_path)
    print(f"Saved PDF: {file_path}")
    return file_path

# Function to rank sentences for summary
def rank_sentences(text, n=5):
    """Rank sentences by importance using spaCy"""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    sentence_scores = {}
    for sent in sentences:
        doc_sent = nlp(sent)
        score = sum(token.rank for token in doc_sent if token.rank) / (len(doc_sent) + 1)
        sentence_scores[sent] = score
    return nlargest(n, sentence_scores, key=sentence_scores.get)

# Function to filter irrelevant summary sentences
def filter_relevant_sentences(sentences, keywords):
    """Filter sentences that are relevant to the article based on keywords"""
    relevant_sentences = []
    for sent in sentences:
        doc = nlp(sent.lower())
        if any(keyword in [token.text for token in doc] for keyword in keywords):
            relevant_sentences.append(sent)
    return relevant_sentences if relevant_sentences else sentences[:min(5, len(sentences))]

# Function to analyze and save article
def analyze_and_save_article(content, is_url=True):
    try:
        if is_url:
            print(f"📥 Downloading article from URL: {content}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/"
            }
            try:
                response = requests.get(content, headers=headers, timeout=15)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 403:
                    print(f"❌ Access denied (403 Forbidden) for URL: {content}")
                    return None, None, None, None, "403 Forbidden: Access denied. This site (e.g., ResearchGate) may require login. Please upload the article as a .txt or .pdf file."
                raise
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "Untitled"
            # Fix common title errors
            title = re.sub(r'\bbioethic\b', 'bioethics', title, flags=re.IGNORECASE)
            
            # Check for login/paywall prompts
            login_indicators = ['login', 'sign in', 'register', 'access restricted', 'log in to view']
            if any(indicator in soup.text.lower() for indicator in login_indicators):
                print("⚠️ Login or paywall detected.")
                return None, None, None, None, "Login or paywall detected. Please upload the article content as a .txt or .pdf file."
            
            # Try multiple selectors for article content
            article_content = (
                soup.find('article') or
                soup.find('div', class_=re.compile('article|content|post|body|entry|story|text|single|page|main-content|post-content|entry-content|article-text|article-body|publication-abstract|nova-e-text', re.I)) or
                soup.find('section', class_=re.compile('article|content|post|body|abstract', re.I)) or
                soup.find('main') or
                soup.find('div', attrs={'role': 'article'}) or
                soup.find('div', class_=re.compile('wp-block-post-content|has-post-content|researchgate', re.I))
            )
            
            if not article_content:
                # Fallback 1: Extract all paragraph tags
                print("⚠️ Primary selectors failed. Attempting fallback to paragraph tags.")
                paragraphs = soup.find_all('p')
                text = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                
                if not text or len(text) < 100:
                    # Fallback 2: Extract from body, excluding scripts and nav
                    print("⚠️ Paragraph fallback failed. Attempting body extraction.")
                    for unwanted in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        unwanted.decompose()
                    body = soup.find('body')
                    text = body.get_text(separator=' ', strip=True) if body else ''
                
                if not text or len(text) < 100:
                    print(f"⚠️ All extraction methods failed. Extracted text: {text}")
                    return None, None, None, None, "Unable to extract article content. The website (e.g., ResearchGate) may use JavaScript rendering or a unique structure. Try uploading the article as a .txt or .pdf file."
            else:
                text = article_content.get_text(separator=' ', strip=True)
                print(f"📄 Extracted text: {text[:1000]}...")
            
        else:
            text = content
            title = "Uploaded_Article"
            title = re.sub(r'\bbioethic\b', 'bioethics', title, flags=re.IGNORECASE)

        # Clean text for PDF and summarization
        text = clean_text_for_pdf(text)
        if not text or len(text) < 100:
            print(f"⚠️ Article content is empty or too short: {text}")
            return None, None, None, None, "Article content is empty or too short."

        # Save original article as PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_filename = f"article_{timestamp}.pdf" if is_url else "uploaded_article.pdf"
        article_file_path = save_text_as_pdf(article_filename, title, text, "articles")

        # Classify the article
        print("🧠 Classifying article...")
        labels = ["Design", "Technology", "Business", "Marketing", "AI"]
        classification = classifier(text, candidate_labels=labels)
        top_label = classification['labels'][0]
        score = round(classification['scores'][0] * 100, 2)
        # Standardize AI label
        display_label = "AI" if top_label.lower() == 'ai' else top_label.capitalize()

        # Summarize the article
        print("📝 Generating summary...")
        chunks = [text[i:i+800] for i in range(0, len(text), 600)]  # Overlap for context
        summary_parts = []
        
        for chunk in chunks:
            try:
                result = summarizer(chunk, max_length=400, min_length=30, do_sample=False)
                summary_parts.append(result[0]['summary_text'])
            except Exception as e:
                print(f"⚠️ Error summarizing chunk: {e}")
                continue
        
        # Combine and rank sentences
        summary_text = " ".join(summary_parts)
        summary_sentences = rank_sentences(summary_text, n=5)
        # Filter relevant sentences using article-related keywords
        keywords = ['artificial intelligence', 'bioethics', 'society', 'medical', 'ethics', 'technology']
        summary_sentences = filter_relevant_sentences(summary_sentences, keywords)
        summary = " ".join(summary_sentences[:min(5, len(summary_sentences))])

        # Save summary as PDF
        summary_filename = f"summary_{timestamp}.pdf" if is_url else "uploaded_article_summary.pdf"
        summary_content = (
            f"Title: {title}\n\n"
            f"Category: {display_label} ({score} percent)\n\n"
            f"Summary:\n{summary}"
        )
        summary_file_path = save_text_as_pdf(summary_filename, title, summary_content, "summaries")

        print(f"\n✅ Saved original in 'articles/{article_filename}'")
        print(f"✅ Saved summary in 'summaries/{summary_filename}'\n")
        
        return article_file_path, summary_file_path, text, summary, None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None, None, str(e)
