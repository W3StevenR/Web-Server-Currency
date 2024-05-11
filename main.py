import os

import matplotlib.pyplot as plt
import base64
from io import BytesIO
from bs4 import BeautifulSoup


# classe que ira plotar e exportar figuras


class ProcDados:
  def __init__(self):
    pass

  # inicialmente plot deve ser um plot e path_html deve ser path ate index.htl
  def exportar(self, plot, path_html):
    with open("templates/index.html") as o:
      index = o.read()
    soup = BeautifulSoup(index, 'html.parser')

    # For demonstration, let's print the entire HTML content
    print(soup.prettify())

    fig = plt.figure()
    # Add your plot elements here
    # For example, a simple line plot
    plt.plot([1, 2, 3, 4], [3, 4, 5, 6])

    # Save the figure to a BytesIO object
    path_save = os.path.join("temp", "temp.png")
    fig.savefig(path_save, format='png')

    # Encode the image data in base64
    # codif = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    # Now, you can use BeautifulSoup to manipulate the HTML structure
    # For example, adding a new paragraph:
    new_paragraph = soup.new_tag("p")
    new_paragraph.string = "Paragrafo de Teste."
    soup.body.append(new_paragraph)
    nova_imagem = soup.new_tag('img', src="temp/temp.png")
    soup.body.append(nova_imagem)

    # Converte objeto BeautifulSoup modificado de volta para string
    modified_html = str(soup)

    # Write the modified HTML to a file
    with open('templates/index.html', 'w') as f:
      f.write(modified_html)
