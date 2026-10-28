#!/bin/sh
# Rebuild the e-reader and print editions from the volume pages in the project folder.
# Needs: python3, and the Swift toolchain once to compile ./render (macOS's WebKit and PDFKit do the work).
set -e
cd "$(dirname "$0")/../.."
HERE=.build/editions
[ -x $HERE/render ] || swiftc -O $HERE/render.swift -o $HERE/render
python3 $HERE/make_covers.py . editions/covers        # cover images, used by the EPUBs
python3 $HERE/make_epub.py . editions/epub
python3 $HERE/make_pdfs.py . editions/pdf             # two passes per book, for the contents page numbers
rm -f editions/Engineers-Syllabus-EPUB.zip editions/Engineers-Syllabus-PDF.zip
(cd editions/epub && zip -q -X ../Engineers-Syllabus-EPUB.zip *.epub)
(cd editions/pdf && zip -q -X ../Engineers-Syllabus-PDF.zip *.pdf)
ls -la editions/*.zip
