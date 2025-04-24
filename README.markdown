# Smart Article Classifier & Summary Generator

This project is developed for Creative Upaay’s internship assignment to automate article classification and summarization using natural language processing (NLP). It processes articles from URLs or uploaded files (`.txt`/`.pdf`), classifies them into one of five categories (Design, Technology, Business, Marketing, AI), and generates concise 3-5 sentence summaries. The tool features a modern Streamlit-based web interface for input, preview, and PDF downloads, with professional formatting and robust error handling for sites like ResearchGate and Digiday.

## Features

- **Web Scraping**: Extracts article content from URLs using `requests` and `BeautifulSoup` with adaptive selectors and fallbacks.
- **Classification**: Categorizes articles using zero-shot classification (`facebook/bart-large-mnli`).
- **Summarization**: Generates abstractive summaries with `google/pegasus-xsum`, optimized for 3-5 sentences.
- **PDF Generation**: Saves original articles and summaries as PDFs with improved readability (clear titles, standardized categories, filtered content).
- **User Interface**: Modern Streamlit dashboard with dark/light themes, sidebar navigation, progress feedback, and container-based layout.
- **Error Handling**: Handles restricted sites, encoding issues, and scraping failures with actionable feedback.

## Approach

1. **Scraping**: Uses browser-like headers and multiple selectors (`article`, `div.article-body`, etc.) to extract content, with fallbacks to paragraph tags or full body text.
2. **Preprocessing**: Normalizes text to ASCII to handle special characters (e.g., en dash `\u2013`) and removes boilerplate (e.g., ads, journal terms).
3. **Classification**: Applies zero-shot classification with labels: Design, Technology, Business, Marketing, AI.
4. **Summarization**: Chunks text (800 chars, 600 stride), summarizes with `google/pegasus-xsum` (`max_length=150`), ranks sentences with `spacy`, and filters irrelevant content using keywords.
5. **Frontend**: Streamlit UI with containers, progress bars, and styled alerts for a professional experience.
6. **PDF Output**: Generates formatted PDFs with headers, dates, bold titles, and clean summaries.

## Installation

### Prerequisites

- Python 3.8+
- 8GB+ RAM (for `google/pegasus-xsum`)
- ~1.5GB disk space (for model weights)

### Dependencies

Install the required libraries:

```bash
pip install streamlit requests beautifulsoup4 transformers fpdf PyPDF2 spacy
python -m spacy download en_core_web_sm
```

### Running the App

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

3. Access the app at `http://localhost:8501` in your browser.

## Usage

1. **Open the App**: Launch the Streamlit interface.
2. **Select Input Method** (via sidebar):
   - **Enter URL**: Paste an article URL (e.g., from ResearchGate, Digiday, The Verge).
   - **Upload File**: Upload a `.txt` or `.pdf` file for restricted sites.
3. **Summarize**:
   - Click "Summarize Article" (for URLs) or "Summarize Uploaded Article" (for files).
   - View progress via a progress bar and spinner.
4. **View Results**:
   - **Extracted Text Preview**: Up to 1000 characters in the UI (full text in console logs).
   - **Summary**: 3-5 sentence summary in the UI and PDF.
   - **Downloads**: Download the original article and summary as PDFs.
5. **Debugging**: Check terminal logs for full extracted text (successful or failed extractions) to verify scraping.

## Why Pegasus-XSUM?

`google/pegasus-xsum` was chosen for its abstractive summarization, producing concise, human-readable summaries. Key optimizations:
- **Chunking**: 800 chars with 600-char overlap for context.
- **Summarization**: `max_length=150` for detailed output.
- **Sentence Ranking**: Uses `spacy` to select top 5 sentences.
- **Relevance Filtering**: Keywords ensure summaries focus on article topics.
- **Efficiency**: Model weights are cached for faster subsequent runs.

## Limitations

- **JavaScript-Rendered Content**: Requires uploads for dynamic sites.
- **Classification Accuracy**: Zero-shot model may misclassify ambiguous articles.
- **Summary Quality**: Depends on input text; irrelevant sentences are mitigated but not eliminated.
- **Restricted Sites**: Scraping may fail for ResearchGate/Digiday, requiring uploads.
- **Verbose Logs**: Full text logging for large articles may clutter the console.
- **Content Length**: Minimum 100 characters to avoid empty articles.

## Potential Improvements

- **API Service**: Expose functionality via REST API.
- **Fine-Tuning**: Train Pegasus on domain-specific data (e.g., academic articles).
- **Advanced Scraping**: Use Selenium for JavaScript-rendered sites (avoided for simplicity).
- **Batch Processing**: Support multiple URLs in parallel.
- **Logging Control**: Add configurable log limits (e.g., 5000 chars) for large articles.

## Contributing

Feel free to fork the repository, submit issues, or create pull requests to enhance functionality. Suggestions for improving scraping, summarization, or UI are welcome.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
