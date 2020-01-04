from lxml import etree
import re
import csv
import mysql.connector
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
db_config = config['Database']

# Connect to db
mydb = mysql.connector.connect(
  host=db_config['host'],
  user=db_config['user'],
  passwd=db_config['password'],
  database=db_config['database']
)

# Open file
csvfile = open('./data.csv', 'w+',)
writer = csv.writer(csvfile)
writer.writerow(['reference', 'title', 'category', 'description', 'category', 'gender', 'color', 'composition','photo'])

typeMap = {
    'Casacos' : 'Casacos',
    'Blusões' : 'Casacos',
    'Casacos e Sobretudos' : 'Casacos',
    'Casacos em pele' : 'Casacos',
    'Coletes' : 'Casacos',
    'Capas' : 'Casacos',
    'Fatos' : 'Fatos',
    'Blazers' : 'Blazers',
    'Denim' : 'Calças e Calções',
    'Calças' : 'Calças e Calções',
    'Calções' : 'Calças e Calções',
    'Macacões' : 'Calças e Calções',
    'Vestidos em tecido': 'Vestidos',
    'Vestidos em malha': 'Vestidos',
    'Saias em tecido' : 'Saias',
    'Saias em tecido' : 'Saias',
    'Camisolas' : 'Camisolas',
    'Pullovers' : 'Camisolas',
    'Polo manga curta' : 'Camisolas',
    'T-shirts' : 'T-shirts',
    'Sweats' : 'Sweats',
    'Camisas Slim Fit': 'Camisas',
    'Camisas Slim Fit': 'Camisas',
    'Camisas Regular Fit': 'Camisas',
    'Túnicas e Tops em tecido' : 'Túnicas e Tops',
    'Túnicas e Tops em malha' : 'Túnicas e Tops',
    'Sapatos' : 'Calçado',
    'Botas' : 'Calçado',
    'Sapatilhas' : 'Calçado',
    'Alpercatas' : 'Calçado',
    'Sandálias' : 'Calçado',
}

genderMap = {
    'man' : 'M',
    'woman': 'W'
}


# Clean gender field
def clean_gender (gender):
    try:
        ret = genderMap[gender.lower()]
    except:
        ret = None 
    return ret

# Clean category field
def clean_category (category):
    try:
        ret = typeMap[category]
    except:
        ret = None 
    return ret

# Clean title field
def clean_title(title):
    title = re.sub(r'\d+$', '', title) # Remove sizes Numbers
    title = re.sub(r'(L|XL|XXL|3XL|S|M|XS|XXS)$', '', title) # remove sizes Letters
    return title

def write_to_csv(file, obj):
    writer.writerow(obj.values())

# Get Colors in Database
def getColors(): 
    colors = {}
    mycursor = mydb.cursor()

    sql = f"SELECT DISTINCT color_id, name FROM color"

    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for row in myresult:
        colors[row[1]] = row[0] 

    mycursor.close()
    return colors

# Get Types in Database
def getTypes(): 
    categories = {}
    mycursor = mydb.cursor()

    sql = f"SELECT DISTINCT type_id, name FROM type"

    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for row in myresult:
        categories[row[1]] = row[0] 

    mycursor.close()

    return categories

# Get brands in database
def getBrands(): 
    brands = {}
    mycursor = mydb.cursor()

    sql = f"SELECT DISTINCT brand_id, name FROM brand"

    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for row in myresult:
        brands[row[1].capitalize()] = row[0] 

    mycursor.close()

    return brands

# Get existing color
db_colors = getColors()
print(db_colors)

# Get existing types
db_types = getTypes()
print(db_types)

# Get existing brands 
db_brands = getBrands()
print(db_brands)

# Load item to database
def load_item(item):
    mycursor = mydb.cursor()

    color = db_colors.get(item['color'], -1)
    type = db_types.get(item['category'], -1)

    price = item['price']
    gender = item['gender']
    description = item['description']
    reference = item['reference']
    photo = item['photo']
    composition = item['composition']

    if color != -1 and type != -1:
        sql = f"INSERT INTO item VALUES (NULL, 1, '{color}', '{type}', '{price}', '{gender}', '{description}', 'dummy_url', '{reference}', '{photo}', '{composition}',1)"
        mycursor.execute(sql)

    mydb.commit()

    mycursor.close()

# Start parsing
root = etree.parse("./feed.xml")

products = root.findall('product')

total_items = 0
total_parents = 0 


for product in products: 
    total_items += 1
    if product.find('parent_id') is None:
        total_parents += 1
        obj = {}

        obj['reference'] = product.find('reference').text
        obj['title'] = clean_title(product.find('title').text)
        obj['category'] = clean_category(product.find('sub_category2').text)
        obj['description'] = product.find('description').text
        obj['price'] = product.find('sale_price_amazon_pt').text
        obj['gender'] = clean_gender(product.find('gender').text)
        obj['color'] = product.find('color').text
        composition = product.find('composition')
        obj['composition'] =  composition.text if composition is not None else ''
        obj['photo'] = product.find('image_url_1').text

        if (obj['gender'] is not None):
            write_to_csv(csvfile, obj)
            load_item(obj)

print('Total items:', total_items)
print('Used items:', total_parents)






