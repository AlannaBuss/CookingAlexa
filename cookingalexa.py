from flask import Flask
from enum import Enum
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

class State(Enum):
    INIT = 1
    SEARCHING = 2
    SELECTED = 3

currentState = State.INIT

recipeList = None
recipeIndex = 0
recipeInformation = None

def setRecipeInformation():
    global recipeInformation

    recipe = recipeList[recipeIndex]
    url = "http://www.cookingalexa.com/api/v1.0/recipes/" + str(recipe['RecipeID'])
    recipeInformation = Recipe(requests.get(url).json())

@app.route('/')
def homepage():
    welcome_message = 'I am Cooking Alexa! What kind of food would you like to make?'
    return question(welcome_message)

@ask.launch
def start_skill():
    welcome_message = 'I am Cooking Alexa! What kind of food would you like to make?'
    return question(welcome_message)

def getRecipeHeader():
    recipe = recipeList[recipeIndex]
    if recipeIndex == 0:
        index = "first"
    else:
        index = "next"
    return ("The " + index + " recipe is a recipe for  %s and has %.1f stars. Would you like to use this recipe?") % (recipe['Title'], recipe['StarRating'])


@ask.intent("SearchIntent", convert={'searchTerm': 'var'})
def search(searchTerm):
    global currentState
    global recipeList

    currentState = State.SEARCHING
    try:
        url = "http://www.cookingalexa.com/api/v1.0/recipes?search_term=" + searchTerm
        results = requests.get(url).json()
        recipeList = results['Results']

        numResults = "Found " + str(results['ResultCount']) + " results for " + searchTerm
        recipeInformation = getRecipeHeader()
        return question(numResults + recipeInformation)
    except Exception:
        return statement("We do not have a recipe for that yet. ")
    

@ask.intent("YesIntent")
def yes_intent():
    global currentState
    global recipeInformation
    
    if recipeInformation == None:
        if currentState is State.INIT:
            return question('I am not sure what you mean.')
        elif currentState is State.SEARCHING:
            setRecipeInformation()
            currentState = State.SELECTED
            return question(recipeInformation.getCurrentStep())
        else:
            pass
    else:
        return question (recipeInformation.yes())

@ask.intent("NoIntent")
def no_intent():
    global recipeIndex
    global recipeInformation

    if recipeInformation == None:
        if currentState is State.INIT:
            return question('I am not sure what you mean.')
        else:
            recipeIndex += 1
            return question(getRecipeHeader())
    else:
        return question (recipeInformation.no())

@ask.intent("IngredientAmountIntent", convert={'ingredient': 'var'})
def ingredient_amount(ingredient):
   
    if recipeInformation == None:
        return question ('No recipe selected.')
    
    return question(recipeInformation.IngredientAmount(ingredient))

@ask.intent("MultiplyServingsIntent", convert={'factor': 'var'})
def multiply_servings(factor):
    global recipeInformation
    print('current state: ' + str(currentState.value))
    if currentState == State.SELECTED:
        recipeInformation.multiply_servings(factor)
        return statement('Recipe multiplied by ' + factor)
    else:
        return question('I am not sure what you mean.')

@ask.intent("NextStepIntent")
def next_step():
    global recipeInformation

    if recipeInformation == None:
        return question('No recipe selected.')

    return question(recipeInformation.getNextStep())

@ask.intent("PreviousStepIntent")
def previous_step():
    global recipeInformation

    if recipeInformation == None:
        return question('No recipe selected.')

    return question(recipeInformation.getPreviousStep())

@ask.intent("RepeatStepIntent")
def repeat_step():
    global recipeInformation

    if recipeInformation == None:
        return question('No recipe selected.')

    return question(recipeInformation.getCurrentStep())

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
