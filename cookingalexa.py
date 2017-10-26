from flask import Flask
from flask_ask import Ask, statement, question, session
from collections import namedtuple
import requests
import time
import unidecode
import logging
import sys
from Recipe import Recipe


app = Flask(__name__)
ask = Ask(app, "/cookingalexa")

searchDone = False
searchResults = None
recipeList = None
recipeIndex = 0
recipe = None
recipeDetails = None
recipeInformation = None

def getRecipeJson(searchTerm): 
    global searchResults
    global recipeList
    global recipe

    url = "http://api2.bigoven.com/recipes?pg=1&rpp=25&title_kw=" + searchTerm + "&api_key=qjYrfW6vcrkd97lI2NHMeMhWag45oaX7"
    
    r = requests.get(url)
    searchResults = r.json()

    recipeList = searchResults['Results']
    recipe = recipeList[recipeIndex]

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
    recipeDetails = r.json()

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
    searchDone = True
    recipeInformation = None
    getRecipeJson(searchTerm)
    return question("Found %i results for %s. The first result is a recipe for %s with %.1f stars. Would you like to use this recipe?" % (searchResults['ResultCount'], searchTerm, recipe['Title'], recipe['StarRating']))

@ask.intent("YesIntent")
def yes_intent():
    global recipeInformation
    global recipeDetails
    
    if recipeInformation == None:
        if searchDone == False:
            return question('I am not sure what you mean.')
        else:
            getDetailsJson()
            recipeInformation = Recipe(recipeDetails)
            return question('Recipe Selected.')
            #return question('%s' % recipeDetails['Instructions'])
    else:
        return question (recipeInformation.yes())

@ask.intent("NoIntent")
def no_intent():
    global searchTerm
    global recipe
    global recipeInformation

    if recipeInformation == None:
        if searchDone == False:
            return question('I am not sure what you mean.')
        else:
            nextRecipe()
            return question('The next result is a recipe for %s with %.1f stars. Would you like to use this recipe?' % (recipe['Title'], recipe['StarRating']))
    else:
        return question (recipeInformation.no())

@ask.intent("IngredientAmountIntent", convert={'ingredient': 'var'})
def ingredient_amount(ingredient):
    global recipeInformation
   
    if recipeInformation == None:
        return question ('No recipe selected.')
    
    return question(recipeInformation.IngredientAmount(ingredient))

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
