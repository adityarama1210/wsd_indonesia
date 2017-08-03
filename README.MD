Crawling(Online dictionary based):
Script crawling dan beberapa file terkait ada pada folder "Crawling"

Cleaner:
Folder yang berisi script untuk membersihkan korpus dari tanda baca (bahasa Indonesia)
dan berisi script untuk membersihkan tag-tag sense yang sudah diberikan IMS untuk mengambil tag-tag terbaik saja

Model Word Embedding:
File model dari word embedding (Word2Vec) berada di folder "model_ignore"


File hasil anotasi dan script evaluasi:
Berada pada folder "WordAlignmentEvaluation"
Untuk menjalankan evaluasi: "python automatic_evaluation.py"

Folder Post Process:
Berisi file hasil post process dari file A3 (hasil alignment)

How to run:
python wsd.py testing <test_file> <featurer>

Example:
python wsd.py testing Resources/testing_file.txt f1
python wsd.py testing Resources/testing_file.txt f3
