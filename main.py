from numpy import mean, sort
import requests
import pandas as pd
import matplotlib.pyplot as plt


baseurl = "https://dummyjson.com"


'''make api call to prducts endpoint'''
def fetchProducts():
    try:
        response = requests.get(f"{baseurl}/products")
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])

        productdf = pd.DataFrame(products)
        return productdf

    except requests.exceptions.RequestException as e:
        print(f"Error fetching products: {e}")
        return None
    

'''make api call to cart endpoint'''
def fetchCartData():
    try:
        response = requests.get(f"{baseurl}/carts")
        response.raise_for_status()
        data = response.json()
        carts = data.get("carts", [])

        cartdf = pd.DataFrame(carts)
        return cartdf
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cart info: {e}")
        return None
    
'''make api call to users endpoint'''
def fetchUserData():
    try:
        response = requests.get(f"{baseurl}/users")
        response.raise_for_status()
        data = response.json()
        users = data.get("users", [])

        userdf = pd.DataFrame(users)
        return userdf, data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user info: {e}")
        return None

''' finds the unique categories in the data and sums up their total stock'''
def getCats(df):
    catList = []
    for i in range(0, len(df)):
        catExists = any(item["category"] == df.loc[i]["category"] for item in catList)
        if catExists:
            for j in catList:
                if j["category"] == df.loc[i]["category"]:
                    j["stock"] += df.loc[i]["stock"]
                    break
        else:
            catList.append({"category": df.loc[i]["category"], "stock": df.loc[i]["stock"]})

    return catList



'''will arrange items and prices from cheapest to most expensive'''
def orderByPrice(df):
    srted = df.sort_values(by='price')
    return srted



def avgPricePerCat(df):
    return df.groupby("category")["price"].mean().reset_index()


if __name__ == "__main__":
    """ products = fetchProducts()
    if not products.empty:
        products.to_csv("products.csv")

        avgPriceByCat = avgPricePerCat(products) #find average price by category
        print("The average price per category is as follows: ")
        print(avgPriceByCat)
        
        catList = getCats(products)
        stockByCat = pd.DataFrame(catList)

        stockByCat.plot.bar("category", "stock") #find the most stocked category
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        orderedByPrice = orderByPrice(products) # find most and least expensive items 
        print("The cheapest 5 products are as follows:")
        print(orderedByPrice[['id', 'title', 'description', 'price']].head())
        print("The most expensive 5 products are as follows:")
        print(orderedByPrice[['id', 'title', 'description', 'price']].tail())

        # find correlation between price and rating
        # as the rating goes down, price goes up: inverse linear relationship
        priceVsRating = pd.DataFrame({"rating": products["rating"], "price":products["price"]})
        correlationMatrix = priceVsRating.corr()
        correlationMatrix.plot()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("product df is empty") """

    cartData = fetchCartData()
    if not cartData.empty:
        cartData.to_csv("cartdata.csv") #write cart data to csv
        # find out how often unique items appear in carts and print the top 5 
        prdctAppearsInCarts = {"title": [], "qty": []}
        for product in cartData["products"]:
            title = product[0]["title"]
            qty = product[0]["quantity"]
            if title not in prdctAppearsInCarts["title"]:
                prdctAppearsInCarts["title"].append(title)
                prdctAppearsInCarts["qty"].append(qty)
            elif title in prdctAppearsInCarts["title"]:
                idx = prdctAppearsInCarts["title"].index(title)
                prdctAppearsInCarts["qty"][idx] += qty

        appearsInCartsDF = pd.DataFrame(prdctAppearsInCarts)
        srted = appearsInCartsDF.sort_values(by="qty", ascending=False)
        print(srted.head())

        # find avg cart value (total cost per cart before discount) 
        totalBeforeDiscount = []
        for product in cartData["products"]:
            totalBeforeDiscount.append(product[0]["total"])
        avg = mean(totalBeforeDiscount)
        print(f"The average cart value is {avg}")

        sumOfCarts = 0
        for total in totalBeforeDiscount:
            sumOfCarts += total

        print(f"The total sales are {sumOfCarts}")

        # add userid to totalBeforeDiscount and make into dict of lists, then order by cart total (desc)
        # take top 5 userids and pull the relevant info of the rows with those userids from the user endpoint
        totalsPerUser = {"total": totalBeforeDiscount, "userid": []}
        for i in range(0, len(cartData)):
            totalsPerUser["userid"].append(cartData.loc[i]["userId"])
        totalsPerUserdf = pd.DataFrame(totalsPerUser)
        top5carts = totalsPerUserdf.sort_values(by="total", ascending=False).head()
        print(top5carts)
        userInfo = []


    userdf, jsonData = fetchUserData()


    """ userdf.to_csv("userinfo.csv")
    for user in top5carts["userid"]:
        for k in range(0, len(userdf)):
            if userdf.loc[k]["id"] == user:
                userInfo.append(userdf.loc[k])
    print(userInfo) """


    #group users by gender 
    female_tuple, male_tuple = userdf.groupby("gender") #male and female are tuples with the dataframe as element 1 in each tuple
    female = female_tuple[1].reset_index()
    male = male_tuple[1].reset_index()

    #find avg cart value based on gender groups
    femaleCartSum = 0
    for idx in range(0, len(female)):
        for idx2 in range(0, len(cartData)):
            if cartData.loc[idx2]["userId"] == female.loc[idx]["id"]:
                femaleCartSum += cartData.loc[idx2]["total"]

    avgFCartVal = femaleCartSum / len(female)
    print(f"The average cart value of female users is {avgFCartVal}")

    maleCartSum = 0
    for idx in range(0, len(male)):
        for idx2 in range(0, len(cartData)):
            if cartData.loc[idx2]["userId"] == male.loc[idx]["id"]:
                maleCartSum += cartData.loc[idx2]["total"]

    avgMCartVal = maleCartSum / len(male)
    print(f"The average cart value of male users is {avgMCartVal}")


    #find avg age and age range based on groups
    avgFAge = mean(female["age"])

    ageSorted = female.sort_values(by = "age").reset_index()
    youngest = ageSorted["age"][0]
    oldest = ageSorted["age"][len(ageSorted) - 1]

    print(f"The avg age of female users is {avgFAge}; the youngest is {youngest} and the oldest is {oldest}")

    avgMAge = mean(male["age"])

    MageSorted = male.sort_values(by = "age").reset_index()
    myoungest = MageSorted["age"][0]
    moldest = MageSorted["age"][len(MageSorted) - 1]

    print(f"The avg age of male users is {avgMAge}; the youngest is {myoungest} and the oldest is {moldest}")

    # analyze spending habits by demographic
    cartsExpanded = cartData.explode('products')
    normalized = pd.json_normalize(jsonData['users'])
    merged = cartsExpanded[['id', 'userId', 'total']].merge(normalized[['id', 'age', 'gender', 'address.city']], left_on="userId", right_on="id", suffixes=('_cart', '_user'))

    print("The columns of Merged follow: ")
    print(merged.head(2))

    spendingByAge = merged.groupby('age')['total'].mean()
    spendingByGender = merged.groupby('gender')['total'].mean()
    spendingByCity = merged.groupby("address.city")['total'].mean()

    """ plt.figure(figsize=(12, 5))
    spendingByAge.plot(kind='bar', title="Avg Spending by Age")
    plt.xlabel("Age")
    plt.ylabel("Avg Spending ($)")
    plt.xticks(rotation = 45)
    plt.show()


    plt.figure(figsize=(6, 4))
    spendingByGender.plot(kind='bar', title = "Avg Spending by Gender", color=['pink', 'blue'])
    plt.xlabel("Gender")
    plt.ylabel("Avg Spending")
    plt.show()

    plt.figure(figsize=(12, 5))
    spendingByCity.nlargest(10).plot(kind = 'bar', title = "Top 10 cities by avg spending")
    plt.xlabel("City")
    plt.ylabel("Avg Spending")
    plt.xticks(rotation = 45)
    plt.show() """


    # calculate profit margin per item sold

    # grab relevant columns from Cart Data's product dicts
    productsInCarts = cartData["products"] #note that this is a series containing lists of dicts
    itemsDict = {"Title": [], "Quantity": [], "Price": [], "EstimatedCost": [], "DiscountPercent": []} # estimated cost is just the discounted price for the purpose of simplicity
    for seriesElement in productsInCarts: 
        for itemdict in seriesElement:
            itemsDict["Title"].append(itemdict["title"])
            itemsDict["Quantity"].append(itemdict["quantity"])
            itemsDict["Price"].append(itemdict["price"])
            itemsDict["DiscountPercent"].append(itemdict["discountPercentage"])
            itemsDict["EstimatedCost"].append(itemdict["price"] * (1 - (itemdict["discountPercentage"] * 0.01)))
    
    itemsdf = pd.DataFrame(itemsDict)
    
    #profit margin per item
    itemsdf["profMargPerItem"] = ((itemsdf["Price"] - itemsdf["EstimatedCost"]) / itemsdf["Price"]) * 100

    #do the actual profit margin calculation (for overall)

    revenueSum = sum(itemsdf["Quantity"] * itemsdf["Price"])
    estCostSum = sum(itemsdf["EstimatedCost"] * itemsdf["Quantity"])
    totalProfit = revenueSum - estCostSum
    
    overAllProfMarg = (totalProfit / revenueSum) * 100

    print(f"The profit margin overall (with a nod to the estimations made) is {overAllProfMarg}%")

