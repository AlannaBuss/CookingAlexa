from flask import Flask
from flask_ask import Ask, statement, question, session
from collections import namedtuple
import requests
import time
import unidecode
import logging
import sys


app = Flask(__name__)
ask = Ask(app, "/cookingalexa")

searchResults = ''
recipeList = ''
recipeIndex = 0
recipe = ''
recipeDetails = ''
ingredientNames = ''

def getRecipeJson(searchTerm): 
    global searchResults
    global recipeList
    global recipe

    url = "http://api2.bigoven.com/recipes?pg=1&rpp=25&title_kw=" + searchTerm + "&api_key=qjYrfW6vcrkd97lI2NHMeMhWag45oaX7"
    
    r = requests.get(url)
    searchResults = r.json()

    recipeList = searchResults['Results']
    recipe = recipeList[0]

def nextRecipe(): 
    global recipeIndex
    global recipe
    global recipeList

    recipeIndex += 1
    recipe = recipeList[recipeIndex]

def getDetailsJson():
    global recipeDetails
    global recipe

    url = "http://api2.bigoven.com/recipe/" + str(recipe['RecipeID']) + "?api_key=qjYrfW6vcrkd97lI2NHMeMhWag45oaX7"

    r = requests.get(url)
    recipieDetails = r.json()

@app.route('/')
def homepage():
    welcome_message = 'I am Cooking Alexa! What kind of food would you like to make?'
    return question(welcome_message)

@ask.launch
def start_skill():
    welcome_message = 'I am Cooking Alexa! What kind of food would you like to make?'
    return question(welcome_message)

@ask.intent("SearchIntent", convert={'searchTerm': 'var'})
def search(searchTerm):
    getRecipeJson(searchTerm)
    return question("Found %i results for %s. The first result is a recipe for %s with %.1f stars. Would you like to use this recipe?" % (searchResults['ResultCount'], searchTerm, recipe['Title'], recipe['StarRating']))

@ask.intent("YesIntent")
def share_headlines():
    getDetailsJson()
    global recipeDetails

    return question('%s' % recipeDetails['Instructions'])

@ask.intent("NoIntent")
def no_intent():
    global searchTerm
    global recipe

    nextRecipe()
    return question('The next result is a recipe for %s with %.1f stars. Would you like to use this recipe?' % (recipe['Title'], recipe['StarRating']))

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
