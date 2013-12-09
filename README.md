scisumm
=======

Single Document Summarization of Scientific Documents

Instructions:

1. Run the requirements.txt through pip
        pip install -r requirements.txt
2. Additionally, nltk data needs to be downloaded without which the scripts
   wont run succesfully.
        run `nltk.download()` inside a python shell
        currently, the stopwords from the corpus are required.
3. Download ROUGE and put the folder RELEASE inside scisumm/lib/ROUGE
4. Change the address of the base directory in scr/Config.py
