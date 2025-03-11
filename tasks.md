#todo strona flask
1.strona glowna nawigacja ok

2. produkty ok 
3. rejestracja ok
3. logowanie ok
4. wylogowywanie ok
5. dashboard dla upowaznionych dodawnie/usuwanie/edycja itemu, lista itemow, ok , wyswietlanie zamowien OK
5. strona produktu opis fota cena przycisk doddaj do koszyka ile szt etc OK
6. koszyk jako zmienna w sesji ok
6. koszyk sumowanie ceny i ilosci OK
7. bramka platnosci
8. dane adresowe OK
9. panel admina do dodawania produktow widoczny tylko dla uzytkownikow z poziomem dostepu >1 ok
10. wyswietlanie zamowien , dodawanie/usuwanie przedmiotow OK

# cala baza danych jest ok

# bazy danych sqlite sqlachemy

# baza danych userow imie nazwisko email haslo poziom uprawnien zamowienia

# baza danych produktow nazwa opis zdjecie cena kategoria

# baza zamowien lista(przedmiotow sztuki jaki przedmiot) kiedy zlozono przez kogo i wysylka gdzie i forma platnosci , status zamowienia

# jeden user ma wiele zamowien

# jedno zamowienie ma wiele przedmiotow

# jedno zamowienie ma jednego usera

# jeden przedmiot nalezy do wielu  zamowien

Aby zliczyć liczbę powtórzeń elementów w liście w Pythonie, możesz użyć kilku metod. Oto kilka przykładów:

### 1. Korzystając z metody `count()`

Metoda `count()` pozwala zliczyć, ile razy występuje dany element w liście.

```python
lista = [1, 2, 3, 2, 1, 2]
liczba_powtorzen_2 = lista.count(2)
print(liczba_powtorzen_2)  # Wypisze: 3
```

### 2. Korzystając z `collections.Counter`

Jeśli chcesz zliczyć wszystkie powtórzenia wszystkich elementów w liście, najlepiej skorzystać z `Counter` z modułu
`collections`.

```python
from collections import Counter

lista = [1, 2, 3, 2, 1, 2]
liczba_powtorzen = Counter(lista)
print(liczba_powtorzen)  # Wypisze: Counter({2: 3, 1: 2, 3: 1})
```

### 3. Korzystając z pętli i słownika

Możesz także zliczyć powtórzenia ręcznie, używając słownika.

```python
lista = [1, 2, 3, 2, 1, 2]
powtorzenia = {}

for element in lista:
    if element in powtorzenia:
        powtorzenia[element] += 1
    else:
        powtorzenia[element] = 1

print(powtorzenia)  # Wypisze: {1: 2, 2: 3, 3: 1}
```

Każda z tych metod ma swoje zastosowanie w zależności od potrzeb. Jeśli zależy Ci na zliczeniu wszystkich powtórzeń,
`Counter` jest najwygodniejszym rozwiązaniem.


