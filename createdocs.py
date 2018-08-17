from docxtpl import DocxTemplate

def new_letter(info_list):
    
    doc = DocxTemplate("correspondence.docx")
#    name = "John"
#    address = "32 Birchland Crescent"
    context = {'recipient': name, 'address': address}
    doc.render(context)
    doc.save("generated_doc.docx")


new_letter()
