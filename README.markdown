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

### Sample URLs

- ResearchGate: https://www.researchgate.net/publication/333709419_Digital_Marketing_A_Review
- Digiday: https://digiday.com/marketing/stability-with-transformation-insights-into-the-turbulent-landscape-of-2024-advertising/
- Open-access sites:
  - https://www.theverge.com/2025/4/15/24131234/ai-breakthroughs-2025
  - https://techcrunch.com/2025/04/10/quantum-computing-advances
  - https://www.forbes.com/sites/bernardmarr/2025/03/20/business-strategies-ai

*Note*: Replace with real, accessible 2025 URLs. For restricted sites (e.g., ResearchGate), upload `.txt`/`.pdf` if scraping fails.

## Improvements and Fixes

### UI/UX Enhancements

- **Modern Design**: Dark theme (default) with light theme option, using Roboto font, inspired by ThingsBoard.io.
- **Sidebar Navigation**: Select input method (URL/upload) and theme for intuitive control.
- **Container-Based Layout**: Replaced nested expanders with `st.container` and custom CSS (`section-container`) to fix Streamlit’s nesting error.
- **Progress Feedback**: Added progress bars and spinners for scraping and summarization.
- **Responsive Styling**: Optimized for desktop and mobile, with centered download buttons and styled alerts.

### Encoding Fix

- **Issue**: Unicode characters (e.g., en dash `\u2013`) caused `'latin-1' codec can't encode` errors in `FPDF`.
- **Fix**: Normalized all text to ASCII in `clean_text_for_pdf`, stripping non-ASCII characters, and simplified `save_text_as_pdf` to avoid `latin-1` encoding.

### Logging Improvements

- **200-Character Error Log Limit**:
  - **Issue**: Error logs in `analyze_and_save_article` truncated extracted text to 200 characters, limiting debugging.
  - **Fix**: Removed `text[:200]` restriction, printing full text for failed extractions (e.g., “All extraction methods failed. Extracted text: {text}”).
- **1000-Character Successful Extraction Log Limit**:
  - **Issue**: Successful extraction logs truncated text to 1000 characters (`text[:1000]`), hiding full content.
  - **Fix**: Removed `text[:1000]` in `print(f"📄 Extracted text: {text}")`, printing the entire extracted text to verify scraping completeness.

### Summarizer Enhancement

- **Issue**: Summaries were too short due to `max_length=100` in `google/pegasus-xsum`.
- **Fix**: Increased `max_length` to 150 for more detailed summaries, maintaining 3-5 sentences via sentence ranking and relevance filtering.

### Summary PDF Readability

- **Issues**:
  - Titles used underscores (e.g., “The_impact_of...”) and had typos (e.g., “bioethic”).
  - Category showed “Ai” or escaped percent signs (`\%`).
  - Summaries included irrelevant text (e.g., “BBC News NI”).
  - PDFs lacked clear formatting.
- **Fixes**:
  - **Title**: Preserved spaces, added regex to fix “bioethic” to “bioethics”.
  - **Category**: Standardized to “AI” (uppercase) and used “percent” (e.g., “AI (81.38 percent)”).
  - **Content**: Enhanced `clean_text_for_pdf` to remove boilerplate (e.g., journal terms, news snippets) and added `filter_relevant_sentences` with keywords (e.g., “artificial intelligence”, “bioethics”).
  - **Formatting**: Added “Article Summary” header, generation date, bold title (14pt), and spaced content (12pt) in `save_text_as_pdf`.

## Handling Restricted Sites

- **ResearchGate**:
  - Selectors: `publication-abstract`, `nova-e-text`.
  - Handles 403 Forbidden/login prompts by suggesting `.txt`/`.pdf` uploads.
- **Digiday**:
  - Selectors: `entry-content`, `article-body` for WordPress sites.
  - Fallbacks: `<p>` tags, `<body>` extraction.
- **Features**:
  - Browser-like headers (`User-Agent`, `Referer`) bypass bot detection.
  - Fallbacks ensure robust extraction.
  - Full text logging (successful/failed) aids debugging.

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

## Sample Usage for Assignment

- **Objective**: Process 3-5 articles from ResearchGate, Digiday, or open-access sites (e.g., The Verge, TechCrunch).
- **Steps**:
  1. Test URLs (e.g., https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8451498/ for AI/bioethics).
  2. Upload `.txt`/`.pdf` for restricted sites.
  3. Verify full extracted text in terminal logs.
  4. Download summary PDFs with clear titles, categories (e.g., “AI”), and 3-5 sentence summaries.
- **Output**:
  - UI: Shows extracted text preview (1000 chars), summary, and download buttons.
  - Console: Logs full text for successful/failed extractions.
  - PDFs: Professional formatting with headers, dates, and clean summaries.
- **Submission**:
  - Include screenshots of UI (sidebar, input, results, themes), terminal logs (full text), and summary PDFs.
  - Highlight encoding fix, nesting fix, logging limit removals, summarizer enhancement, and PDF improvements.

## Thought Process

- **NLP**: Combines zero-shot classification (`bart-large-mnli`) and abstractive summarization (`pegasus-xsum`) with chunking, ranking, and keyword-based filtering.
- **Preprocessing**: ASCII normalization and aggressive boilerplate removal ensure clean input/output.
- **Scraping**: Adaptive selectors and fallbacks handle diverse site structures.
- **UI/UX**: Streamlit with containers, themes, and feedback enhances usability.
- **Logging**: Full text logs (successful/failed) support debugging.
- **PDFs**: Polished formatting meets professional standards.
- **Error Handling**: Addresses encoding, nesting, logging limits, and restricted sites.
- **Documentation**: Comprehensive README for GitHub, covering all fixes and usage.

## Contributing

Feel free to fork the repository, submit issues, or create pull requests to enhance functionality. Suggestions for improving scraping, summarization, or UI are welcome.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.