import openai
import pytesseract
from pdf2image import convert_from_path
import pandas as pd

# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual OpenAI API key

# Step 1: Convert PDF to images
pdf_path = 'JPMC2023.pdf'  # Replace with your actual PDF path
pages = convert_from_path(pdf_path)

# Step 2: Function to search for pages with relevant keywords
def find_relevant_pages(pages, keywords):
    relevant_pages = []
    for i, page in enumerate(pages):
        # Extract text from each page
        page_text = pytesseract.image_to_string(page)
        # Check if the page contains any of the keywords
        if any(keyword in page_text for keyword in keywords):
            relevant_pages.append((i, page_text))
    return relevant_pages

# Step 3: Define keywords to search for in the PDF
keywords = ["Net Income", "EPS", "ROTCE", "Return on Tangible Common Equity"]

# Step 4: Find pages containing the financial data
relevant_pages = find_relevant_pages(pages, keywords)

# Step 5: Combine the text from the relevant pages
combined_text = " ".join([page_text for _, page_text in relevant_pages])

print(relevant_pages)

# Step 6: Define a function to use GPT-4 to extract structured data
def extract_data_with_gpt4(extracted_text):
    prompt = f"""
    Extract the financial data for Year, Net Income, EPS, and ROTCE from the following text. 
    Structure it in the following format:
    Year, Net Income, EPS, ROTCE

    Text:
    {extracted_text}
    """

    # Call GPT-4 model via OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use GPT-4 model
        messages=[
            {"role": "system", "content": "You are an assistant that extracts structured data from financial reports."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0  # Keep temperature low for factual accuracy
    )

    structured_data = response['choices'][0]['message']['content'].strip()
    return structured_data

# Step 7: Use GPT-4 to extract structured data from the combined relevant text
structured_data = extract_data_with_gpt4(combined_text)

# Step 8: Process the structured data into a DataFrame
lines = structured_data.splitlines()
data = [line.split(',') for line in lines]
df_financial_data = pd.DataFrame(data[1:], columns=data[0])

# Step 9: Display the DataFrame
print("Extracted Financial Data from 2005 to 2023:")
print(df_financial_data)

# Optional: Save the DataFrame to a CSV file for further analysis
df_financial_data.to_csv('financial_data_2005_2023.csv', index=False)
