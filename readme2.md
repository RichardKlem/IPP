Implementační dokumentace k 2. úloze do IPP 2019/2020<br>
Jméno a příjmení: Richard Klem<br>
Login: xklemr00
#1) interpret.py
##1.1) Knihovny
`argparse` pro parsování argumentů skriptu<br> 
`re` pro práci s regulárními výrazy<br>
`sys` pro práci se stdin/out/err, argumenty a spuštění skriptu<br>
`xml.etree.ElementTree` pro parsování vstupního XML a objektovou práci s XML<br>
##1.2) Moduly a členení
Část interpretu se skládá ze tří modulů: `interpret.py`, `constants.py`<br>
 a `instruction_methods.py`.
###1.2.1) Modul constants.py
V tomto modulu jsou uskladněny konstanty, ať už jako seznamy nebo slovníky.<br>
Tím, že jsou konstanty odděleny od zbytku kódu, jsou dostupné a importovatelné<br>
tam, kde je zrovna třeba a omezí se redundance kódu a tím pádem i chyb.
###1.2.2) Modul instruction_methods.py
V tomto modulu jsou umístěny funkce, které implementují chování jednotlivých<br>
instrukcí. Pro každou instrukci je jedna funkce. Navíc jsou zde dvě pomocné funkce.<br>
A to `var_prepare()` a `replace_escape_sequences()`. `var_prepare()` se používá<br>
když očekáváme proměnnou jako první argument instrukce, na vstupu přijímá<br>
objekt Element třídy ElementTree obsahující informace o instrukci, <br>
na výstup pak vrací dvojici _var_frame_, _var_name_ představující rámec, v kterém se<br>
proměnná nachází a název proměnné. Funkce `replace_escape_sequences()` nahradí escape<br>
sekvence v textu za patřičný znak dle specifikace v zadání.
Oddělením instrukcí od zbylého kódu do vlastního modulu vede opět k větší přehlednosti<br>
v hlavním modulu skriptu.
###1.2.3) Modul interpret.py
Toto je hlavní modul skriptu. Zde dochází ke čtení vstupního XML souboru.<br>
V modulu je implementována **třída `Interpret`**. Její instance nese řadu atributů<br>
(např. _input_data_ pro vstupní data určené jako vstup pro interpretaci,<br>
slovník _global_frame_ sloužící jako slovník globálních proměnných nebo _data_stack_,<br>
který slouží pro data zásobníkových instrukcí).<br>
Dále třída obsahuje několik metod, některé jsou statické. Metody jsou popsány<br>
v daném modulu, za zmínku zde stojí metoda `inst2method()`, která obratně<br>
využívá faktu, že i funkce a metody jsou v Python3 objektem a tudíž se používá slovník,<br>
ve kterém jsou klíče řetězce s názvem instrukce a hodnoty jsou příslušné funkce z modulu<br>
`instructio_methods.py`. Díky této metodě není za potřebí neúnosně dlouhého<br>
výrazu _if-elif-...-elif-else_ a pro každou instrukci se zavolá tato metoda, která<br>
získá patřičnou funkci reprezentující funkcionalitu dané instrukce.<br>
Samotné interpretování obstarává metoda `interpret()`.
##1.3) Průběh skriptu
Nejprve se načtou a zpracují argumenty z příkazové řádky. Pokud jsou splněny<br>
formální požadavky na kombinace argumentů apod., je vytvořena instance třídy<br>
`Interpret` a je zavolána metoda `interpret()`.

Poté se čte vstupní XML. K tomu je využívaná třída `ElementTree` a její<br>
metody z modulu `xml.etree.py`. Nyní mám k dispozici strom Elementů. Pro další<br>
zpracování bylo nutné si XML seřadit podle atributu instrukce _order_.<br>
K tomu jsem využil vestavěné metody `sorted`, které jsem předal jako argument _key_<br>
funkci _lambda_, která z instrukce získávala právě atribut _order_.

Dále se v jednoduchém for cyklu iteruje přes všechny instrukce a kontroluje se,<br>
zda splňují všechny formální požadavky. Zároveň se řadí opět pomocí _lambda_ funkce<br>
atributy instrukcí. K tomu se ještě zjišťují a kontrolují všechna návěští a ukládají<br>
se do instanční proměnné _label_dict_.

Následuje cyklus _while_, který bylo nutné použít kvůli možným skokům<br>
v interpretovaném programu. Python bohužel nedisponuje "klasickým" _for_ cyklem,<br>
ale pouze "_for each_" cyklem.<br>
Jednotlivé instrukce provádí různé operace podle specifikace v zadání.

#2) test.php
##2.1) Knihovny
Ve skriptu `test.php` jsem využil pouze vestavěných funkcí.
##2.2) Moduly a členění
Skript `test.php` je samostatným skriptem, nemá žádné moduly.
##2.3) Průběh skriptu
Nejprve se načtou argumenty z příkazové řádky a zkontrolují formální požadavky na ně.<br>
Poté se projde adresář s testy, rekurzivně nebo pouze na první úrovni, a naplní se<br>
pole patřičnými názvy souborů. V případě, že nějaký chybí, tak se vytvoří dle specifikace<br>
v zadání.

Následuje již přímo samotné testování, podle režimu, který je zvolen pomocí parametrů,<br>
se buď provádí pouze testování parseru anebo pouze testování interpretu anebo testování<br>
nejprve parseru a jeho XML výstup se použije jako vstup pro interpret.<br>
V každé jedné iteraci nad testovacími soubory se provede i kontrola správnosti výstupu.<br>
XML výstup z parseru se porovnává oproti referenčnímu pomocí nástroje _JExamXML_. Výstup<br>
z interpretu se porovnává pomocí unixového nástroje _diff_.

Na základě výsledků z testu se generuje patřičný záznam do HTML výstupu.<br>
Samotný HTML výstup je strukturován do tabulky s jednoduchým barevným odlišením testů,<br>
které prošly a které ne a jsou vypsány základní informace o testu.