import requests;
import csv;
import tkinter as tk
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

url = 'https://store.steampowered.com/search/?filter=topsellers'     #ßcraping for the top 10 best selling games on steam
print('Getting the top 10 games from Steam...')
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
gamesRows = soup.find_all('a', class_='search_result_row', limit=10)

games = []

lemmatizer = WordNetLemmatizer()

for game in gamesRows:    #scraping for the review section of steam
    title = game.find('span', class_='title').getText()

    gameURL = game['href']
    gameID = game['data-ds-appid']

    response = requests.get('https://store.steampowered.com/appreviews/'+gameID+'?json=1')
    data = response.json()

    gameReviews = []
    gameReviewsText = ''
    print(f"Processing reviews for game: {title}...")

    for review in data['reviews']:    #for loop for tokenization and lemitization
        gameReviewsText += review['review']
        tokens = word_tokenize(review['review'])   
        lemmas = [lemmatizer.lemmatize(token) for token in tokens]
        lemmatizedReview = ' '.join(lemmas)
        reviewSentiment = TextBlob(lemmatizedReview).sentiment

        sentimentText = ''
        if reviewSentiment.polarity == 0 : 
            sentimentText = 'neutral'
        elif reviewSentiment.polarity > 0 :             #Sentiment Analysis
            sentimentText = 'positive'
        else: sentimentText = 'negative'


        gameReview = { 'text': review['review'], 'sentiment' : sentimentText, 'score': reviewSentiment.polarity }
        gameReviews.append(gameReview)

    gameItem = { 'title' : title, 'reviews' : gameReviews }
    games.append(gameItem)

window = tk.Tk()
window.title('Top 10 Steam Game Reviews')     #this code is for creating a gui
listbox = tk.Listbox(window)
listbox.pack()
filename = 'gameReviews.csv'

with open(filename, 'w', newline='') as file:     #here i am creating a csv file to store all the reviews in it.
    writer = csv.DictWriter(file, fieldnames=['Game Name', 'Review', 'Sentiment', 'Sentiment Score'])
    writer.writeheader()
    for game in games:
        for review in game['reviews']: 
            writer.writerow({'Game Name': game['title'], 'Review' : review['text'], 'Sentiment' : review['sentiment'], 'Sentiment Score' : review['score']})
            row = [game['title'], review['text'], review['sentiment'], review['score']]
            listbox.insert(tk.END, row)


window.minsize(600, 400)
window.maxsize(800, 600)

window.mainloop()

print(f"CSV file {filename} has been generated and window loaded.")
