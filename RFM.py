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

#RFM skorlarının hesaplanması

#Recency (1 en yakın, 5 en uzak tarihi temsil eder)
rfm["recency_score"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
#Frequency (1 en az satın alma sayısını, 5 en çok satın alma sayısını temsil eder)
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#Monetary (1 en az parasal değeri, 2 en fazla parasal değeri temsil eder)
rfm["monetary_score"]= pd.qcut(rfm["Monetary"],5,labels=[1,2,3,4,5])

#Oluşan 2 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
type("recency_score")
type("frequency_score")
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))

#RFM Skorlarının Segment Olarak Tanımlanması ve İsimlendirilmesi
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

#Segmentlere göre RFM metriklerinin ortalama ve sıklık değerlerini gruplama
rfm.groupby("segment")["segment", "Recency","Frequency","Monetary"].agg({"mean","count"}).head(20)

rfm[rfm["segment"] == "cant_loose"]
rfm[rfm["segment"] == "hibernating"]
rfm[rfm["segment"] == "potential_loyalists"]

#Seçilen bir segmentin excel çıktısının alınması

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.to_excel("new_customers.xlsx")
