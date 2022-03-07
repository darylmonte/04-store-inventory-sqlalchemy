from models import (Base, session, Product, engine)
import datetime
import csv
import time


# clean the price
def clean_price(price_str):
    try:
        price_float = float(price_str)
    except ValueError:
        input('''
            \n ***** PRICE ERROR *****
            \r The price should be a number without the currency symbol.
            \r Ex: 10.99
            \r Press enter to try again.
            \r ***********************''')
        return
    else:
        return int(price_float * 100)


# clean the date
def clean_date(date_str):
    split_date = date_str.split('/')
    month = int(split_date[0])
    day = int(split_date[1])
    year = int(split_date[2])
    return datetime.date(year, month, day)


# check for id error
def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
                    \r******* ID ERROR *******
                    \rThe ID should be a number
                    \rPress enter to try again
                    \r*************************''')
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
                \r******* ID ERROR *******
                \rOptions: ({options[0]} to {options[-1]})
                \rPress enter to try again
                \r*************************''')
            return


# add the csv to the database
def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            products = session.query(Product).filter(Product.product_name == row['product_name']).one_or_none()
            if products is None:
                name = row['product_name']
                price = clean_price(row['product_price'].split('$')[1])
                quantity = row['product_quantity']
                date = clean_date(row['date_updated'])
                new_product = Product(product_name=name, product_price=price, product_quantity=quantity, date_updated=date)
                session.add(new_product)
            elif products is not None:
                new_date = clean_date(row['date_updated'])
                duplicate_product = session.query(Product).filter(Product.product_name == row['product_name']).first()
                if products.product_name == duplicate_product.product_name and duplicate_product.date_updated <= new_date:
                    duplicate_product.product_price = clean_price(row['product_price'].split('$')[1])
                    duplicate_product.product_quantity = row['product_quantity']
                    duplicate_product.date_updated = new_date
        session.commit()


# main menu - view, add, create backup, exit
def menu():
    while True:
        print('''
            \r*** MAIN MENU ***
            \r[V] View A Product
            \r[A] Add A Product
            \r[B] Create A Backup
            \r[X] Exit
            \r*****************''')
        choice = input('\nWhat would you like to do? ').lower()
        if choice in ['v', 'a', 'b', 'x']:
            return choice
        else:
            input('''
                \rPlease choose one of the options above.
                \rPress enter to try again...''')


# loop runs program
def app():
    app_running = True
    while app_running:
        choice = menu()

        # View the Product
        if choice == 'v':
            options = []
            for item in session.query(Product):
                options.append(item.product_id)

            id_error = True
            while id_error:
                choice_id = input(f"\nEnter a product's ID number. ({options[0]} to {options[-1]}) ")
                id_choice = clean_id(choice_id, options)
                if id_choice:
                    id_error = False

            item = session.query(Product).filter(Product.product_id == id_choice).first()
            print(f'''
                \r***** {item.product_name} *****
                \rPrice: ${(item.product_price/100):.2f}
                \rQuantity: {item.product_quantity}
                \rDate Updated: {item.date_updated}''')
            print('*' * 20)
            input('\nPress ENTER to continue...')

        # Add a Product
        elif choice == 'a':
            # Ask for product name
            product_name = input('What is the name of the product? ')
            # Ask for quantity
            quantity_error = True
            while quantity_error:
                try:
                    product_quantity = int(input('How many products are available? '))
                except ValueError:
                    input('''
                        \n******* QUANTITY ERROR *******
                        \rInvalid entry. Please enter a whole number.
                        \rPress ENTER to try again
                        \r******************************''')
                else:
                    if type(product_quantity) == int:
                        quantity_error = False
            # Ask for price
            price_error = True
            while price_error:
                price = input('How much is the product? (Ex: 11.09) ')
                price = clean_price(price)
                if price:
                    price_error = False
            # Add date automatically
            date = datetime.date.today()

            new_product = Product(product_name=product_name, product_quantity=product_quantity, product_price=price, date_updated=date)

            # Checking for duplicate
            product_names = []
            for product in session.query(Product):
                product_names.append(product.product_name)

            if new_product.product_name in product_names:
                for product in session.query(Product):
                    if (new_product.product_name == product.product_name and new_product.date_updated >= product.date_updated):
                        new_product.product_id = product.product_id
                        session.delete(product)
                        session.commit()
                        print(f'\n{product_name} has been updated!')
                        input('Press ENTER to continue...')
                    elif (new_product.product_name == product.product_name and
                            new_product.date_updated < product.date_updated):
                        print('\nThis product is already up to date.')
                        input('Press ENTER to continue...')
            else:
                input(f'''
                    \r*** {product_name} added ***
                    \rPress ENTER to continue...''')

            session.add(new_product)
            session.commit()

        # Create a Backup of the DB as csv
        elif choice == 'b':
            with open('new_inventory.csv', 'a') as csv_file:
                header = ['product_name', 'product_price', 'product_quantity', 'date_updated']
                writer = csv.writer(csv_file)
                writer.writerow(header)
                for product in session.query(Product):
                    items = [product.product_name, product.product_price/100, product.product_quantity, product.date_updated]
                    writer.writerow(items)
                print('Backing up data...')
                time.sleep(1.5)
                input('''
                    \n*** New backup CSV file created ***
                    \rPress ENTER to continue ''')

        # Quit the App
        else:
            print('\nGoodbye. Thank you for using our app.\n')
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()
