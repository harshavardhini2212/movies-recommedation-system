import flask
import csv
from flask import Flask, render_template, request
import difflib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

app = flask.Flask(__name__, template_folder='templates')
movies_data = pd.read_csv('movies.csv')
all_titles = movies_data['title'].tolist()
selected_features = ['genres','keywords','tagline','cast','director']
for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')
combined_features = movies_data['genres']+' '+movies_data['keywords']+' '+movies_data['tagline']+' '+movies_data['cast']+' '+movies_data['director']
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
similarity = cosine_similarity(feature_vectors)

def get_recommendations(title):
    l=[]
    movie_name=str(title)
    list_of_all_titles = movies_data['title'].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
    close_match = find_close_match[0] 
    index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True)
    # print('Movies suggested for you : \n')
    i = 1
    names = []
    dates = []
    ratings = []
    overview=[]
    types=[]
    mid=[]
    for movie in sorted_similar_movies:
        index = movie[0]
        tit = movies_data[movies_data.index==index]['title'].values[0]
        m_id=movies_data[movies_data.index==index]['id'].values[0]
        m_ov=movies_data[movies_data.index==index]['overview'].values[0]
        m_time=movies_data[movies_data.index==index]['runtime'].values[0]
        m_rat=movies_data[movies_data.index==index]['vote_average'].values[0]
        if (i<=10):
            names.append(str(tit))
            overview.append(str(m_ov))
            mid.append(str(m_id))
            ratings.append(str(m_rat))
            dates.append(str(m_time)+" mins")
            i+=1
    for i in range(len(names)):
        l.append(tuple([names[i],overview[i],mid[i],ratings[i],dates[i]]))
    return tuple(l)
def get_suggestions():
    data = pd.read_csv('movies.csv')
    return list(data['title'])

app = Flask(__name__)
@app.route("/")
@app.route("/index")
def index():
    NewMovies=[]
    with open('movieR.csv','r') as csvfile:
        readCSV = csv.reader(csvfile)
        NewMovies.append(random.choice(list(readCSV)))
    m_name = NewMovies[0][0]
    m_name = m_name.title()
    
    with open('movieR.csv', 'a',newline='') as csv_file:
        fieldnames = ['Movie']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Movie': m_name})
        result_final = get_recommendations(m_name)
        names = []
        dates = []
        ratings = []
        overview=[]
        types=[]
        mid=[]
        for i in range(len(result_final)):
            names.append(result_final[i][0])
            dates.append(result_final[i][4])
            ratings.append(result_final[i][3])
            overview.append(result_final[i][1])
            mid.append(result_final[i][2])
    suggestions = get_suggestions()
    
    return render_template('index.html',suggestions=suggestions,movieid=mid,movie_overview=overview,movie_names=names,movie_date=dates,movie_ratings=ratings,search_name=m_name)

# Set up the main route
@app.route('/positive', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))

    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        if m_name not in all_titles:
            return(flask.render_template('negative.html',name=m_name))
        else:
            with open('movieR.csv', 'a',newline='') as csv_file:
                fieldnames = ['Movie']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'Movie': m_name})
            result_final = get_recommendations(m_name)
            names = []
            dates = []
            ratings = []
            overview=[]
            types=[]
            mid=[]
            for i in range(len(result_final)):
                names.append(result_final[i][0])
                dates.append(result_final[i][4])
                ratings.append(result_final[i][3])
                overview.append(result_final[i][1])
                mid.append(result_final[i][2])
               
            return flask.render_template('positive.html',movieid=mid,movie_overview=overview,movie_names=names,movie_date=dates,movie_ratings=ratings,search_name=m_name)

if __name__ == '__main__':
    app.run()
