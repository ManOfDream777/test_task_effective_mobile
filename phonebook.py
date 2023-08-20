import json
import math

# Пакет rich для стилизации консольного вывода
from rich import print
from rich.traceback import install
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt

console = Console()

install()

# Разделитель нужен для разделения данных в txt файле
separator = '----------'


class PersonInBook:
    """ 
        Пользователь в телефонном справочнике
    """

    def __init__(
        self,
        id: int,
        surname: str,
        name: str,
        middlename: str,
        personal_phone: str,
        org_name: str | None,
        phone_for_work: str | None,
    ) -> None:
        self.id = id
        self.surname = surname
        self.name = name
        self.middlename = middlename
        self.org_name = org_name
        self.phone_for_work = phone_for_work
        self.personal_phone = personal_phone

    def as_dict(self) -> dict:
        """ Метод для быстрого преобразования данных класса в словарь и последующего сохранения """
        return {
            'id': self.id,
            'surname': self.surname,
            'name': self.name,
            'middlename': self.middlename,
            'org_name': self.org_name,
            'phone_for_work': self.phone_for_work,
            'personal_phone': self.personal_phone
        }

    def full_info(self) -> str:
        """ Метод для быстрого получения данных об экземпляре класса """
        return 'ФИО: {0} {1} {2} \nОрганизация: {3} \nРабочий телефон: {4} \nЛичный телефон: {5}'.format(
            self.surname,
            self.name,
            self.middlename,
            self.org_name,
            self.phone_for_work,
            self.personal_phone,
        )


class PhoneBook:
    """ 
        Телефонный справочник
    """

    def __init__(self) -> None:
        self._default_pagination: int = 10
        self._data: list[dict] = self._normalize_data()
        self._analog_dict = {
            'фамилия': 'surname',
            'имя': 'name',
            'отчество': 'middlename',
            'организация': 'org_name',
            'рабочий телефон': 'phone_for_work',
            'личный телефон': 'personal_phone',
        }  # для получения необходимого ключа по запросу пользователя

    def __len__(self) -> int:
        return len(self._data)

    @property
    def data(self):
        """ Удобное получения данных """
        return self._data

    def _normalize_data(self):
        """ Преобразование текста из файла в python list[dict] object """
        lines = [line.rstrip('\n') for line in self._read_file() if line.rstrip(
            '\n') != '' and line.rstrip('\n') != separator]  # Убираем пустые строки и переносы строки
        data = []
        data_id = 0  # id для создания нового словаря и занесение в него данных
        for line in lines:
            if line.startswith('{'):
                data.append({})
                continue
            if not line.startswith('}'):
                key, value = line.split(':')
                # Удаление где необходимо ненужных символов
                key = key.replace('\"', '').replace(',', '').strip()
                # Удаление где необходимо ненужных символов
                value = value.replace('\"', '').replace(',', '').strip()
                if value == 'null':
                    value = 'Не указан'
                data[data_id][key] = value
            else:
                data_id += 1
                continue
        return data

    def _read_file(self) -> list[str]:
        """ Открытие файла и чтение всего файла """
        try:
            with open('phonebook.txt', 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            """ Если файл не найден, создаем и далее открываем """
            with open('phonebook.txt', 'x') as file:
                pass

            with open('phonebook.txt', 'r') as file:
                return file.readlines()

    def _update_data(self) -> None:
        """ Обновление атрибута data, для работы с ним """
        self._data = self._normalize_data()

    def display_all_contacts_by_pagination(self, pagination: int = 0) -> bool:
        """ Отображение всех данных с помощью пагинации. По умолчанию выводится 10 записей, согласно self._default_pagination """

        # Устанавливаем значение предыдущей пагинации, для правильного вывода страниц, Если атрибут уже есть, то идем дальше
        if not hasattr(self, 'previous_pagination'):
            self.__setattr__('previous_pagination', 0)

        # Устанавливаем значение текущей страницы, для правильного вывода страниц, Если атрибут уже есть, то идем дальше
        if not hasattr(self, 'page'):
            self.__setattr__('page', 1)

        previous_pagination = self.__getattribute__('previous_pagination')
        page = self.__getattribute__('page')

        # Создание таблиц и колонок пакета rich
        table = Table(title='Ваши контакты')
        table.add_column('Фамилия', style='magenta')
        table.add_column('Имя', style='magenta')
        table.add_column('Отчество', style='magenta')
        table.add_column('Организация', style='magenta')
        table.add_column('Рабочий телефон', style='magenta')
        table.add_column('Личный телефон', style='magenta')

        if pagination == 0:
            pagination = self._default_pagination

        # Всего страниц в зависимости от пагинации
        total_pages = math.ceil(len(self.data) / pagination)

        if previous_pagination != 0:
            pagination += previous_pagination
            page += 1

        for person in self.data[previous_pagination:pagination]:
            table.add_row(person.get('surname'),
                          person.get('name'),
                          person.get('middlename'),
                          person.get('org_name'),
                          person.get('phone_for_work'),
                          person.get('personal_phone'),
                          )
        console.print(table)
        self.__setattr__('previous_pagination', pagination)
        self.__setattr__('page', page)

        print(f'Страница {page} из {total_pages}')
        if page == total_pages:
            return False
        return True

    def add_new_contact(self, PersonInBook: PersonInBook) -> bool:
        """ Добавление нового контакта """
        """ По сути можно было обойтись без try except, так как код будет всегда срабатывать, но хотелось бы возвращать статус об успешности операции """
        try:
            with open('phonebook.txt', 'a', encoding='utf-8') as file:
                json.dump(PersonInBook.as_dict(), file,
                          ensure_ascii=False, indent=4)
                file.write(f'\n\n\n{separator}\n\n\n')
            self._update_data()
            return True
        except Exception:
            return False

    def edit_contact(self) -> None:
        """ Редактирование контакта """

        """ Логику работы с пользователем стоило вынести за пределы этого метода, но я решил уже оставить так. Считаю, что все достаточно читаемо и работает что самое главное """

        table = Table(title='Ваши контакты')
        table.add_column('ID', style='magenta')
        table.add_column('Фамилия', style='magenta')
        table.add_column('Имя', style='magenta')
        table.add_column('Отчество', style='magenta')
        table.add_column('Организация', style='magenta')
        table.add_column('Рабочий телефон', style='magenta')
        table.add_column('Личный телефон', style='magenta')

        # Использование здесь ID нужно для того, чтобы пользователь по ID выбрал какую запись ему редактировать. Хоть ID здесь. число меньше на 1, чем фактическое ID, но для простоты и удобство пользования я решил сделать так.
        for iter, contact in enumerate(self.data, start=1):
            table.add_row(str(iter), contact.get('surname'), contact.get('name'), contact.get(
                'middlename'), contact.get('org_name'), contact.get('phone_for_work'), contact.get('personal_phone'),)

        console.print(table)
        number = int(input(('Выберите цифру контакта для изменения: ')))

        print('Что хотите изменить?')
        print(
            'Поля для изменения: \n[underline]Фамилия[/], [underline]Имя[/], [underline]Отчество[/], [underline]Организация[/], [underline]Рабочий телефон[/], [underline]Личный телефон[/]')
        while True:
            contact = self.data[number - 1]
            field = input(
                'Введите название поля или exit для выхода: ').lower().strip()
            if field in self._analog_dict.keys():
                field = self._analog_dict[field]
                value = input('Новые данные: ')
                contact[field] = value
                print('\nФИО: {0} {1} {2} \nОрганизация: {3} \nРабочий телефон: {4} \nЛичный телефон: {5} \n'.format(
                    contact.get('surname'),
                    contact.get('name'),
                    contact.get('middlename'),
                    contact.get('org_name'),
                    contact.get('phone_for_work'),
                    contact.get('personal_phone'),
                ))
                with open('phonebook.txt', 'w') as file:
                    for contact in self.data:
                        json.dump(contact, file, ensure_ascii=False, indent=4)
                        file.write(f'\n\n\n{separator}\n\n\n')
                self._update_data()
                continue
            elif field.strip() == 'exit':
                break
            print('Введенное поле не найдено')
            continue

    def search_contact(self, value: str) -> list[dict]:
        """ Поиск контакта по введенному значению. Искать можно по любому полю. Возможно, не самая быстрая реализация поиска, зато рабочая """
        if value.strip() == '':
            return self.data
        filtered_data = []
        value = value.lower()
        for contact in self.data:
            values = list(contact.values())
            for i in values:
                if value in i.lower():
                    filtered_data.append(contact)
                    break
        return filtered_data


def main():
    """ Основная функция для запуска программы """
    phonebook = PhoneBook()
    console.print(
        'Вы открыли программу "Телефонный справочник" ', style='cyan')
    if len(phonebook) == 0:
        """ Проверка на первый запуск программы """
        print(
            'Прежде всего добавьте свой контакт. Поля со [underline]звездочкой*[/] обязательны к заполнению.')
        surname = input('Ваша фамилия*: ').strip()
        name = input('Ваше имя*: ').strip()
        middlename = input('Ваше отчество*: ').strip()
        personal_phone = input('Личный (сотовый) телефон*: ').strip()
        org_name = Prompt.ask('Организация', default='Не указано').strip()
        phone_for_work = Prompt.ask(
            'Рабочий телефон', default='Не указано').strip()

        if surname == '' or name == '' or middlename == '' or personal_phone == '':
            """ Проверка на заполнение обязательных полей. Если не заполнено, программа завершит работу! """
            print(
                'Одно или несколько обязательных полей не были заполнены. Попробуйте еще раз')
            return

        owner = PersonInBook(
            id=0,
            surname=surname,
            name=name,
            middlename=middlename,
            personal_phone=personal_phone,
            org_name=org_name,
            phone_for_work=phone_for_work,
        )
        phonebook.add_new_contact(owner)
        print(owner.full_info())
    while True:
        print('Выберите что хотите сделать')
        print("""
                1. Посмотреть все контакты
                2. Добавить новый контакт
                3. Редактировать контакт
                4. Найти контакт
                5. [red]Выйти[/]
        """)
        choice = int(Prompt.ask('Укажите цифру', default=5))

        if choice == 1:
            pagination = int(Prompt.ask(
                'Укажите размер пагинации выводимых данных. По умолчанию значение = 10', default=0))
            if pagination >= 0:
                while True:
                    result = phonebook.display_all_contacts_by_pagination(
                        pagination)
                    
                    if result:
                        input('Нажмите любую кнопку чтобы продолжить')
                        continue

                    console.print(
                        'Ваш телефонный справочник закончился.', style='green')
                    
                    # Возвращение к дефолтному значению атрибутов, после полной отработки метода, для правильной работы при следующем запуске
                    phonebook.__setattr__('previous_pagination', 0)
                    phonebook.__setattr__('page', 1)
                    input('Нажмите любую кнопку чтобы продолжить')
                    break
            else:
                console.print(
                    'Пагинация не может быть отрицательной!', style='red')
                continue

        elif choice == 2:
            print(
                'Поля со звездочкой [red][underline]обязательны[/][/] к заполнению.')
            
            surname = input('Ваша фамилия*: ').strip()
            name = input('Ваше имя*: ').strip()
            middlename = input('Ваше отчество*: ').strip()
            personal_phone = input('Личный (сотовый) телефон*: ').strip()
            org_name = Prompt.ask('Организация', default='Не указано').strip()
            phone_for_work = Prompt.ask(
                'Рабочий телефон', default='Не указано').strip()
            
            if surname == '' or name == '' or middlename == '' or personal_phone == '':
                console.print(
                    'Одно или несколько обязательных полей не были заполнены. Попробуйте еще раз', style='red')
                continue

            contact = PersonInBook(
                id=len(phonebook),
                surname=surname,
                name=name,
                middlename=middlename,
                personal_phone=personal_phone,
                org_name=org_name,
                phone_for_work=phone_for_work,
            )
            result = phonebook.add_new_contact(contact)

            if result:
                print('\n' + contact.full_info() + '\n')
                input('Нажмите любую кнопку чтобы продолжить')
                continue

            console.print('Возникла ошибка при сохранении контакта. Вероятно, что то произошло с файлом или его расположение изменилось. Убедитесь, что файл расположен рядом с программой и попробуйте еще раз', style='red')
            input('Нажмите любую кнопку чтобы продолжить')
            continue

        elif choice == 3:
            phonebook.edit_contact()
            continue

        elif choice == 4:
            value = input(
                'Введите строку для поиска в Вашем телефонном справочнике: ')
            filtered_data = phonebook.search_contact(value)

            if len(filtered_data) != 0:
                table = Table(title='Найденные контакты')
                table.add_column('ID', style='red')
                table.add_column('Фамилия', style='magenta')
                table.add_column('Имя', style='magenta')
                table.add_column('Отчество', style='magenta')
                table.add_column('Организация', style='magenta')
                table.add_column('Рабочий телефон', style='magenta')
                table.add_column('Личный телефон', style='magenta')

                for contact in filtered_data:
                    table.add_row(
                        contact.get('id'),
                        contact.get('surname'),
                        contact.get('name'),
                        contact.get('middlename'),
                        contact.get('org_name'),
                        contact.get('phone_for_work'),
                        contact.get('personal_phone'),
                    )

                console.print(table)
            else:
                console.print(
                    'Контактов с таким содержимым не было найдено', style='red')
                
            input('Нажмите любую кнопку чтобы продолжить')
            continue

        elif choice == 5:
            console.print(
                'Спасибо за использование, до свидания!', style='cyan')
            break

        else:
            console.print('Выбранной опции нет в списке!', style='red')
            continue


if __name__ == '__main__':
    main()
