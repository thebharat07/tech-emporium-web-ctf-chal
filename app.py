from flask import Flask, render_template, request, redirect, url_for, session
import database
import os
import uuid

app = Flask(__name__)

# REQUIRED: Secret key is needed to encrypt the session cookie
app.secret_key = 'sql_injection_lab_secret_key'

UPLOAD_FOLDER = '/app/uploads'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    query = None
    error = None
    if request.method == 'POST':
        # Get user from database
        user, query = database.login_user(request.form['username'], request.form['password'])
        
        if user:
            # 1. STORE USER INFO IN SESSION
            # This "logs them in" and persists across different pages
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            
            # 2. REDIRECT BASED ON ROLE
            # This updates the URL in the browser address bar
            if session['role'] == 'administrator':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('products'))
        else:
            error = "Invalid Credentials"

    return render_template('login.html', error=error, query=query)

@app.route('/products')
def products():
    # If not logged in, you can choose to redirect to login or show as guest
    # For this lab, let's just grab the search results
    search = request.args.get('search', '')
    results, query, error = database.search_products(search)
    
    # We pass 'session' as the 'user' variable to templates
    return render_template('products.html', 
                           results=results, 
                           query=query, 
                           error=error, 
                           user=session if 'username' in session else None)

@app.route('/users')
def users():
    user_id = request.args.get('id', '')
    user, query = None, None
    if user_id:
        user, query = database.get_user_by_id(user_id)
    return render_template('users.html', user=user, query=query)

@app.route('/admin')
def admin_dashboard():
    # Count current files
    plugins = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    slots_used = len(plugins)
    
    # Logic: Only allow upload if less than 2 files exist
    can_upload = slots_used < 2
    
    return render_template('admin.html', plugins=plugins, slots_used=slots_used, can_upload=can_upload)

    
@app.route('/admin/upload', methods=['POST'])
def upload():
    # 1. Check current quota
    current_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    if len(current_files) >= 2:
        return "<h1>FATAL ERROR: STORAGE DEPLETED</h1><p>WORM (Write Once Read Many) Drive is full. Contact System Administrator for hardware replacement.</p>", 403

    file = request.files.get('file')
    if file:
        # 2. Get original filename and extension
        original_name = file.filename
        name, ext = os.path.splitext(original_name)

        # 3. THE DEVIOUS PART: Add a unique random suffix
        # Even if they upload the same file again, it gets a new name.
        unique_id = uuid.uuid4().hex[:6] 
        new_filename = f"{name}_{unique_id}{ext}"
        
        # 4. Save the file
        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
        
    return redirect('/admin')

@app.route('/admin/run_tool')
def run_tool():
    filename = request.args.get('file')
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Safety: check if file actually exists
    if not os.path.exists(path):
        return "File not found.", 404

    try:
        import subprocess
        # Executes the file. 
        output = subprocess.check_output(['python3', path], stderr=subprocess.STDOUT, timeout=60)
        return f"<pre>{output.decode()}</pre><br><a href='/admin'>Back</a>"
    except Exception as e:
        return f"Error: {str(e)}<br><a href='/admin'>Back</a>"
@app.route('/logout')
def logout():
    session.clear() # Clear the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)