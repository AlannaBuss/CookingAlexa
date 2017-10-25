import nltk
from nltk.metrics import edit_distance

# Documentation for the big oven API json 
# http://api2.bigoven.com/web/documentation/recipes

class Recipe(object):
   
   def __init__(self, json):
      self.title = json['Title']
      self.recipeID = json['RecipeID']
      self.ingredients = json['Ingredients']
      self.instructions = json['Instructions']
      self.state = 'None'

   def IngredientAmount(self, specified_ingredient):
      self.state = 'ingredient'
      ingredient = self.getIngredient(specified_ingredient)
      if ingredient != None:
         self.state = 'None'
         return "Yes you need that ingredient"
      else:
         self.sim_ingredients = self.getSimilarIngredients(specified_ingredient) 
         self.sim_ingr_index = 0
         ingred_name = self.sim_ingredients[self.sim_ingr_index]["Name"]
         self.sim_ingr_index += 1
         response = "Did you mean " + ingred_name + "?"
         return response

   def yes(self):
      if self.state == 'ingredient':
         self.state = 'None'
         return "Yes you need that ingredient"
      else:
         return "I'm not sure what you mean."


   def no(self):
      if self.state == 'ingredient':
         if self.sim_ingr_index < len(self.sim_ingredients):
            ingred_name = self.sim_ingredients[self.sim_ingr_index]['Name']
            self.sim_ingr_index += 1
            response = "Did you mean " + ingred_name + "?"
            return response
         else:
            self.state = 'None'
            return "No ingredients similar to the specified ingredient were found."
      else:
         return "I am not sure what you mean."

   def getIngredient(self, specified_ingredient):
      '''Returns the dictionary of the ingredient or None if not found'''
      for ingredient in self.ingredients:
         if ingredient['Name'].lower() == specified_ingredient.lower():
            return ingredient
      return None

   def getSimilarIngredients(self, specified_ingredient):
      '''Returns a list of ingredients with similar names to the specified ingredient.'''
      similar_ingredients = []
      specified_ingredient = specified_ingredient.lower()
      for ingredient in self.ingredients:
         name = ingredient['Name'].lower()
         if specified_ingredient in name:
            similar_ingredients.append(ingredient)

      if len(similar_ingredients) == 0:
         distance_list = []
         for ingredient in self.ingredients:
            name = ingredient['Name'].lower()
            distance = edit_distance(name, specified_ingredient)
            print("Specified {} dist to {} is {}".format(specified_ingredient, name, distance))
            distance_list.append((distance, ingredient))

         distance_list = sorted(distance_list, key = lambda x : x[0])

         similar_ingredients.extend([ing[1] for ing in distance_list[:2]])

      return similar_ingredients
