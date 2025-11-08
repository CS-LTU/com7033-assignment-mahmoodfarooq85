Hospital Secure Web App

This is my(mahmood's) project for the Secure Software Development assignment(COM-7033)
I built it using Flask (Python) 

 What it is,

It has Home, About, Register, and Data pages.

You can register a new user.

This app uses SQLite to store user information.

It shows a sample health dataset (stroke_data.csv) as an HTML table.(provided by our teacher)

Right now, it includes:

Input validation for registration

Password hashing (to keep passwords safe)

Maybe I will add more features later like better encryption and maybe MongoDB.

 How to run it,
I open my project in VS Code and type the below written comand in the terminal,
"python app.py"

it shows, like this,
"http://127.0.0.1:5000"

I also added simple unit test to check that all my pages on flask are working properly, these tests were  (Home, About and Register pages) by using this below comand in vs code terminal 
"python -m unittest test_app.py"

