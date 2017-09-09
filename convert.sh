#!/bin/bash
FILE=${BASH_ARGV[0]}
>&2 echo "Parsing file \""$FILE"\""

if [ ! -e $FILE ]
then
    >2& echo "File not found!"
    exit
fi

Start_NUM=$(cat $FILE -n | grep 'begin{document}' | gawk '{print $1}')
End_NUM=$(cat $FILE -n | grep 'end{document}' | gawk '{print $1}')

>&2 echo "Parsing from $Start_NUM to $End_NUM"

cat $FILE | tail -n +$Start_NUM | head -n $((End_NUM-Start_NUM)) \
    | sed 's/\\item<.*>/\\item/g' \
    | sed 's/</\\lt /g' \
    | sed 's/>/\\gt /g' \
    | sed '/^\s*$/d' \
    | sed '/%.*$/d' \
    | sed 's/\\begin{document}\[\?.*\]\?/<section>/g' \
    | sed 's/\\subsection{.*}/<\/section>/g' \
    | sed 's/\\end{frame}/<\/section>/g' \
    | sed 's/\\begin{frame}\[\?.*\]\?/<section>/g' \
    | sed 's/\\end{frame}/<\/section>/g' \
    | sed 's/\\frametitle{\(.*\)}/<h2>\1<\/h2>/g' \
    | sed '/\\section{.*}.*$/d' \
    | awk 'BEGIN{p=1;content=""} /\\item/ { if (p==1) {p=0} else {print "<li>"content"</li>"; content="";}} /\\end\{itemize\}/ { if (p==0) {print "<li>"content"</li>"; content=""; p=1;} } {if (p==1) {print} else {content=content$0"\n";}}' \
    | sed 's/\\begin{itemize}/<ul>/g' \
    | sed 's/\\end{itemize}/<\/ul>/g' \
    | sed 's/\\item//g' \
    | sed 's/\\bm/\\boldsymbol/g' \
    | sed 's/\\includegraphics\[\?.*\]\?{\(.*\)}/<img src="\1"><\/img>/g' \
    | sed 's/\\begin{center}//g' \
    | sed 's/\\end{center}//g' \
    | sed 's/\\begin{flushleft}/<div style="text-align:left;">/g' \
    | sed 's/\\end{flushleft}/<\/div>/g' \
    | sed 's/``/&ldquo;/g' \
    | sed "s/''/&rdquo;/g" \
    | sed -Ee's/.*\{\\bf([^}]*(\{[^{}]*\}[^{]*)*)\}/<b>\1<\/b>/g' \
    | sed 's/\\end{center}//g'

