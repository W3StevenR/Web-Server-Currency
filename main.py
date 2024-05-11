import os

import matplotlib.pyplot as plt
import base64
from io import BytesIO
from bs4 import BeautifulSoup


# classe que ira plotar e exportar figuras


class Exportador:
  def __init__(self):
    pass

  def exportar(self, plot, str_html, h, w):
    # Create a matplotlib figure
    fig = plt.figure(figsize=(h, w))
    # Add your plot elements here
    # For example, a simple line plot
    plt.plot(plot)

    # Save the figure to a BytesIO object
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    tmpfile.seek(0)  # Move to the beginning of the file

    # Encode the image data in base64
    codif = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(str_html, 'html.parser')

    # Now, you can use BeautifulSoup to manipulate the HTML structure
    # For example, adding a new paragraph:
    new_paragraph = soup.new_tag("p")
    new_paragraph.string = "This is a new paragraph added with BeautifulSoup."
    soup.body.append(new_paragraph)

    # Convert the modified BeautifulSoup object back to a string
    modified_html = str(soup)

    # Write the modified HTML to a file
    with open('modified_plot.html', 'w') as f:
      f.write(modified_html)


import requests

with open("templates/index.html") as o:
  index = o.read()
soup = BeautifulSoup(index, 'html.parser')

# Step 4: Extract or manipulate the HTML
# For demonstration, let's print the entire HTML content
print(soup.prettify())

fig = plt.figure()
# Add your plot elements here
# For example, a simple line plot
plt.plot([1, 2, 3, 4], [3, 4, 5, 6])

# Save the figure to a BytesIO object
path_save = os.path.join("temp","temp.png")
fig.savefig(path_save, format='png')


# Encode the image data in base64
#codif = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

# Now, you can use BeautifulSoup to manipulate the HTML structure
# For example, adding a new paragraph:
new_paragraph = soup.new_tag("p")
new_paragraph.string = "This is a new paragraph added with BeautifulSoup."
soup.body.append(new_paragraph)
nova_imagem = soup.new_tag('img', src="temp/temp.png")
soup.body.append(nova_imagem)

# Convert the modified BeautifulSoup object back to a string
modified_html = str(soup)

# Write the modified HTML to a file
with open('templates/index.html', 'w') as f:

  f.write(modified_html)

with open('index.html', 'r') as f:
  f.read()
  print(f)
