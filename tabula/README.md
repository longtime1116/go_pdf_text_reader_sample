# 導入

```
brew install openjdk
echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME=$(/usr/libexec/java_home)' >> ~/.zshrc
. ~/.zshrc
```

# memo: どれくらいのarea領域を指定するといい感じになるか

## sales_by_productの場合

```
/usr/bin/python3 pdf_to_csv_tabula.py ~/Downloads/drive-download-20251001T051013Z-1-001/sales_by_product_2025.pdf -o out --outfile sales_by_product_2025.csv -a "80,28,555,820" --mode stream --guess false --merge
```

## product_by_supplierの場合

```
/usr/bin/python3 pdf_to_csv_tabula.py ~/Downloads/drive-download-20251001T051013Z-1-001/product_by_supplier_2025.pdf -o out --outfile product_by_supplier_2025.csv -a "80,28,570,820" --mode stream --guess false
--merge
```

## product_by_buyerの場合


```
/usr/bin/python3 pdf_to_csv_tabula.py ~/Downloads/drive-download-20251001T051013Z-1-001/product_by_buyer_2025.pdf -o out --outfile product_by_buyer_2025.csv -a "90,28,570,820" --mode stream --guess false --merge
```

## buyerの場合

```
/usr/bin/python3 pdf_to_csv_tabula.py ~/Downloads/drive-download-20251001T051013Z-1-001/buyer_2025.pdf -o out --outfile buyer_2025.csv -a "80,28,570,820" --mode stream --guess false --merge
```