import sqlite3

# Ma'lumotlar bazasini yaratish yoki unga ulanish
conn = sqlite3.connect('movies.db')
c = conn.cursor()

# Kino jadvali
c.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        country TEXT,
        language TEXT,
        year INTEGER,
        genre TEXT,
        views INT NOT NULL DEFAULT 0
    )''')

c.execute('''
    CREATE TABLE IF NOT EXISTS movie_parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        part_number INTEGER,
        video TEXT NOT NULL,
        size REAL NOT NULL,
        FOREIGN KEY(movie_id) REFERENCES movies(id) ON DELETE CASCADE
    )''')

# Ensure new columns exist in movies table
def ensure_columns():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    # Check current columns
    c.execute("PRAGMA table_info(movies)")
    existing_columns = [col[1] for col in c.fetchall()]
    
    new_cols = [
        ("description", "TEXT"),
        ("country", "TEXT"),
        ("language", "TEXT"),
        ("year", "INTEGER"),
        ("genre", "TEXT")
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in existing_columns:
            try:
                c.execute(f"ALTER TABLE movies ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")
    
    conn.close()

ensure_columns()

# Migration: Check if movies table has older columns and migrate data to movie_parts
try:
    c.execute("SELECT video, size, id FROM movies")
    movies_data = c.fetchall()
    for v, s, mid in movies_data:
        if v and s:
            # Check if this part has already been migrated
            c.execute("SELECT id FROM movie_parts WHERE movie_id=? AND part_number=1", (mid,))
            if not c.fetchone():
                c.execute("INSERT INTO movie_parts (movie_id, part_number, video, size) VALUES (?, ?, ?, ?)", (mid, 1, v, s))
            
            # Note: We don't remove the columns from 'movies' here because SQLite 
            # support for DROP COLUMN varies. We just stop using them.
except Exception as e:
    # Older columns might not exist, which is fine.
    pass

c.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        is_true Boolen NOT NULL DEFAULT False
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS saveds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        users_id INT NOT NULL,
        movie_id INT,
        FOREIGN KEY(movie_id) REFERENCES movies(id) ON DELETE CASCADE
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS is_trues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checkbox Boolen NOT NULL default False
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS bot_admins (
        user_id INTEGER PRIMARY KEY,
        is_super BOOLEAN DEFAULT FALSE,
        can_add_movie BOOLEAN DEFAULT TRUE,
        can_del_movie BOOLEAN DEFAULT TRUE,
        can_manage_channels BOOLEAN DEFAULT TRUE,
        can_manage_ads BOOLEAN DEFAULT TRUE,
        can_send_message BOOLEAN DEFAULT TRUE,
        can_view_stats BOOLEAN DEFAULT TRUE
    )
''')

c.execute('''SELECT * FROM is_trues''')

checks = c.fetchone()

# print(checks)
if checks is None:
    c.execute('''
            INSERT INTO is_trues (checkbox) VALUES (?)
        ''', (False,))

conn.commit()
conn.close()

def insert_movie(data):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Get existing columns to avoid IntegrityError with old NOT NULL columns (size, video)
    c.execute("PRAGMA table_info(movies)")
    columns = [col[1] for col in c.fetchall()]
    
    fields = ["name", "description", "country", "language", "year", "genre"]
    placeholders = ["?", "?", "?", "?", "?", "?"]
    values = [data['name'], data.get('description'), data.get('country'), data.get('language'), data.get('year'), data.get('genre')]

    if "size" in columns:
        fields.append("size")
        placeholders.append("0")
    if "video" in columns:
        fields.append("video")
        placeholders.append("''")

    query = f"INSERT INTO movies ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
    c.execute(query, values)

    movie_id = c.lastrowid
    
    conn.commit()
    conn.close()

    return movie_id

def insert_movie_part(movie_id, part_number, video, size):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO movie_parts (movie_id, part_number, video, size) VALUES (?, ?, ?, ?)
    ''', (movie_id, part_number, video, size))
    
    conn.commit()
    conn.close()

def get_movie_parts(movie_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute("SELECT part_number, video, size FROM movie_parts WHERE movie_id=? ORDER BY part_number", (movie_id,))
    parts = c.fetchall()
    conn.close()
    return parts

def get_movie_details(movie_id):
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT * FROM movies WHERE id=?
    ''', (movie_id,))

    movie = c.fetchone()
    conn.close()

    if movie:
        return dict(movie)
    else:
        return None

# Misol uchun ma'lumot kiritish
# print(insert_movie('Film nomi', 700.2, '789456'))

# def get_movie_details(movie_id):
#     conn = sqlite3.connect('movies.db')
#     c = conn.cursor()

#     c.execute('''
#         SELECT id, name, size, video, views FROM movies WHERE id=?
#     ''', (movie_id,))

#     movie = c.fetchone()
#     conn.close()

#     if movie:
#         return {'id': movie[0], 'name': movie[1], 'size': movie[2], 'video': movie[3], 'views': movie[4]}
#     else:
#         return None

# Misol uchun detalni olish
# movie_details = get_movie_details(1)


# Qidirish funksiyasi
def search_movie(movie_name):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT id, name, size, video, views FROM movies WHERE name LIKE ?
    ''', ('%' + movie_name + '%',))

    movies = c.fetchall()
    conn.close()

    if movies:
        result = []
        for movie in movies:
            result.append({'id': movie[0], 'name': movie[1], 'size': movie[2], 'video': movie[3], 'views': movie[4]})
        return result
    else:
        return None

# Misol uchun qidirish
# movies_found = search_movie('i')
# print(search_movie('i'))
def update_movies(id, view):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Qaysi ustunlarni yangilash kerakligini aniqlash
    if view:
        c.execute(f"UPDATE movies SET views = {view} WHERE id = {id}")

    rows_affected = c.rowcount
    conn.commit()
    conn.close()
    
    if rows_affected > 0:
        return True
    else:
        return False

# print(update_movies(id=1, view=1))

def all_movie():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM movies
    ''')

    movies = c.fetchall()
    conn.close()

    if movies:
        result = []
        for movie in movies:
            result.append({'id': movie[0], 'name': movie[1], 'size': movie[2], 'video': movie[3], 'views': movie[4]})
        return result
    else:
        return None

# print(all_movie())
# movies_found = all_movie()
def delete_movies_id(id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        DELETE FROM movies WHERE id=?
    ''', (id,))

    conn.commit()
    conn.close()



# Kanal uchun ---
def insert_channel(name, link, is_true=False):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT name, link FROM channels WHERE name=? and link=?
    ''', (name, link))
    
    channel = c.fetchone()
    if channel is None:
        c.execute('''
            INSERT INTO channels (name, link, is_true) VALUES (?, ?, ?)
        ''', (name, link, is_true))

        check = True
    else:
        check = False
    
    conn.commit()
    conn.close()

    return check


# print(insert_channel('Channel', 'channel', False))
# Kanalga murojat qilib olish
def get_channel_details(channel_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT name, link, is_true FROM channels WHERE id=?
    ''', (channel_id,))

    channel = c.fetchone()
    conn.close()

    if channel:
        return {'name': channel[0], 'size': channel[1], 'is_true': channel[2]}
    else:
        return None

# a = get_channel_details(1)
# print(a)
def all_channels():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM channels
    ''')

    channels = c.fetchall()
    conn.close()

    if channels:
        result = []
        for channel in channels:
            result.append({'id': channel[0], 'name': channel[1], 'link': channel[2], 'is_true': channel[3]})
        return result
    else:
        return None

# Kanal o'chirish
def delete_channel(channel_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        DELETE FROM channels WHERE id=?
    ''', (channel_id,))

    conn.commit()
    conn.close()
    print(f"ID: {channel_id} bo'yicha kanal o'chirildi.")

# Kanal o'zgartirish
def update_channel_details(channel_id, is_true=None):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Qaysi ustunlarni yangilash kerakligini aniqlash
    if is_true is not None:
        c.execute(f"UPDATE channels SET is_true = ? WHERE id = ?", (is_true, channel_id))

    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected > 0:
        print(f"ID: {channel_id} bo'yicha kanal ma'lumotlari yangilandi.")
        return True
    else:
        print(f"ID: {channel_id} bo'yicha kanal topilmadi yoki yangilanmadi.")
        return False

# Misol uchun yangilash
# channel_id = 2
# result = update_channel_details(channel_id, is_true=True)
# print(f"Yangilash muvaffaqiyatli bo'ldimi? {result}")

# Reklama uchun
def insert_ads(name, link):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT name, link FROM ads WHERE name=?
    ''', (name,))
    
    ads = c.fetchone()
    if ads is None:
        c.execute('''
            INSERT INTO ads (name, link) VALUES (?, ?)
        ''', (name, link))

        check = True
    else:
        check = False
    
    conn.commit()
    conn.close()

    return check
# print(insert_ads('Reklama', 'reklama'))

# Reklamaga murojat qilib olish
def get_ads_details(ads_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT id, name, link FROM ads WHERE id=?
    ''', (ads_id,))

    ads = c.fetchone()
    conn.close()

    if ads:
        return {'id': ads[0], 'name': ads[1], 'link': ads[2]}
    else:
        return None
# print(get_ads_details(1))

def all_ads():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM ads
    ''')

    ads = c.fetchall()
    conn.close()

    if ads:
        result = []
        for ad in ads:
            result.append({'id': ad[0], 'name': ad[1], 'link': ad[2]})
        return result
    else:
        return None

# Reklama o'chirish
def delete_ads(ads_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        DELETE FROM ads WHERE id=?
    ''', (ads_id,))

    conn.commit()
    conn.close()
    print(f"ID: {ads_id} bo'yicha kanal o'chirildi.")
# delete_ads(1)

# Saved uchun
def insert_saved(movie_id, users_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT movie_id, users_id FROM saveds WHERE users_id=? and movie_id=?
    ''', (users_id, movie_id))
    
    saved = c.fetchone()
    if saved is None:
        c.execute('''
            INSERT INTO saveds (movie_id, users_id) VALUES (?, ?)
        ''', (movie_id, int(users_id)))

        check = True
    else:
        check = False
    
    conn.commit()
    conn.close()

    return check
# print(insert_saved(movie_id=1, users_id=4571))

# saved user_id ga teng bolganlarga murojat qilish
def get_saveds(users_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT saveds.id, saveds.movie_id, saveds.users_id, movies.name, movies.size, movies.video, movies.views FROM saveds JOIN
               movies ON movies.id = saveds.movie_id WHERE saveds.users_id = ?
    ''', (users_id,))

    saveds = c.fetchall()
    conn.close()
    results = []
    
    if saveds:
        for saved in saveds:
            results.append({'id':saved[0], 'movie_id': saved[1], 'users_id': saved[2], 'name': saved[3], 'size': saved[4], 'video': saved[5], 'views': saved[6]})

    if results:
        return results
    else:
        return None
# print(get_saveds(4571))

def get_saveds_movies_id(users_id, movie_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT saveds.id, saveds.movie_id, saveds.users_id, movies.name, movies.size, movies.video, movies.views FROM saveds JOIN
               movies ON movies.id = saveds.movie_id WHERE saveds.users_id = ? AND saveds.movie_id = ?
    ''', (users_id, movie_id))

    saved = c.fetchone()
    conn.close()

    if saved:
        return {'id':saved[0], 'movie_id': saved[1], 'users_id': saved[2], 'name': saved[3], 'size': saved[4], 'video': saved[5], 'views': saved[6]}
    else:
        return None

def delete_saved(saved_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        DELETE FROM saveds WHERE id=?
    ''', (saved_id,))

    conn.commit()
    conn.close()
    print(f"ID: {saved_id} bo'yicha saqlangan kino o'chirildi.")

def get_checkbox():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT id, checkbox FROM is_trues WHERE id=?
    ''', (1,))

    check_true = c.fetchone()
    conn.close()

    if check_true:
        return {'id': check_true[0], 'is_true': check_true[1]}
    else:
        return None

def update_checkbox(is_true):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Qaysi ustunlarni yangilash kerakligini aniqlash
    if is_true is not None:
        c.execute(f"UPDATE is_trues SET checkbox = ? WHERE id = ?", (is_true, 1))

    conn.commit()
    conn.close()

# Admin management functions
def get_admin(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bot_admins WHERE user_id=?', (user_id,))
    admin = c.fetchone()
    conn.close()
    if admin:
        return {
            'user_id': admin[0],
            'is_super': admin[1],
            'can_add_movie': admin[2],
            'can_del_movie': admin[3],
            'can_manage_channels': admin[4],
            'can_manage_ads': admin[5],
            'can_send_message': admin[6],
            'can_view_stats': admin[7]
        }
    return None

def add_admin(user_id, is_super=False):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO bot_admins (user_id, is_super) VALUES (?, ?)', (user_id, is_super))
    conn.commit()
    conn.close()

def delete_admin(user_id):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('DELETE FROM bot_admins WHERE user_id=? AND is_super=0', (user_id,))
    conn.commit()
    conn.close()

def update_admin_permission(user_id, column, value):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute(f'UPDATE bot_admins SET {column}=? WHERE user_id=?', (value, user_id))
    conn.commit()
    conn.close()

def get_all_admins():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bot_admins')
    admins = c.fetchall()
    conn.close()
    return admins




# update_checkbox(is_true = False)
# print(get_checkbox())

