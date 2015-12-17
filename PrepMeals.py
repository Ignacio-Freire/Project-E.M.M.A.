import random

protein = ['100g Chicken', '100g Pork Steak', '100g Meatballs', '100g Lean Beef', '100g Hamburguer']
sides = ['1c Broccoli', '1c Green Beans', '1c Brussel Sprouts', '1c Snap Peas', '1c Spinach', '1 Eggs', '1c Beans',
         '1 Eggplant']
main_seasoning = ['Garlic, Pepper', 'Green Onion', 'Cajun Pepper', 'Masala', 'Chili', 'BBQ', 'Onion BBQ',
                  'Honey Mustard']
secondary_seasonings = ['Chia Seeds', 'Sunflower Seeds', 'Quinoa Seeds', 'Almonds']

recipes = []
tobuy = []


class MealPrep:

    @staticmethod
    def create_recipes(cant):

        for i in range(cant):

            main = random.sample(protein, 1)
            side_one = random.sample(sides, 1)
            side_two = random.sample(sides, 1)
            main_season = random.sample(main_seasoning, 1)
            sec_season = random.sample(secondary_seasonings, 1)
            recipe_num = ['-Recipe number {}'.format(i+1)]

            recipes.extend(recipe_num + main + side_one + side_two + main_season + sec_season)

        return recipes

    @staticmethod
    def grocery_list(recipes_list):

        tobuy.append('Butcher:')
        for _i in protein:
            cant = recipes_list.count(_i)

            if cant != 0:
                tobuy.append('        {}{}'.format(cant, _i[1::]))

        tobuy.append('Greenstore:')
        for _i in sides:
            cant = recipes_list.count(_i)

            if cant != 0:
                tobuy.append('        {}{}'.format(cant, _i[1::]))

        tobuy.append('Seasonings:')
        for _i in main_seasoning:
            cant = recipes_list.count(_i)

            if cant != 0:
                tobuy.append('        {}'.format(_i))

        for _i in secondary_seasonings:
            cant = recipes_list.count(_i)

            if cant != 0:
                tobuy.append('        {}'.format(_i))

        return tobuy
