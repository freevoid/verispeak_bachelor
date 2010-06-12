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

TEX_INCLUDEDIR=tex_include
TEX_INCL=er_main
TEX_NOPDF_INCL=seq_verification_nopdf

DIAINCL= use_cases idef0_main idef0_pre enrollment_server_sd verification_server_sd enrollment_client_sd verification_client_sd main_arch deployment
DIAPS = $(DIAINCL)

SVGINCL=gmm_pdf gmm_hist gmm_merged_full

FIXBB=./fixbb
FONTHACK=./hackfont.sh 
EPSINCL= waveform#foo bar

#%.ps: %.dvi
#	dvips $<

#%.pdf: %.ps
#	ps2pdf $<

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

$(INCLUDEDIR)/%_ptex.pdf: $(TEX_INCLUDEDIR)/%.tex
	latex -output-directory $(INCLUDEDIR) $< &&\
		echo "Echoing $*" &&\
		dvips $(INCLUDEDIR)/$*.dvi -o $(INCLUDEDIR)/$*.ps &&\
		$(FIXBB) $(INCLUDEDIR)/$*.ps &&\
		ps2pdf $(INCLUDEDIR)/$*.ps $(INCLUDEDIR)/$*.pdf &&\
		$(CROPPAGE) $(INCLUDEDIR)/$* $@ &&\
		rm -vf $(INCLUDEDIR)/$*.*

$(INCLUDEDIR)/%_tex.pdf: $(TEX_INCLUDEDIR)/%.tex
	$(LATEX) -output-directory $(INCLUDEDIR) $< &&\
		echo "Echoing $*" &&\
		$(CROPPAGE) $(INCLUDEDIR)/$* $@ &&\
		rm -vf $(INCLUDEDIR)/$*.*

$(REPORT_NAME).pdf: $(TEXFILE) $(HEADER) ${PARTS:%=body/%.tex} eps tex_include dia svg $(BIBLE)
	$(LATEX) $(TEXFILE)

$(REPORT_NAME).ps: $(TEXFILE) $(HEADER) ${PARTS:%=%.tex} $(BIBLE) tex_include diaps
	latex $(TEXFILE)
	dvips $(REPORT_NAME).dvi

draft:
	$(LATEX) -draftmode $(TEXFILE)

beamer:
	cd $(PRESENTATION_DIR); make

eps: ${EPSINCL:%=$(INCLUDEDIR)/%_eps.pdf}
tex_include: $(TEX_NOPDF_INCL:%=$(INCLUDEDIR)/%_ptex.pdf) $(TEX_INCL:%=$(INCLUDEDIR)/%_tex.pdf)
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

