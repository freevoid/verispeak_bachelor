.PHONY: force clean bib 

LATEX=pdflatex
CROPPAGE=pdfcrop

CSF=/usr/share/texmf-texlive/bibtex/csf/gost/utf8-ru.csf
TEXCRAP=*.log *.out *.aux

PRESENTATION_DIR=presentation

REPORT_NAME=report
TEXFILE=$(REPORT_NAME).tex

PARTS=intro abbreviations analytic construct technological bzhd economic conclusion appendix

BIBLE_BASE=biblio
BIBLE=$(REPORT_NAME).bbl

HEADER=header.tex

INCLUDEDIR=include

TIKZDIR=tikz
TIKZINCL=er_main

DIAINCL= use_cases idef0_main idef0_pre learning_fsm_times#main_arch
DIAPS = $(DIAINCL)

SVGINCL=gmm_pdf gmm_hist gmm_merged_full

FIXBB=./fixbb
FONTHACK=./hackfont.sh 
EPSINCL= waveform#foo bar

$(INCLUDEDIR)/%_svg.pdf: svg/%.svg
	inkscape $< --export-pdf $@

$(INCLUDEDIR)/%_dia.eps: dia/%.dia
	dia --export=$@ -t eps-pango $<

$(INCLUDEDIR)/%_dia.pdf: dia/%.dia
	TMP=`mktemp` && dia --export=$$TMP -t eps-pango $< && epstopdf --outfile=$@ $$TMP && rm $$TMP

$(INCLUDEDIR)/%_dot.pdf: dot/%.dot
	TMP=`mktemp` && dot -o$$TMP -Tps $< && epstopdf --outfile=$@ $$TMP && rm $$TMP

$(INCLUDEDIR)/%_eps.pdf: eps/%.eps
	$(FIXBB) $< && $(FONTHACK) $< && epstopdf --outfile=$@ $<

$(INCLUDEDIR)/%_tikz.pdf: tikz/%.tex
	$(LATEX) -output-directory $(INCLUDEDIR) $< &&\
		echo "Echoing $*" &&\
		$(CROPPAGE) $(INCLUDEDIR)/$* $@ &&\
		rm -vf $(INCLUDEDIR)/$*.*

$(REPORT_NAME).pdf: $(TEXFILE) $(HEADER) ${PARTS:%=body/%.tex} eps tikz dia svg $(BIBLE)
	$(LATEX) $(TEXFILE)

$(REPORT_NAME).ps: $(TEXFILE) $(HEADER) ${PARTS:%=%.tex} $(BIBLE) tikz diaps
	latex $(TEXFILE)
	dvips $(REPORT_NAME).dvi

draft:
	$(LATEX) -draftmode $(TEXFILE)

beamer:
	cd $(PRESENTATION_DIR); make

eps: ${EPSINCL:%=$(INCLUDEDIR)/%_eps.pdf}
tikz: $(TIKZINCL:%=$(INCLUDEDIR)/%_tikz.pdf)
dia: ${DIAINCL:%=$(INCLUDEDIR)/%_dia.pdf}
diaps: ${DIAINCL:%=$(INCLUDEDIR)/%_dia.ps}
svg: ${SVGINCL:%=$(INCLUDEDIR)/%_svg.pdf}
#dot: $(DOTINCL)

$(BIBLE): $(BIBLE_BASE).bib
	-test -f "$<" && pdflatex -draftmode $(TEXFILE) && bibtex $(REPORT_NAME)

bib:
	-test -f "$(BIBLE_BASE).bib" && pdflatex -draftmode $(TEXFILE) && bibtex $(REPORT_NAME)

force:
	$(LATEX) $(TEXFILE)

clean:
	rm -vf $(TEXCRAP) *.toc *.bbl *.blg $(INCLUDEDIR)/*.pdf body/*.aux \
	   *dot2tex*.dot *dot2tex*.tex *.tmp
	cd $(PRESENTATION_DIR); make clean

$(HEADER):
	echo "Preambule has been chanhed"

