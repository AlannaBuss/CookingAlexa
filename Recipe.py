import nltk

class Recipe(object):
   
   def __init__(self, json):
      self.title = json['Title']
      self.recipeID = json['RecipeID']
      self.ingredients = json['Ingredients']

   def getIngredient(specified_ingredient):
      '''Returns the dictionary of the ingredient or None if not found'''
      for ingredient in self.ingredients:
         if ingredient['Name'].lower() == specified_ingredient.lower():
            return ingredient
      return None

   def getSimilarIngredients(specified_ingredient):
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
            distance = nltk.metrics.distance.edit_distance(name, specified_ingredient)                  
            distance_list.append((distance, ingredient))

         distance_list = sorted(distance_list, key = lambda x : x[0])

         similar_ingredients.extend([ing[1] for ing in distance_list[:2]])

      return similar_ingredients
