.env file ochamiz va activate qilamiz  
requirments.txt  o'rnatamiz 

3 terminlda ishlaymiz 
1 terminal python3 manage.py  runserver 
2 terminal  celery -A Admin worker --loglevel=info
3 terminal celery -A Admin beat --loglevel=info

data.py fileda   objectlar bor  shundan korib admin paneldan  product create qilamiz uid va name foto  bir biriga mos Bo'lishiga etibor berin 


pip install rapidfuzz

windowsda
2 terminal  celery -A Admin worker --pool=solo --loglevel=info

