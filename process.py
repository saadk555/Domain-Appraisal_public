import re
from collections import Counter
from nltk.corpus import stopwords  # Import stopwords for basic filtering
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from api import get_registered_domains, whois_creation_date, get_domain_price
import matplotlib.pyplot as plt
from PIL import Image
import io
import numpy as np
import matplotlib.dates as mdates
import datetime

def generate_pdf(domain_name):
    """
    Generates a PDF report for a domain name, identifying relevant keywords.

    Args:
        domain_name (str): The domain name to analyze.
    """

    # Create a new PDF with Reportlab
    c = canvas.Canvas("new.pdf", pagesize=letter)

    # Set the font to Times-Roman and size to 10 for the appraisal text
    c.setFont("Times-Roman", 10)

    # Draw the appraisal text
    c.drawString(230, 580, "Domain Name's Appraisal Value:")

    # Set the font to Times-Bold and size to 10 for the price
    c.setFont("Times-Bold", 10)

    # Draw the price
    c.drawString(257, 570, "$10,00,000 (1M)")

    # Set the font to Helvetica-Bold and size to 14 for the heading
    c.setFont("Helvetica-Bold", 10)

    # Draw the heading
    c.drawString(50, 530, "COMMENTS: ")

    # Set the font to Helvetica-Oblique (italic) and size to 9 for the text
    c.setFont("Helvetica-Oblique", 9)

    # Draw the text
    c.drawString(125, 530, "Hello, World!")

    # Path to the dictionary file (assuming it's a separate file)
    dictionary_file = "dictionary.txt"

    # Read keywords from the dictionary
    keywords = [line.strip().lower() for line in open(dictionary_file, "r")]

    # Check if dictionary is empty
    if not keywords:
        print("Warning: Keyword dictionary is empty!")
        return

    # Get the first part of the domain name (without extension)
    domain_part = domain_name.split('.')[0].lower().strip()

    # Load stopwords for basic filtering (optional)
    stop_words = set(stopwords.words('english'))

    # Train n-gram model using the corpus (considering words and numbers)
    corpus_file = "corpus.txt"  # Path to the corpus file containing n-grams
    with open(corpus_file, "r") as f:
        """
        Processing logic redacted for demo purposes.
        """
        all_grams = []
        for line in f:
            words = [word.lower() for word in line.strip().split() if word not in stop_words]
            all_grams.extend([tuple(words[i:i + j]) for i in range(len(words)) for j in range(1, 3)])  # Consider 1 & 2-grams
        

    ngram_counts = Counter(all_grams)

    # Find potential keywords using regular expression search
    found_keywords = [
        keyword.lower() for keyword in keywords
        if re.search(rf"{keyword.lower()}", domain_part.lower())
    ]


    print("Found Keywords:", found_keywords)

    # Filter and prioritize keywords based on co-occurrence in the corpus (considering proximity)
    filtered_keywords = []
    for keyword in found_keywords:
        max_score = 0
        best_ngram = None
        # Search for n-grams where the keyword and a word from the domain part are present
        for ngram in ngram_counts:
            if keyword in ngram and (domain_part in ngram or any(w in domain_part for w in ngram)):
                score = ngram_counts[ngram]
                if score > max_score:
                    max_score = score
                    best_ngram = ngram
        if best_ngram:
            filtered_keywords.append(keyword)  # Include only the keyword (not the full n-gram)

    # Sort keywords by score (descending)
    prioritized_keywords = sorted(filtered_keywords, key=lambda x: x[1], reverse=True)

    # Calculate the total length of the prioritized keywords
    keyword_length = sum(len(keyword) for keyword in prioritized_keywords)

    # Calculate the length of the domain name (excluding the extension)
    domain_length = len(domain_name.split('.')[0].strip())

    # Calculate the ratio of keyword length to domain length
    ratio = keyword_length / domain_length

    remaining_letters = domain_length - keyword_length

# Only proceed with ratio calculation if remaining letters > 2
    if remaining_letters > 2:
    # If the ratio is less than a certain threshold, discard the keywords
        if ratio < 0.7:  # Adjust this threshold as needed
            print("Keyword is not a proper keyword because the number of non-meaningful words in the domain is high.")
            prioritized_keywords = []

    # Print the prioritized keywords
    print("Prioritized Keywords:", prioritized_keywords)

    tld = domain_name.split('.')[-1]
    
    #domain_info = get_registered_domains(tld) | please uncomment it in the production
    domain_info = "269,424,854"
    age = "1996"  # Placeholder (replace with actual logic)


    # Update bullet points with identified keywords
    points = [
        "AVERAGE KEYWORD PRICE: $2070",
        f"FOUND KEYWORDS: {', '.join(prioritized_keywords)}",
        f"KEYWORD COUNT: {len(set(prioritized_keywords))}",
        "LETTERS COUNT: " + str(len(domain_name.split('.')[0].strip()) if '.' in domain_name else 0),
        f"AGE: {age}",  # Placeholder (replace with actual logic)
        "HYPHEN: " + ("No" if "-" not in domain_name else "Yes"),
        "DIGITS: " + ("No" if not re.search(r"\d", domain_name) else "Yes"),
        "",
        "",
        "SALES PER TLD: $66.1 Million in 2022",
        f"REGISTERED DOMAINS: {domain_info}",
        "GLOBAL TLD RANKING: 1st (48.7%)",
    ]
    # Get the bullet point style from the sample style sheet
    styles = getSampleStyleSheet()

    # Define a custom style for bold text
    bold_style = ParagraphStyle(
        name='Bold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12
    )

    bullet_style = styles["Bullet"]

    domain_infos = int(domain_info.replace(',', ''))

    # Pie Chart Generation (with REGISTERED DOMAINS removed)
    labels = ['KEYWORD COUNT', 'LETTERS COUNT', 'AGE']
    values = [len(set(prioritized_keywords)), len(domain_name.split('.')[0].strip()), 1] 

    # Normalize data to percentages
    total = sum(values)
    normalized_values = [v / total * 100 for v in values] 

    # Shades of black color list
    grayscale_colors = ['#000000',  # black
                        '#333333',  # dark gray
                        '#666666',  # medium gray
                        '#999999']  # light gray

    # Create the figure with a transparent background
    plt.figure(figsize=(10, 10), facecolor='none')

    patches, texts, autotexts = plt.pie(normalized_values, labels=labels, autopct="%1.1f%%", colors=grayscale_colors, textprops={'color':"black", 'fontsize': 14, 'fontweight': 'bold'})

    # Change the color of the percentage labels to white
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(14)  # Increase the font size
        autotext.set_fontweight('bold')  # Make the font bold
    # Rotate the autopct texts
    for autotext in autotexts:
        autotext.set_rotation(45)

    plt.title("Domain Overall Features", fontweight='bold', fontsize=20)

    # Set transparent background
    plt.gca().patch.set_alpha(0.0)

    # Remove extra white space around the pie chart
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)  

    # Save the figure with a transparent background
    plt.tight_layout()
    plt.savefig("piechart.png",  transparent=True) 
    
    # Generate age line graph
    current_year = datetime.datetime.now().year
    #registration_year = 1996  # Placeholder (replace with actual logic)
    registration_year = whois_creation_date(domain_name)  # Placeholder (replace with actual logic)
    years = [datetime.datetime(year, 1, 1) for year in range(registration_year, current_year + 1)]
    age_values = [year.year - registration_year for year in years]

    # Specific Years to highlight
    #drops = ['laptop.com', '$ 375,000.00 USD', '2020'] 
    drops = list(get_domain_price(domain_name))

    if drops[0] is None:
        print(drops[1])
        drops = [None, "Domain doesn't have any past sales", ""]

    fig, ax = plt.subplots(figsize=(10, 6))  # Increase the size of the figure

    # Plot the main line
    ax.plot(years, age_values, color='black', linewidth=2)  # Increase the line width

    # Plot points for the specific years
    drop_year = int(drops[-1]) if drops[-1].isdigit() else current_year  # Select only the last element in the list
    x = datetime.datetime(drop_year, 1, 1)  # Find dateTime object for drop year
    y = drop_year - registration_year  # Calculate corresponding age value
    ax.plot(x, y, marker='o', markersize=8, color='black')  # Plot black point
    offset = -3  # Adjust this value as needed
    ax.text(x, y + offset, drops[1], fontsize=12, fontweight='bold')  # Increase the font size and make it bold

    ax.set_xlabel("Year", fontsize=12, fontweight='bold')  # Increase the font size and make it bold
    ax.set_ylabel("Age", fontsize=12, fontweight='bold')  # Increase the font size and make it bold
    ax.set_title("Domain Age", fontsize=20, fontweight='bold')  # Increase the font size and make it bold

    # Format x-axis ticks for years
    ax.xaxis.set_major_locator(mdates.YearLocator(base=5))  # Display every 5th year
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Adjust font size and temporarily remove rotation
    ax.tick_params(labelsize=10)  # Increase the font size

    # Add grid lines
    ax.grid(True, color='gray', linestyle='--', linewidth=3)

    # Add note if drops is not empty
    if drops:
        plt.text(0.5, -0.35, 'Note: Points show the domain sale', ha='center', va='center', transform=ax.transAxes, fontsize=10, fontweight='bold')  # Increase the font size and make it bold

    # Tight layout and display the plot
    plt.tight_layout()
    plt.savefig("age_graph.png", transparent=True)  # Save the figure with a transparent background
    
    # Draw each bullet point as a separate paragraph
    y = 300
    for point in points:
        if ':' in point:
            keyword, text = point.split(':', 1)
            p = Paragraph(f"<b>{keyword}:</b>{text}", bullet_style)
        else:
            p = Paragraph(point, bullet_style)
        p.wrapOn(c, 500, 400)
        p.drawOn(c, 50, y)
        y -= 15  # Move the y-coordinate down for the next point

    # Draw the image on the canvas
    #c.drawImage("piechart.png", 380, 300, width=150, height=150, mask='auto')
    #c.drawImage("age_graph.png", 380, 50, width=150, height=100, mask='auto')  
    c.drawImage("piechart.png", 380, 250, width=200, height=200, mask='auto')
    c.drawImage("age_graph.png", 380, 50, width=200, height=200, mask='auto') 
    c.save()

    # Open the existing PDF and the new PDF
    existing_pdf = PdfReader("Domain-Appraisal.pdf")
    new_pdf = PdfReader("new.pdf")

    # Get the first page from the existing PDF
    page = existing_pdf.pages[0]

    # Merge the new PDF onto the existing page
    page.merge_page(new_pdf.pages[0])

    # Create a PdfWriter object and add the page to it
    output = PdfWriter()
    output.add_page(page)

    # Write the output to a new file
    with open("output.pdf", "wb") as output_pdf:
        output.write(output_pdf)

if __name__ == "__main__":
    # Call the function with a domain name
    generate_pdf("laptop.com")