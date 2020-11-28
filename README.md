# Изменение лица повествования

В файле text_processor.py находится класс для обработки текста

## Установка необходимых библиотек

```bash
# Если хотите использовать исправление опечаток:

sudo apt install swig3.0
pip3 install -r requirements.txt
```

## Использование класса обработки текста

```python
text_processor = TextProcessor()
result = text_processor.process('я увидел')
print(result)

# на выходе будет "он увидел"
```
