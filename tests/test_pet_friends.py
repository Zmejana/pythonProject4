from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key(email=valid_email, password=valid_password):
    """ Проверяем, что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result

def test_post_api_pet(name='Барбос', animal_type='терьер',
                                     age='15', pet_photo='images/P1040103.jpg'):
    """Проверяем, что можно добавить питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.post_api_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_delete_api_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.post_api_pet(auth_key, "Суперт", "кот", "1", "images/cat1.jpg")
        _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_api_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Проверяем, что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_put_api_pet(name='Мурзик', animal_type='Кот', age=2):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.put_api_pet(auth_key, my_pets['pets'][0]['id'], name, animal_type, age, pet_photo='images/cat1.jpg')

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("Питомцев нет")

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_post_api_create_pet_simple(name='Барбарис', animal_type='кот',
                                     age='8'):
    """1 - Проверяем, что можно добавить питомца без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.post_api_create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_post_api_pets_set_photo(pet_photo='images/cat1.jpg'):
    """2 - Проверяем, что можно добавить фото питомца по его ID"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.post_api_pets_set_photo(auth_key, pet_id, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert 'pet_photo' in result

def test_post_api_create_pet_simple_unreal_age(name='Боря', animal_type='котенок',
                                     age=100):
    """3 - Проверяем возможность добавления питомца с нереальным возрастом"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Если возраст питомца меньше 50, то пробуем его добавить
    if age < 50:
        status, result = pf.post_api_create_pet_simple(auth_key, name, animal_type, age)

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если возраст питомца превышает 50, то выкидываем исключение с текстом о невозможноти добавления питомца
        raise Exception("Неверно указан возраст питомца")

def test_post_api_pet_empty_value_type(name='Булочка>', animal_type='',
                                     age='2', pet_photo='images/P1040103.jpg'):
    """4 - Проверяем возможность добавления питомца без указания типа животного"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Если nип животного не указан, выкидываем исключение с текстом о невозможноти добавления питомца
    if animal_type == '':
        raise Exception("Не указан тип животного")
    else:

        # Добавляем питомца и проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        status, result = pf.post_api_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
        assert result['name'] == name

def test_get_api_key_incorrect_password(email=valid_email, password='valid_password'):
    """5 - Проверяем, что запрос api ключа возвращает статус, отличный от 200 и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status != 200
    assert 'key' not in result

def test_get_api_key_incorrect_email(email='valid_email', password=valid_password):
    """6 - Проверяем, что запрос api ключа возвращает статус, отличный от 200 и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status != 200
    assert 'key' not in result

def test_delete_api_first_pet():
    """7 - Проверяем возможность удаления первого добавленного питомца """

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.post_api_pet(auth_key, "Суперт", "кот", "1", "images/cat1.jpg")
        _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][-1]['id']
    status, _ = pf.delete_api_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")

    # Проверяем, что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_put_api_pet_no_name(name='', animal_type='Кот', age=1):
    """8 - Проверяем возможность обновления информации о питомце юез указания его имени"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, "my_pets")


    if name == '':
        raise Exception('Не указано имя питомца')
    elif len(my_pets['pets']) > 0:
        status, result = pf.put_api_pet(auth_key, my_pets['pets'][0]['id'], name, animal_type, age,
                                    pet_photo='images/cat1.jpg')

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("Питомцев нет")

def test_get_my_pets_with_valid_key(filter='my_pets'):
    """9 - Проверяем, что запрос моих питомцев возвращает не пустой список.
    Доступное значение параметра filter - 'my_pets' либо '' """

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_pets(auth_key, filter)

    # Проверяем - если список своих питомцев пустой, то добавляем нового и запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.post_api_pet(auth_key, "Суперт", "кот", "1", "images/cat1.jpg")

    status, result = pf.get_list_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0

def test_post_api_create_pet_simple_unauthorized_user(name='Барбарис', animal_type='кот', age=5):
    """10 - Проверяем возможность добавить питомца без фото неавторизованным пользователем"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key('', '')

    # Добавляем питомца
    status, result = pf.post_api_create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name