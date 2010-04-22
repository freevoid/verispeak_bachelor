PRESENTATION = slides.pdf

.PHONY: slides.pdf
slides.pdf:
	pdflatex slides.tex

all: $(PRESENTATION)

TEXCRAP=*.log *.out *.aux

clean:
	rm -vf $(TEXCRAP) *.pdf *.snm *.toc *.nav
