- ENTRO NELLA CARTELLA
## cd info_segugio_assistant

- INSTALLARE LA LIBRERIA POETRY
## poetry install

- ATTIVARE VIRTUAL ENVIRONMENT
## eval $(poetry env activate)
- ATTIVARE VIRTUAL ENVIRONMENT SU WINDOW ( i percorsi di Windows vanno trattati con gli slash / invece dei backslash \ e le lettere dei drive (C:) vanno scritte in minuscolo con /c/.)
## source /c/Users/Windows10/AppData/Local/pypoetry/Cache/virtualenvs/info-segugio-assistant-bdREUtaS-py3.13/Scripts/activate

- LANCIARE L'APPLICATIVO(src perché è il percorso dove poetry mi ha creato il progetto )
## chainlit run src/info_segugio_assistant/__init__.py -w

- INSTALLARE LA LIBRERIA OPENAI
## poetry add openai