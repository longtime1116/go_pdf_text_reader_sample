# 導入

```
brew install openjdk
echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME=$(/usr/libexec/java_home)' >> ~/.zshrc
. ~/.zshrc
```

# memo

sales_by_productの場合
/usr/bin/python3 pdf_to_csv_tabula.py "input.pdf" -o out -a "80,28,555,820" --mode stream --guess false
