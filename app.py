from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
users = []

def load_users():
    with open('users.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split(',')
            users.append({'username': username, 'password': password})

def save_users():
    with open('users.txt', 'w') as file:
        for user in users:
            file.write(f"{user['username']},{user['password']}\n")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not is_username_taken(username):
            users.append({'username': username, 'password': password})
            save_users()
            return redirect('/')
        else:
            return "Username already taken. Please choose a different username."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username  # Установить значение сеанса
                return redirect('/account')
        return "Invalid username or password."
    return render_template('login.html')

@app.route('/')
def index():
    logged_in = 'username' in session  # Проверить, вошел ли пользователь в аккаунт
    return render_template('index.html', logged_in=logged_in, users=users)

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'username' in session:  # Проверить, вошел ли пользователь в аккаунт
        logged_in = 'username' in session
        render_template('index.html', logged_in=logged_in, users=users)
        if request.method == 'POST':
            username = session['username']  # Получить имя пользователя из сеанса
            file = request.files['photo']
            filename = f"static/photos/{username}.jpg"
            file.save(filename)
            return redirect('/account')

        username = session['username']  # Получить имя пользователя из сеанса
        user = next((user for user in users if user["username"] == username), None)
        return render_template('account.html', logged_in=True, user=user)
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Удалить значение сеанса
    return redirect('/')

@app.route('/profile/<username>')
def profile(username):
    user = next((user for user in users if user["username"] == username), None)
    if user:
        return render_template('profile.html', user=user)
    else:
        return "Пользователь не найден"

@app.route('/messages/<username>')
def messages(username):
    # Код для отображения сообщений пользователя
    return render_template('messages.html', username=username)
####################################################
@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' in session:
        sender = session['username']
        recipient = request.form['recipient']
        message = request.form['message']
        # Сохранить сообщение в файле отправителя и получателя
        save_user_message(recipient, f"{sender}: {message}")
        return redirect(f'/messages/{recipient}')
    else:
        return redirect('/login')
####################################################
def save_user_message(username, message):
    with open(f"{username}_messages.txt", 'a') as file:
        file.write(message + '\n')

@app.route('/messages')
def user_messages():
    if 'username' in session:
        username = session['username']
        # Загрузить сообщения из файла пользователя
        messages = load_user_messages(username)
        return render_template('messages.html', username=username, messages=messages)
    else:
        return redirect('/login')

def load_user_messages(username):
    filename = f"{username}_messages.txt"
    try:
        with open(filename, 'r') as file:
            messages = file.read().splitlines()
    except FileNotFoundError:
        messages = []
    return messages

def save_user_messages(username, messages):
    filename = f"{username}_messages.txt"
    with open(filename, 'w') as file:
        file.write('\n'.join(messages))
def is_username_taken(username):
    for user in users:
        if user['username'] == username:
            return True
    return False

if __name__ == '__main__':
        load_users()
        app.run(port=80)