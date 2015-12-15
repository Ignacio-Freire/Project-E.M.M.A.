import re
import random

protein = ['100g Chicken', '100g Pork Steak', '200g Meatballs', '100g Lean Beef', '200g Hamburguer']
sides = ['1c Broccoli', '1c Green Beans', '1c Brussel Sprouts', '1c Snap Peas', '2c Spinach', '1 Eggs', '1c Beans',
         '1 Eggplant', '1 Onion']
main_seasoning = ['Garlic, Pepper', 'Cajun Pepper', 'Masala', 'Chili', 'BBQ', 'Onion BBQ', 'Honey Mustard']
secondary_seasonings = ['Chia Seeds', 'Sunflower Seeds', 'Quinoa Seeds', 'Almonds']

mls = re.compile(r'<meals (?P<meals>\d{1,2})>', re.I | re.M)

text = '<meals 12>'

meals_qty = mls.findall(text)

for i in range(int(meals_qty[0])):
    main = random.sample(protein, 1)
    side = random.sample(sides, 2)
    main_season = random.sample(main_seasoning, 1)
    sec_season = random.sample(secondary_seasonings, 1)

    print('-Recipe number {}-\n{}\n{}, {}\n{}, {} and Salt\n'.format(i+1, main[0], side[0], side[1], main_season[0],
                                                                     sec_season[0]))
