echo '-> django checks'
python manage.py check --deploy
echo '-> django migrations'
python manage.py migrate --noinput
#echo '-> django statics'
#python manage.py collectstatic 