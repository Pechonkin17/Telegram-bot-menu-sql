from app.data.database import create_connection



def get_foods():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM bot_data')
    foods = cursor.fetchall()
    cursor.close()
    connection.close()

    food_dicts = []
    for food in foods:
        food_dict = {
            'id': food[0],
            'name': food[1],
            'ingredients': food[2],
            'photo_url': food[3],
            'rating': food[4]
        }
        food_dicts.append(food_dict)
    return food_dicts



def get_food_by_name(name):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM bot_data WHERE name = %s"
    cursor.execute(query, (name,))
    food = cursor.fetchone()
    cursor.close()
    connection.close()

    if food is None:
        return {}
    else:
        food_dict = {
            'id': food[0],
            'name': food[1],
            'ingredients': food[2],
            'photo_url': food[3],
            'rating': food[4]
        }
        return food_dict



def create_food(food: dict):
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO bot_data (name, ingredients, photo_url, rating)
    VALUES (%s, %s, %s, %s)
    """
    name = food.get('name')
    ingredients = food.get('ingredients')
    photo_url = food.get('photo_url')
    rating = food.get('rating')

    cursor.execute(query, (name, ingredients, photo_url, rating))
    connection.commit()
    cursor.close()
    connection.close()



def delete_food(name):
    if not find_food(name):
        return False

    connection = create_connection()
    cursor = connection.cursor()
    query = "DELETE FROM bot_data WHERE name = %s"
    cursor.execute(query, (name,))
    connection.commit()
    cursor.close()
    connection.close()
    return True



def update_food(name, updated_food):
    connection = create_connection()
    cursor = connection.cursor()
    query = """
        UPDATE bot_data 
        SET name = %s, ingredients = %s, photo_url = %s, rating = %s 
        WHERE name = %s
        """
    cursor.execute(query, (
        updated_food.get('name'),
        updated_food.get('ingredients'),
        updated_food.get('photo_url'),
        updated_food.get('rating'),
        name
    ))
    connection.commit()
    cursor.close()
    connection.close()



def find_food(name):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM bot_data WHERE name = %s"
    cursor.execute(query, (name,))
    food = cursor.fetchone()
    cursor.close()
    connection.close()

    if food is None:
        return None
    else:
        food_dict = {
            'name': food[1],
            'ingredients': food[2],
            'photo_url': food[3],
            'rating': food[4]
        }
        return food_dict



def find_foods_by_partial_name(name):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM bot_data WHERE name LIKE %s"
    cursor.execute(query, ('%' + name + '%',))
    foods = cursor.fetchall()
    cursor.close()
    connection.close()

    food_dicts = []
    for food in foods:
        food_dict = {
            'id': food[0],
            'name': food[1],
            'ingredients': food[2],
            'photo_url': food[3],
            'rating': food[4]
        }
        food_dicts.append(food_dict)
    return food_dicts