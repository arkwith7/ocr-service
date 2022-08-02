
# import module
from pdf2image import convert_from_path
 
 
# Store Pdf with convert_from_path function
images = convert_from_path('수출면장-PDF.pdf')
 
for i in range(len(images)):
   
      # Save pages as images in the pdf
    images[i].save('../output/수출면장-PDF-img'+ str(i) +'.jpg', 'JPEG')