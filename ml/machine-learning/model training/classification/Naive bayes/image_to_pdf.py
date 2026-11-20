import fitz
import os

print(os.getcwd())
doc= fitz.open()
image_path= r"C:\Users\gupta\OneDrive\Pictures\Screenshots 1\pyq2.png"

image_path2= r"C:\Users\gupta\OneDrive\Pictures\Screenshots 1\pyq1.png"
image_rect= fitz.Rect(100,100,300,300)
page = doc.new_page()
page.insert_image(image_rect,filename=image_path)
page2 = doc.new_page()
page2.insert_image(image_rect,filename=image_path2)

doc.save("dbms2026.pdf")
doc.close()

