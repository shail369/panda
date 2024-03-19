from flask import Flask, render_template, request, session, jsonify,redirect    
from flask_mysqldb import MySQL
from flask import redirect, url_for
import MySQLdb.cursors, re, time, bcrypt, jwt, os, ffmpeg, subprocess
from werkzeug.utils import secure_filename
import base64, cv2
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip, concatenate_audioclips, ImageClip, concatenate_videoclips
from moviepy.video.fx import fadein
import psycopg2
import io
import tempfile

db_url = "postgresql://shail_369:rkkkT45_7SwCazYO00GEvA@slideshow-9000.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/slideshow?sslmode=verify-full"

conn = psycopg2.connect(db_url)
cursor = conn.cursor()

current = 1280

SECRET_KEY = "suspense"

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(hashed_password, input_password):
    hashed_password_bytes = bytes(hashed_password)
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password_bytes)

def create_jwt_token(name, username, email, favourite_sport, id):
    payload = {"name": name, "username": username, "email": email, "favourite_sport": favourite_sport, "id" : id}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        return "Invalid token. Please log in again."

def get_last_part_after_slash(input_string):
    result = ""

    for char in reversed(input_string):
        if char == '/':
            break
        result = char + result

    return result

def verify_user(username, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kaptaan WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        if verify_password(user['password'], password):
            return True
    return False

def images_to_video(selected_images):
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    cursor = conn.cursor()
    cursor.execute("SELECT image_data FROM current WHERE user_id = %s",(session['id'],))
    images_data = cursor.fetchall()
    cursor.close()

    images = []
    max_height = 720
    max_width = 1280
    for image_data in images_data:
        image_array = np.frombuffer(image_data[0], np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        height, width, _ = frame_rgb.shape
        print(height,width,_)
        images.append(frame_rgb)

    if images:
        output_video = os.path.join(upload_dir, "output_video.mp4")

        duration_per_image = 2 

        final_frames_with_durations = []

        for frame_rgb in images:
            height, width, _ = frame_rgb.shape
            if width != max_width or height != max_height:
                scale_factor = min(max_width / width, max_height / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                resized_frame = cv2.resize(frame_rgb, (new_width, new_height))
                offset = ((max_width - new_width) // 2, (max_height - new_height) // 2)
                background = Image.new('RGB', (max_width, max_height), (203, 215, 223))
                background.paste(Image.fromarray(resized_frame), offset)
                final_frames_with_durations.append((np.array(background), duration_per_image))
            else:
                final_frames_with_durations.append((np.array(frame_rgb), duration_per_image))

        clip = ImageSequenceClip([frame[0] for frame in final_frames_with_durations], 
                                 durations=[frame[1] for frame in final_frames_with_durations])
        clip.write_videofile(output_video, codec='libx264', fps=24) 
        input_filepath = os.path.join(upload_dir, 'output_video.mp4')
        video_path = os.path.join(app.static_folder, 'new_output_video.mp4')
        original_video = VideoFileClip(input_filepath)
        print("Video generated successfully:", output_video)
        if current == 1280:
            new_resolution = (1280,720)
        elif current == 1920:
            new_resolution = (1920,1080)
        else:
            new_resolution = (480,360)
        resized_video = original_video.resize(new_resolution)
        resized_video.write_videofile(video_path)
    else:
        print("No images found")


def change_duration(selected_images, duration,transition):
    if selected_images == []:
        return
    if duration == "":
        return
    print(duration)
    for image in selected_images:
        print(image)
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    cursor = conn.cursor()
    cursor.execute("SELECT filename, image_data, duration FROM current WHERE user_id = %s ORDER BY id",(session['id'],))
    images = cursor.fetchall()
    cursor.close()

    final_frames_with_durations = []
    
    max_width = 1280
    max_height = 720
    for image_data in images:
        filename = image_data[0]
        if filename in selected_images:
            cursor = conn.cursor()
            cursor.execute('UPDATE current SET duration = %s WHERE filename = %s AND user_id = %s' ,
                       (duration,filename,session['id'],))
            conn.commit()
            cursor.close()

def transitions(selected_images, transition):
    try:
        if not selected_images:
            print("No images selected.")
            return
        
        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_dir, exist_ok=True)
        
        cursor = conn.cursor()
        cursor.execute("SELECT filename, image_data, duration, transition FROM current WHERE user_id = %s ORDER BY id",(session['id'],))
        images = cursor.fetchall()
        cursor.close()
        
        final_clips = []
        max_width = 1280
        max_height = 720
        
        for image_data in images:
            filename = image_data[0]
            if filename in selected_images:
                cursor = conn.cursor()
                cursor.execute('UPDATE current SET transition = %s WHERE filename = %s AND user_id = %s',
                               (transition, filename,session['id']))
                conn.commit()
                cursor.close()
                
        cursor = conn.cursor()
        cursor.execute("SELECT filename, image_data, duration, transition FROM current WHERE user_id = %s ORDER BY id",(session['id'],))
        images = cursor.fetchall()
        cursor.close()
        
        for image_data in images:
            curr_transition = image_data[3]
            filename = image_data[0]
            d = image_data[2]
            # if d =="" :
            #     d=2 
            # else :
            #     print()  
            d=int(d)
            
            clip_duration = d  # Convert duration to integer
            image_array = np.frombuffer(image_data[1], dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame_rgb.shape
            
            if width != max_width or height != max_height:
                scale_factor = min(max_width / width, max_height / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                resized_frame = cv2.resize(frame_rgb, (new_width, new_height))
                offset_x = (max_width - new_width) // 2
                offset_y = (max_height - new_height) // 2
                background = Image.new('RGB', (max_width, max_height), (203, 215, 223))
                background.paste(Image.fromarray(resized_frame), (offset_x, offset_y))
                resized_frame_with_bg = np.array(background)
                img_clip = ImageClip(resized_frame_with_bg, duration=clip_duration)
            else:
                img_clip = ImageClip(frame_rgb, duration=clip_duration)
            
            # Apply transitions based on the provided transition type
            print(curr_transition)
            print(type(curr_transition))
            if curr_transition == "fade-in":
                fadein_duration = 1
                img_clip = img_clip.fadein(fadein_duration)
            elif curr_transition == "fade-out":
                fadeout_duration = 1
                img_clip = img_clip.fadeout(fadeout_duration)
            elif curr_transition == "crossin":
                crossfade_duration = 1
                img_clip = img_clip.crossfadein(crossfade_duration)
            elif curr_transition == "crossout":
                crossfade_duration = 1
                img_clip = img_clip.fadeout(crossfade_duration)
            elif curr_transition == "fade-in-out":
                fadein_duration = 0.5
                fadeout_duration = 0.5
                img_clip = img_clip.fadein(fadein_duration).fadeout(fadeout_duration)
            elif curr_transition == "crossinout":
                crossfade_duration = 0.5
                img_clip = img_clip.fadein(crossfade_duration).fadeout(crossfade_duration)
            elif curr_transition == "none":
                pass
            # else:
            #     img_clip = ImageClip(frame_rgb, duration=clip_duration)

            final_clips.append(img_clip)

        output_video = os.path.join(upload_dir, "output_video.mp4")
        final_concatenated_clip = concatenate_videoclips(final_clips, method="compose")
        final_concatenated_clip.write_videofile(output_video, codec='libx264', fps=24)

        print("Video generated successfully:", output_video)
        
    except Exception as e:
        print("An error occurred:", e)



def multiple_audio(selected_Music, selected_duration):
    if selected_duration == "":
        selected_duration = 0
        selected_Music = []
    selected_duration = int(selected_duration)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration) AS total_duration FROM current WHERE user_id = %s",(session['id'],))
    images_temp = cursor.fetchone()
    cursor.close()
    images_duration = images_temp[0]
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration) AS total_duration FROM audio WHERE user_id = %s",(session['id'],))
    audio_temp = cursor.fetchone()
    cursor.close()
    audio_duration = audio_temp[0]
    if audio_duration is not None:
        audio_duration = int(audio_duration)
    else:
        audio_duration = 0
    images_duration = int(images_duration)
    print(audio_duration)
    print(images_duration)
    if images_duration == audio_duration and selected_duration != 0:
        cursor = conn.cursor()
        cursor.execute('TRUNCATE TABLE audio')
        cursor = conn.cursor()
        cursor.close()
    curr_time = 0
    total_time = images_duration
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audio ")
    audio_file = cursor.fetchall()
    cursor.close()
    for audio in audio_file:
        duration = audio[2]
        curr_time += int(duration)
    for audio in selected_Music:
        if total_time - curr_time > 0:
            print(audio)
            if total_time - curr_time > selected_duration:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO audio (user_id, audio, duration) VALUES (%s, %s, %s)',
                       (session['id'], audio, selected_duration,))
                conn.commit()
                cursor.close()
                curr_time += selected_duration
            else:
                duration = total_time - curr_time
                cursor = conn.cursor()
                cursor.execute('INSERT INTO audio (user_id, audio, duration) VALUES (%s, %s, %s)',
                       (session['id'],audio, duration,))
                conn.commit()
                cursor.close()
                curr_time = total_time
                break
        else:
            break
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    video_path = os.path.join(upload_dir, "output_video.mp4")
    audio_clips = []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audio ")
    audio_file = cursor.fetchall()
    cursor.close()
    for audio in audio_file:
        selected_music = audio[1]
        duration = audio[2]
        cursor = conn.cursor()
        cursor.execute('SELECT audio_data FROM music WHERE filename = %s', (f'{selected_music}.mp3',))
        audio_data = cursor.fetchone()
        cursor.close()
        audio_bytes = audio_data[0]
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        audio_clip = AudioFileClip(temp_file_path)
        if audio_clip.duration < duration:
            audio_clip = audio_clip.loop(duration=duration)
        elif audio_clip.duration > duration:
            audio_clip = audio_clip.subclip(0, duration)
        audio_clips.append(audio_clip)
        print(selected_music,duration)
        os.unlink(temp_file_path)
    if audio_clips != []: 
        if total_time - curr_time > 0:
            duration = total_time - curr_time
            cursor = conn.cursor()
            cursor.execute('SELECT audio_data FROM music WHERE filename = %s', ('silence.mp3',))
            audio_data = cursor.fetchone()
            cursor.close()
            audio_bytes = audio_data[0]
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            audio_clip = AudioFileClip(temp_file_path)
            if audio_clip.duration < duration:
                audio_clip = audio_clip.loop(duration=duration)
            elif audio_clip.duration > duration:
                audio_clip = audio_clip.subclip(0, duration)
            audio_clips.append(audio_clip)
            os.unlink(temp_file_path)
        final_audio = concatenate_audioclips(audio_clips)

        video_clip = VideoFileClip(video_path)

        video_clip = video_clip.set_audio(final_audio)
        if os.path.exists(video_path):
            os.remove(video_path)

        video_clip.write_videofile(video_path, codec='libx264', audio_codec='aac')
    input_filepath = os.path.join(upload_dir, 'output_video.mp4')
    video_path = os.path.join(app.static_folder, 'new_output_video.mp4')
    original_video = VideoFileClip(input_filepath)
    if current == 1280:
        new_resolution = (1280,720)
    if current == 1920:
        new_resolution = (1920,1080)
    if current == 480:
        new_resolution = (480,360)
    resized_video = original_video.resize(new_resolution)
    resized_video.write_videofile(video_path)
    return jsonify({'video_path': '/static/new_output_video.mp4'})
    
app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = '880248'
app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net' 
app.config['MYSQL_USER'] = 'sql6689061'       
app.config['MYSQL_PASSWORD'] = 'VdGbTa5KDU'  
app.config['MYSQL_DB'] = 'sql6689061'

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

mysql = MySQL(app)

@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kaptaan WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and verify_password(user[5],password):
            jwt_token = create_jwt_token(user[1], user[3], user[2], user[4], user[0])
            session['jwt_token'] = jwt_token
            session['username'] = user[3]
            session['email'] = user[2]
            session['name'] = user[1]
            session['id'] = user[0]
            message = 'Logged in successfully!'
            cursor.close()
            return render_template('home2.html',  username=session['username'], email=session['email'], name=session['name'])
        else:
            message = 'Please enter correct username / password!'
            cursor.close()
            return render_template('login.html', message=message,)
    return render_template('login.html')

@app.route('/home2')
def home2():
    cursor = conn.cursor()
    cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1))
    conn.commit()
    cursor.close()
    return render_template('home2.html', username=session['username'], email=session['email'], name=session['name'])

@app.route('/duration', methods=['GET', 'POST'])
def duration():
    selected_images = request.json.get('selectedImages',[])
    selected_music = request.json.get('selectedMusic',[])
    selected_duration = request.json['duration']
    transition = request.json['transition']
    change_duration(selected_images,selected_duration,transition) 
    transitions(selected_images,transition)
    multiple_audio(selected_music,selected_duration)
    return jsonify({'video_path': '/static/new_output_video.mp4'})

@app.route('/addpics', methods=['GET', 'POST'])
def addpics():
    cursor = conn.cursor()
    cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1))
    conn.commit()
    cursor.close()
    if request.method == 'POST':
        time.sleep(0.5)
        files = request.files.getlist('imageInput')
        print(files)
        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        for idx, file in enumerate(files):
            if file.filename=='':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM picture WHERE filename = %s AND user_id = %s', (filename, session['id'],))
            user = cursor.fetchone() 
            cursor.close()
            if not user:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file.read())
                # file.save(filepath) 
                filesize = os.path.getsize(filepath)
                filetype = file.mimetype
                temp_file_path = temp_file.name
                with open(temp_file_path, 'rb') as f:
                    image_data = f.read()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO picture (user_id, filename, filepath, filesize, filetype, image_file) VALUES (%s, %s, %s, %s, %s, %s)',(session['id'], filename, filepath, filesize, filetype, image_data,))
                conn.commit()
                cursor.close()
                os.unlink(temp_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM picture WHERE user_id = %s", (session['id'],))
        images = cursor.fetchall()
        cursor.close()
        return redirect(url_for('photos'))
    else:
        return render_template('addpics.html')
    
@app.route('/resize_video', methods=['POST'])
def resize_video():
    
        desired_resolution = request.json.get('selectedResolution')
        print("Received resolution:", desired_resolution) 
        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        input_filepath = os.path.join(upload_dir, 'output_video.mp4')
        video_path = os.path.join(app.static_folder, 'new_output_video.mp4')
        original_video = VideoFileClip(input_filepath)
        resolution_options = {
            'high': (1920, 1080),
            'medium': (1280, 720),
            'low': (480, 360),
            'none': original_video.size
        }
        new_resolution = (1920,1080)
        print(desired_resolution)
        if desired_resolution == "high":
            current = 1920
            new_resolution = (1920,1080)
        if desired_resolution == "medium":
            current = 1280
            new_resolution = (1280,720)
        if desired_resolution == "low":
            current = 480
            new_resolution = (480,360)
        # new_resolution = resolution_options.get(desired_resolution)
        resized_video = original_video.resize(new_resolution)
        resized_video.write_videofile(video_path)
        # time.sleep(2)
        return jsonify({'video_path': '/static/new_output_video.mp4'})

@app.route('/videoview', methods=['GET', 'POST'])
def videoview():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM picture WHERE user_id = %s AND video = %s', (session['id'],1))
    image_data = cursor.fetchall()
    cursor.close()
    images = []
    for row in image_data:
        filename = row[2]
        image_file = row[6]
        filetype = row[5]
        encoded_image = base64.b64encode(image_file).decode('utf-8')
        images.append({'filename': filename, 'encoded_image': encoded_image, 'filetype': filetype})
    return render_template('videoview.html', username=session['username'], email=session['email'], name=session['name'], images = images)
    
@app.route('/photos', methods=['GET','POST'])
def photos():
    if request.method == 'POST':
        time.sleep(0.5)
        selected_images = request.form.getlist('selectedImages[]')
        cursor = conn.cursor() 
        cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1,))
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        for image_filename in selected_images:
            # time.sleep(0.1)
            cursor.execute('UPDATE picture SET video = %s WHERE filename = %s AND user_id = %s' , (1,image_filename,session['id'],))
            conn.commit()
        cursor.close()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM picture WHERE user_id = %s AND video = %s', (session['id'],1))
        image_data = cursor.fetchall()
        
        cursor = conn.cursor()
        cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1))
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM current WHERE user_id = %s',(session['id'],))
        cursor = conn.cursor()
        cursor.close()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM audio WHERE user_id = %s',(session['id'],))
        cursor = conn.cursor()
        cursor.close()
        print(session['id'])
        for row in image_data:
            id = row[0]
            filename = row[2]
            image_file = row[6]
            filetype = row[5]
            print(filename)
            encoded_image = base64.b64encode(image_file).decode('utf-8')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO current (user_id, id, filename, image_data, duration, transition) VALUES (%s, %s, %s, %s, %s, %s)',
                       (session['id'],id,filename, image_file, 2, None,))
            conn.commit()
            cursor.close()            
            images.append({'filename': filename, 'encoded_image': encoded_image, 'filetype': filetype})
        images_to_video(selected_images) 
        return render_template('videoview.html', username=session['username'], email=session['email'], name=session['name'], images = images)
    cursor = conn.cursor()
    cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1))
    conn.commit()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute("SELECT filename,image_file,filetype FROM picture WHERE user_id = %s", (session['id'],))
    image_data = cursor.fetchall()
    cursor.close()  
    images = []
    for row in image_data:
        filename = row[0]
        image_file = row[1]
        filetype = row[2]
        encoded_image = base64.b64encode(image_file).decode('utf-8')
        images.append({'filename': filename, 'encoded_image': encoded_image, 'filetype': filetype})
    
    return render_template('photos.html', images=images)

@app.route('/delete')
def delete():
    cursor = conn.cursor()
    cursor.execute('TRUNCATE TABLE audio')
    conn.commit()
    cursor.close()

@app.route('/account')
def account():
    cursor = conn.cursor()
    cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1,))
    conn.commit()
    cursor.close()
    return render_template('account.html', username=session['username'], email=session['email'], name=session['name'])

@app.route('/admin', methods=['GET','POST'])
def admin():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kaptaan')
    account = cursor.fetchall()
    for user in account:
        print(user.id)
    cursor.close()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM picture GROUP BY user_id ORDER BY user_id')
    number = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', users = account)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'username' in request.form and 'favourite_sport' in request.form:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        favourite_sport = request.form['favourite_sport']
        hashed_password = hash_password(password)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kaptaan WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
            return render_template('signup.html', message=message)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
            return render_template('signup.html', message=message)
        elif not username or not password or not email or not name or not favourite_sport:
            message = 'Please fill out the form !'
            return render_template('signup.html', message=message)
        else:
            cursor.execute('INSERT INTO kaptaan (name, email, username, favourite_sport, password) VALUES (%s, %s, %s, %s, %s)',
                       (name, email, username, favourite_sport, hashed_password,))
            conn.commit()
            cursor.close()
            message = 'You have successfully registered !'
            return render_template('login.html', message=message)
    elif request.method == 'POST':
        message = 'Please fill out the form !'
        cursor.close()
        return render_template('signup.html',message=message)
    return render_template('signup.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        if "admin" in username and "admin" in password:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) AS total_users FROM kaptaan')
            total_users = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) AS total_users FROM picture')
            total_images = cursor.fetchone()[0]
            cursor.execute('SELECT k.id, k.username, k.email, COUNT(k.id) AS log, COUNT(p.user_id) AS count FROM kaptaan k LEFT JOIN picture p ON k.id = p.user_id GROUP BY k.id')
            account = cursor.fetchall()
            cursor.close()
            return render_template('admin.html', users = account,  total = total_users, images = total_images)
        else:
            message = 'You are not admin'
            return render_template('admin_login.html', message=message)
    return render_template('admin_login.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'favourite_sport' in request.form and 'password' in request.form:
        username = request.form['username']
        favourite_sport = request.form['favourite_sport']
        password = request.form['password']
        hashed_password = hash_password(password)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kaptaan WHERE username = %s AND favourite_sport = %s', (username, favourite_sport,))
        user = cursor.fetchone()
        if user:
            cursor.execute('UPDATE kaptaan SET password = %s WHERE username = %s',
                       (hashed_password, username,))
            conn.commit()
            message = 'Password changed successfully!'
            cursor.close()
            return render_template('login.html', message=message)
        else:
            message = 'Please enter correct username / favourite_sport!'
            cursor.close()
            return render_template('forgot.html', message=message)
    return render_template('forgot.html')


@app.route('/logout')
def logout():
    cursor = conn.cursor()
    cursor.execute('UPDATE picture SET video = %s WHERE video = %s' , (0,1))
    conn.commit()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM current WHERE user_id = %s',(session['id'],))
    cursor = conn.cursor()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM audio WHERE user_id = %s',(session['id'],))
    cursor = conn.cursor()
    cursor.close()
    session.pop('username', None)
    session.pop('name', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('id', None)
    return render_template('home.html')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'id' not in session:
        return redirect(url_for('login')) 

    cursor = conn.cursor()
    cursor.execute("DELETE FROM picture WHERE user_id = %s", (session['id'],))
    conn.commit()
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("DELETE FROM kaptaan WHERE id = %s", (session['id'],))
    conn.commit()
    cursor.close()

    return redirect(url_for('logout')) 
if __name__ == "__main__":
    app.run(debug=True)
