from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('PJ_VGI_v4.sqlite') # Connects directly to the SQLite file
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def home():
    sort_by = request.args.get('sort', 'id_asc')
    search_query = request.args.get('q', '').strip()

    sort_columns = {
        'game_asc': 'TRIM(Game) COLLATE NOCASE ASC',
        'game_desc': 'TRIM(Game) COLLATE NOCASE DESC',
        'sales_desc': 'CAST(Sales AS REAL) DESC',
        'developer_asc': 'TRIM(Developer) COLLATE NOCASE ASC',
        'publisher_asc': 'TRIM(Publisher) COLLATE NOCASE ASC',
        'series_asc': 'TRIM(Series) COLLATE NOCASE ASC',
        'id_asc': 'CAST(Gameid AS INTEGER) ASC'
    }

    order_clause = sort_columns.get(sort_by, 'CAST(Gameid AS INTEGER) ASC')

    conn = get_db_connection()

    if search_query:
        # Using a CAST that includes Gameid and Sales so numbers can be searched
        sql = f'''
            SELECT Gameid, Game, Sales, Series, Developer, Publisher 
            FROM Games_tbl 
            WHERE Game LIKE ? 
               OR Series LIKE ? 
               OR Developer LIKE ? 
               OR Publisher LIKE ?
               OR CAST(Gameid AS TEXT) LIKE ?
               OR CAST(Sales AS TEXT) LIKE ?
            ORDER BY {order_clause} LIMIT 175
        '''
        pattern = f'%{search_query}%'
        games = conn.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern)).fetchall()
    else:
        sql = f'SELECT Gameid, Game, Sales, Series, Developer, Publisher FROM Games_tbl ORDER BY {order_clause} LIMIT 175'
        games = conn.execute(sql).fetchall()

    conn.close()

    return render_template('index.HTML', games=games, current_sort=sort_by, search_query=search_query)


@app.route('/most-selling')
def most_selling():
    sort_by = request.args.get('sort', 'sales_desc')
    search_query = request.args.get('q', '').strip()

    sort_columns = {
        'sales_desc': 'CAST(Sales_In_Millions AS REAL) DESC',
        'title_asc': 'TRIM(Title) COLLATE NOCASE ASC',
        'title_desc': 'TRIM(Title) COLLATE NOCASE DESC',
        'developer_asc': 'TRIM(Developer) COLLATE NOCASE ASC',
        'publisher_asc': 'TRIM(Publisher) COLLATE NOCASE ASC',
        'genre_asc': 'TRIM(Genre) COLLATE NOCASE ASC'
    }

    order_clause = sort_columns.get(sort_by, 'CAST(Sales_In_Millions AS REAL) DESC')

    conn = get_db_connection()

    if search_query:
        # CAST sales to TEXT so number searches (e.g., '14', '1.0') work
        sql = f'''
            SELECT Title, Series, Sales_In_Millions, Genre, Developer, Publisher, Release_Date 
            FROM View_Top_Selling_Games 
            WHERE Title LIKE ? 
               OR Series LIKE ? 
               OR Developer LIKE ? 
               OR Publisher LIKE ? 
               OR Genre LIKE ?
               OR CAST(Sales_In_Millions AS TEXT) LIKE ?
               OR Release_Date LIKE ?
            ORDER BY {order_clause}
        '''
        pattern = f'%{search_query}%'
        games = conn.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern, pattern)).fetchall()
    else:
        sql = f'SELECT Title, Series, Sales_In_Millions, Genre, Developer, Publisher, Release_Date FROM View_Top_Selling_Games ORDER BY {order_clause}'
        games = conn.execute(sql).fetchall()

    conn.close()
    
    return render_template('most_selling.HTML', games=games, current_sort=sort_by, search_query=search_query)

@app.route('/game-genres')
def game_genres():
    sort_by = request.args.get('sort', 'id_asc')
    search_query = request.args.get('q', '').strip()

    sort_columns = {
        'id_asc': 'CAST(Gameid AS INTEGER) ASC',
        'genre_asc': 'TRIM(Genre) COLLATE NOCASE ASC',
        'genre_desc': 'TRIM(Genre) COLLATE NOCASE DESC',
        'title_asc': 'TRIM(Title) COLLATE NOCASE ASC',
        'title_desc': 'TRIM(Title) COLLATE NOCASE DESC',
    }

    order_clause = sort_columns.get(sort_by, 'TRIM(Genre) COLLATE NOCASE ASC')

    conn = get_db_connection()

    if search_query:
        # Cast Gameid to text so numeric searches (like ID numbers) work alongside text searches
        sql = f'''
            SELECT Gameid, Title, Genre 
            FROM Games_All_Genres 
            WHERE Title LIKE ? 
               OR Genre LIKE ? 
               OR CAST(Gameid AS TEXT) LIKE ?
            ORDER BY {order_clause}
        '''
        pattern = f'%{search_query}%'
        games = conn.execute(sql, (pattern, pattern, pattern)).fetchall()
    else:
        sql = f'SELECT Gameid, Title, Genre FROM Games_All_Genres ORDER BY {order_clause}'
        games = conn.execute(sql).fetchall()

    conn.close()

    return render_template('game_genres.HTML', games=games, current_sort=sort_by, search_query=search_query)

@app.route('/developed-games')
def developed_games():
    sort_by = request.args.get('sort', 'developer_asc')
    search_query = request.args.get('q', '').strip()

    # Groups and sorts strictly chronologically from Jan -> Dec across calendar years
    month_year_sort = '''
        CASE SUBSTR(Release_Date, 1, 3)
            WHEN 'Jan' THEN '01'
            WHEN 'Feb' THEN '02'
            WHEN 'Mar' THEN '03'
            WHEN 'Apr' THEN '04'
            WHEN 'May' THEN '05'
            WHEN 'Jun' THEN '06'
            WHEN 'Jul' THEN '07'
            WHEN 'Aug' THEN '08'
            WHEN 'Sep' THEN '09'
            WHEN 'Oct' THEN '10'
            WHEN 'Nov' THEN '11'
            WHEN 'Dec' THEN '12'
            ELSE '99'
        END ASC,
        CASE 
            WHEN CAST(SUBSTR(Release_Date, 5, 2) AS INTEGER) >= 80 
            THEN '19' || SUBSTR(Release_Date, 5, 2)
            ELSE '20' || SUBSTR(Release_Date, 5, 2)
        END ASC
    '''

    sort_columns = {
        'developer_asc': 'TRIM(Developer) COLLATE NOCASE ASC',
        'developer_desc': 'TRIM(Developer) COLLATE NOCASE DESC',
        'title_asc': 'TRIM(Title) COLLATE NOCASE ASC',
        'title_desc': 'TRIM(Title) COLLATE NOCASE DESC',
        'sales_desc': 'CAST(Sales_In_Millions AS REAL) DESC',
        'release_jan_dec': month_year_sort
    }

    order_clause = sort_columns.get(sort_by, 'TRIM(Developer) COLLATE NOCASE ASC')

    conn = get_db_connection()

    if search_query:
        sql = f'''
            SELECT Developer, Title, Release_Date, Sales_In_Millions 
            FROM Developed_Games 
            WHERE Developer LIKE ? 
               OR Title LIKE ? 
               OR Release_Date LIKE ? 
               OR CAST(Sales_In_Millions AS TEXT) LIKE ?
            ORDER BY {order_clause}
        '''
        pattern = f'%{search_query}%'
        games = conn.execute(sql, (pattern, pattern, pattern, pattern)).fetchall()
    else:
        sql = f'SELECT Developer, Title, Release_Date, Sales_In_Millions FROM Developed_Games ORDER BY {order_clause}'
        games = conn.execute(sql).fetchall()

    conn.close()

    return render_template('developed_games.html', games=games, current_sort=sort_by, search_query=search_query)

@app.route('/published-games')
def published_games():
    sort_by = request.args.get('sort', 'publisher_asc')
    search_query = request.args.get('q', '').strip()

    # Sorts chronologically month-by-month (Jan to Dec) across years
    month_year_sort = '''
        CASE SUBSTR(Release_Date, 1, 3)
            WHEN 'Jan' THEN '01'
            WHEN 'Feb' THEN '02'
            WHEN 'Mar' THEN '03'
            WHEN 'Apr' THEN '04'
            WHEN 'May' THEN '05'
            WHEN 'Jun' THEN '06'
            WHEN 'Jul' THEN '07'
            WHEN 'Aug' THEN '08'
            WHEN 'Sep' THEN '09'
            WHEN 'Oct' THEN '10'
            WHEN 'Nov' THEN '11'
            WHEN 'Dec' THEN '12'
            ELSE '99'
        END ASC,
        CASE 
            WHEN CAST(SUBSTR(Release_Date, 5, 2) AS INTEGER) >= 80 
            THEN '19' || SUBSTR(Release_Date, 5, 2)
            ELSE '20' || SUBSTR(Release_Date, 5, 2)
        END ASC
    '''

    sort_columns = {
        'publisher_asc': 'TRIM(Publisher) COLLATE NOCASE ASC',
        'publisher_desc': 'TRIM(Publisher) COLLATE NOCASE DESC',
        'title_asc': 'TRIM(Title) COLLATE NOCASE ASC',
        'title_desc': 'TRIM(Title) COLLATE NOCASE DESC',
        'sales_desc': 'CAST(Sales_In_Millions AS REAL) DESC',
        'release_jan_dec': month_year_sort
    }

    order_clause = sort_columns.get(sort_by, 'TRIM(Publisher) COLLATE NOCASE ASC')

    conn = get_db_connection()

    if search_query:
        sql = f'''
            SELECT Publisher, Title, Release_Date, Sales_In_Millions 
            FROM Published_Games 
            WHERE Publisher LIKE ? 
               OR Title LIKE ? 
               OR Release_Date LIKE ? 
               OR CAST(Sales_In_Millions AS TEXT) LIKE ?
            ORDER BY {order_clause}
        '''
        pattern = f'%{search_query}%'
        games = conn.execute(sql, (pattern, pattern, pattern, pattern)).fetchall()
    else:
        sql = f'SELECT Publisher, Title, Release_Date, Sales_In_Millions FROM Published_Games ORDER BY {order_clause}'
        games = conn.execute(sql).fetchall()

    conn.close()

    return render_template('published_games.html', games=games, current_sort=sort_by, search_query=search_query)

@app.route('/about')
def about():
    search_query = request.args.get('q', '').strip()
    return render_template('about.HTML', search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True)