from lib.DocLoader import DocLoader

# dl = DocLoader('data/CVPR-Paper.pdf')
dl = DocLoader('data/FPA Review.docx')

dl.read_contents()

print(dl.get_doc_text())