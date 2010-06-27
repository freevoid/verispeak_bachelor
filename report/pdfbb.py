#!/usr/bin/env python

import sys
from math import ceil, floor

import numpy as np
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams

filename = sys.argv[-1]
# Open a PDF file.
fp = open(filename, 'rb')
# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
doc = PDFDocument()
# Connect the parser and document objects.
parser.set_document(doc)
doc.set_parser(parser)
# Check if the document allows text extraction. If not, abort.
#if not doc.is_extractable:
#    sys.exit(1)
# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()
laparams = LAParams()
# Create a PDF device object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)

def generate_bboxes(doc):
    for page in doc.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()    
        bboxes = np.array([a.bbox for a in layout.objs])
        yield (bboxes[:,0].min(), bboxes[:,1].min(), bboxes[:,2].max(), bboxes[:,3].max())

def format_bbox(bbox):
    return '%%%%BoundingBox: %d %d %d %d' % (floor(bbox[0]), floor(bbox[1]), ceil(bbox[2]), ceil(bbox[3]))
    # (math.np.concatenate([np.floor(bbox[:2]), np.ceil(bbox[2:])]).tolist()
    return ("%%HiResBoundingBox: %(x1).6f %(y1).6f %(x2).6f %(y2).6f" %
                {'x1': bbox[0], 'y1': bbox[1], 'x2': bbox[2], 'y2': bbox[3]})

print "Ghostscript replacer"
print "Copyright (C) 2010 Nikolay Zakharov. Do what you want."
print ""
for pnum, bbox in enumerate(generate_bboxes(doc)):
    print "Page %d" % (pnum + 1)
    print format_bbox(bbox)

sys.exit(0)

