import pandas as pd
from sqlalchemy import create_engine

# Koneksi MySQL
engine = create_engine("mysql+mysqlconnector://root:password_kamu@localhost/coffee_Sales")

# Baca file CSV
df = pd.read_csv("Coffe_sales.csv")

# Simpan ke tabel MySQL
df.to_sql("penjualan", con=engine, if_exists="replace", index=False)

print("✅ Data berhasil diimpor ke MySQL!")
