# PDF auto-tagging with PDFix SDK (www.pdfix.net)

# example based on deepdoctection sample for document extraction and 
# document layout analysis tasks using deep learning models
# https://github.com/deepdoctection/deepdoctection

import os
import deepdoctection as dd
from IPython.core.display import HTML
from matplotlib import pyplot as plt

from pdfixsdk.Pdfix import *

pdf = os.path.dirname(os.path.abspath(__file__)) +"/pdf/example.pdf"

# deepdoctection part
analyzer = dd.get_dd_analyzer()  # instantiate the built-in analyzer similar to the Hugging Face space demo
df = analyzer.analyze(path = pdf)  # setting up pipeline
df.reset_state()                 # Trigger some initialization
doc = iter(df)
# page = next(doc) 

# here comes the pdf stuff, process first page only
pdfix = GetPdfix()
pdfDoc = pdfix.OpenDoc(pdf, "")
pdfDoc.RemoveTags(0, None)
structTree = pdfDoc.CreateStructTree()
docStructElem = structTree.GetStructElementFromObject(structTree.GetObject())

for page in doc:

   # image = page.viz()
   # plt.figure(figsize = (25,17))
   # plt.axis('off')
   # plt.imshow(image)
   # plt.show()

   pdfPage = pdfDoc.AcquirePage(page.page_number)

   # prepare page view for coordinate transformation
   cropBox = pdfPage.GetCropBox()
   rotate = pdfPage.GetRotate()
   pdfPageWidth = cropBox.right - cropBox.left
   if rotate == kRotate90 or rotate == kRotate270:
      pdfPageWidth = cropBox.top - cropBox.bottom
   zoom = page.width / pdfPageWidth
   pdfPageView = pdfPage.AcquirePageView(zoom, 0)

   # pre-create objects from AI to the page map
   pdePageMap = pdfPage.AcquirePageMap()
   for layout in page.layouts:
      rect = PdfDevRect()
      rect.left = int(layout.bbox[0])
      rect.top = int(layout.bbox[1])
      rect.right = int(layout.bbox[2])
      rect.bottom = int(layout.bbox[3])
      bbox = pdfPageView.RectToPage(rect)

      # create initial element
      parent = PdeElement(None)
      pdeElemType = kPdeText            # text (default)
      if layout.category_id == '3':     # list
         pdeElemType = kPdeList
      elif layout.category_id == '4':   # table
         pdeElemType = kPdeTable
      elem = pdePageMap.CreateElement(pdeElemType, parent)
      elem.SetBBox(bbox)
      if layout.category_id == '2':     # title
         elem.SetTextStyle(kTextH1)

   # recognize page
   pdePageMap.CreateElements(0, None)

   # prepare page struct element
   pageElem = docStructElem.AddNewChild("NonStruct", docStructElem.GetNumChildren())
   pdePageMap.AddTags(pageElem, False, PdfTagsParams(), 0, None)

   # cleanup
   pdfPageView.Release()
   pdePageMap.Release()
   pdfPage.Release()

# save document
pdfDoc.Save(os.path.splitext(pdf)[0] + "_tagged.pdf", kSaveFull)
pdfDoc.Close()

print("All Done")
