#Customer Segmentation using RFM

#Import libraries and reading data
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")
df=df.copy()

#Data Preparation - look at some descriptive statistics
df.describe().T
df.head()
df.shape
df.columns

#Checking of Missing Values
df.isnull().sum()

#Remove the missing observations
df.dropna(inplace=True) 

#Unique Items
df.nunique()

#Product Items
df["Description"].value_counts()

#Rank the 5 most ordered products from most to least
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity",ascending=False).head()

#Remove the canceled transactions from the dataset
df = df[~df["Invoice"].str.contains("C", na=False)]

#The total amount of each invoice
df["TotalPrice"] = df["Quantity"] * df["Price"]

#RFM metriklerinin hesaplanması

#Recency: Date from customer's last purchase
#Frequency:  Total number of purchases
#Monetary: Total spend by the customer

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.columns=["Recency","Frequency","Monetary"]
rfm=rfm[(rfm["Monetary"]>0) & (rfm["Frequency"]>0)]
rfm.head()

#Calculating of RFM Metrics

#Date from customer's last purchase.The nearest date gets 5 and the furthest date gets 1.
rfm["recency_score"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
# Total number of purchases.The least frequency is 1 and the maximum frequency is 5.
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#Total spend by the customer. the least money gets 1, the most money gets 5.
rfm["monetary_score"]= pd.qcut(rfm["Monetary"],5,labels=[1,2,3,4,5])

#The value of 2 different variables that were formed was recorded as a RFM_SCORE
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))

#Segmenting customers using RFM score
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

#Interpretation of descriptive statistics of segments
rfm.groupby("segment")["segment", "Recency","Frequency","Monetary"].agg({"mean","count"}).head(20)

rfm[rfm["segment"] == "cant_loose"]
rfm[rfm["segment"] == "hibernating"]
rfm[rfm["segment"] == "potential_loyalists"]

#Getting excel output of a selected segment

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.to_excel("new_customers.xlsx")

#Reviews About the Segments

#Cant Loose

#There are 63 people in this segment.
#Shopping was done on average 133 days ago.
#The frequency of shopping is 8, the total number of purchases is 63.
#A total of £102,54 has been spent.

#Action:
#Even if the last purchase was made 133 days, the total number of purchases is high. 
#It is a group of customers who do not come for a long time, but also make a lot of purchases when they come. 
#We can analyze the process by sending surveys to these customers, and we can be changed by sharing personalized campaigns by e-mail.

#Need Attention

#There are 187 people in this segment.
#Shopping was done on average 52 days ago.
#The frequency of shopping is 2, the total number of purchases is 3.
#A total of £12,602 has been spent.

#Action:
#These customers need to be reminded of the brand. 
#So,short-term discounts can be made to remind these customers of our brand and allow them to shop again.
