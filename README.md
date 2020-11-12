# image-uploader
 
To run the program enter

docker-compose up -d --build

docker-compose exec web-backend python manage.py migrate 

makes tables in the database and creates 3 plans - Basic, Premium, Enterprise, and Admin user with Admin_password and with Basic plan

I didn't have time to finish some tests and create a production version of the server and upload it to aws, but the server works fine.
it took me like 30 hours to finish this task
