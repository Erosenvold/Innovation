import openfoodfacts


#Number of allergens
numbers = [1,2,3,4,5]

#Setting variables to default values
keywordsExists = False
allergensExists = False
ingredientsExists = False
vegetarian, vegan = "", ""

#Dict for finding allergens
foundRestrictions = {
    "vegetarianKeywords": False,
    "veganKeywords" : False,
    "lactoseKeywords": False,
    "lactoseAllergy": False,
    "nutKeywords": False,
    "nutAllergy": False,
    "customIngrKeywords": False,
    "customIngrAllergy": False
}

#Dict for different dietary restrictions
allergens = {
    "Vegetarian":["meat","beef","pork","chicken","turkey","fish","poultry","en:meat","en:beef","en:pork","en:chicken","en:turkey","en:fish","en:poultry"],
    "Vegan":["gelatin","eggs","egg","en:gelatin","en:eggs","en:egg"],
    "Nut":["en:almonds","en:hazelnut","en:cashew","en:peanut","en:nuts","en:nut","nut","en:walnut","almonds","hazelnut","cashew","peanut","nuts","walnut"],
    "Lactose":["en:dairy","en:cheese","en:cream","en:yogurt","en:yoghurt","en:milk","dairy","cheese","cream","yogurt","yoghurt","milk"],
    "CustomAllergy":[""]
}


#Making a custom list of allergens
def customAllergy():
    customAllergene = []
    done = False
    while(not done):
        print("Please enter an allergen")
        item = input().lower()

        if item:
            customAllergene.append("en:"+item)
            customAllergene.append(item)
            if not item.endswith('s'): 
                customAllergene.append("en:"+item+'s')
                customAllergene.append(item+'s')
        else:
            print("Please enter something")
            print()

        print("Do you wish to enter another allergen? Y/N")
        answer = input().lower()
        done = True if answer == 'n' else False
        print()
    
    allergens["CustomAllergy"] = customAllergene


#Checks if a given requirement can eat a certain item, returns True if edible, false otherwise
def edible(req):
    global keywordsExists,allergensExists,ingredientsExists,foundRestrictions,vegetarian,vegan
    edible = True
    
    #Vegetarian Checks
    if (req == 1):
        if ingredientsExists and vegetarian == "no":
            edible = False
            
        elif keywordsExists:
            edible = False if foundRestrictions["vegetarianKeywords"] else True
    
    #Vegan checks        
    if req == 2:
        if ingredientsExists and vegan == "no":
            edible = False
        elif keywordsExists:
            edible = False if foundRestrictions["vegetarianKeywords"] and foundRestrictions["veganKeywords"] and foundRestrictions["lactoseKeywords"] else True
        elif allergensExists:
            edible = False if foundRestrictions["lactoseAllergy"] else True
    
    #Nut allergy checks            
    if req == 3:
        if keywordsExists:
            edible = False if foundRestrictions["nutKeywords"] else True
            
        elif allergensExists:
            edible = False if foundRestrictions["nutAllergy"] else True
    
    #Lactose checks        
    if req == 4:
        if keywordsExists:
            edible = False if foundRestrictions["lactoseKeywords"] else True
            
        elif allergensExists:
            edible = False if foundRestrictions["lactoseAllergy"] else True

    if req == 5:
        if keywordsExists:
            edible = False if foundRestrictions["customIngrKeywords"] else True
        elif allergensExists:
            edible = False if foundRestrictions["customIngrAllergy"] else True
    
    return edible   


# Extracting keywords, ingredients, and allergens info
def extractInfo(productInfo):
    global keywordsExists,allergensExists,ingredientsExists,foundRestrictions,vegetarian,vegan

    #Checks if keywords exists in products information
    if "_keywords" in productInfo:
        productKeywords = productInfo.get("_keywords") #list of strings
        keywordsExists = True
        foundRestrictions["vegetarianKeywords"] = bool(set(productKeywords) & set(allergens.get("Vegetarian")))
        foundRestrictions["veganKeywords"] = bool(set(productKeywords) & set(allergens.get("Vegan")))
        foundRestrictions["nutKeywords"] = bool(set(productKeywords) & set(allergens.get("Nut")))
        foundRestrictions["lactoseKeywords"] = bool(set(productKeywords) & set(allergens.get("Lactose")))
        foundRestrictions["customIngrKeywords"] = bool(set(productKeywords) & set(allergens.get("CustomAllergy")))
    
    #Checks if allergens exists in products information
    if "allergens" in productInfo:
        productAllergens = productInfo.get("allergens").split(",")#List of strings
        allergensExists = True
        foundRestrictions["nutAllergy"] = bool(set(productAllergens) & set(allergens.get("Nut")))
        foundRestrictions["lactoseAllergy"] =  bool(set(productAllergens) & set(allergens.get("Lactose")))
        foundRestrictions["customIngrAllergy"] = bool(set(productAllergens) & set(allergens.get("CustomAllergy")))
    
    #Checks if ingredients exists in products information
    if("ingredients" in productInfo):
        productIngre = productInfo.get("ingredients")[0] #dict
        vegetarian = productIngre.get("vegetarian") #string
        vegan = productIngre.get("vegan") #string
        ingredientsExists = True



if __name__ == "__main__":
    isNumber = False
    while(not isNumber):
        print("[1] Vegetarian\n[2] Vegan\n[3] Nut allergy\n[4] Lactose intolerant\n[5] Create customized dietary restriction")
        print("Enter the number of your dietary requirement: ")
        req = int(input())
        isNumber = req in numbers
        if not isNumber:
            print("Please enter a valid choice of number")
        print()

    #making a custom allergene list
    if req == 5:
        customAllergy()

    done = False
    while(not done):
         #Setting variables to default values
        keywordsExists, allergensExists, ingredientsExists = False, False, False
        vegetarian, vegan = "", ""
            
        for i in foundRestrictions:
            foundRestrictions[i] = False
        print("Enter the barcode of the item you would like: ")
        item = input()
        print()

        #Gets the product information from a given barcode
        productInfo = openfoodfacts.get_product(f'{item}')
        if productInfo.get("status") == 1:
            productInfo = productInfo.get("product")
            extractInfo(productInfo)

            #Check on all keys existence, terminate if missing keys are relevant
            if not keywordsExists and not allergensExists and not ingredientsExists:
                print("We cannot give a safe estimate on this product because we have too little information")
            else:
                print(f'The product: {productInfo.get("product_name")} is: ')
                if not edible(req):
                    print("Not safe to eat!")
                else:
                    print("Ok to eat!")
        else:
            print("I'm sorry we didn't have any data on this product.")
        print("\nWant to check another product? Y/N")
        response = input().lower()
        print()

        done= True if response == "n" else False

