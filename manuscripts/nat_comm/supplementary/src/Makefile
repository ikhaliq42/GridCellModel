# makefile pro preklad LaTeX verze Bc. prace
#
#
# asi budete chtit prejmenovat:
CO=SI_text
IMAGES = fig/
DROPBOX_DIR = ~/Dropbox/shared_data/noise/


.PHONY: fig $(CO).pdf

all: pdf

final:
	cd fig; $(MAKE) grafy
	$(MAKE) pdf

pdf: fig $(CO).pdf

$(CO).ps: $(CO).dvi
	dvips $(CO)

$(CO).pdf: 
	pdflatex $(CO)
	bibtex $(CO)
	pdflatex $(CO)

$(CO).dvi: $(CO).tex $(CO).bib fig
	latex $(CO)
	bibtex $(CO)
	latex $(CO)
	latex $(CO)

clean:
	rm -f *.dvi *.log $(CO).blg $(CO).bbl $(CO).toc *.aux $(CO).out
	rm -f $(CO).pdf
	cd $(IMAGES); $(MAKE) clean
	cd $(CD_DST_DIR); rm -rf $(final_files)

#pack:
#	tar czvf bp-xjmeno.tar.gz *.tex *.bib *.cls *.pdf *.eps \
#	    Makefile ChangeLog README TODO

fig:
	cd fig; $(MAKE)

dropbox:
	cp $(CO).pdf ${DROPBOX_DIR}
