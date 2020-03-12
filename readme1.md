Implementační dokumentace k 1. úloze do IPP 2019/2020<br>
Jméno a příjmení: Richard Klem<br>
Login: xklemr00
##Knihovny
Použil jsem třídu XMLWriter z modulu _xmlwriter.php_ pro vytváření a manipulaci s xml objekty.
##Členění kódu a funkce
Funkce _get_type_and_value()_ zpracovává argumenty operačních kódů a kontroluje jejich správnost.

Funkce _too_many_args()_ kontroluje správný počet argumentů.

V hlavním těle kódu se postupně načítají řádky vstupního souboru a pomocí výše<br>
uvedených funkcí se kontroluje jejich lexikální a syntaktická správnost.<br>
V případě chyby se navrátí patřičný návratový kód skriptu.<br>
V případě, že vše proběhlo jak mělo, se vypíše xml reprezentace na stdout.