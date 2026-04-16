# github-pr-extractor
Acest script Python a fost creat pentru a extrage automat informații detaliate despre Pull Requests (PR) din repozitoarele GitHub și pentru a le salva într-un fișier CSV.
Include un sistem de protecție împotriva limitelor API. Deoarece GitHub permite maxim 5.000 de cereri pe oră pentru un token standard, scriptul monitorizează constant numărul de cereri rămase. Când se apropie de limită, intră automat pe pauză, așteaptă resetarea limitelor de pe server și își reia activitatea, permițând astfel extragerea volumelor mari de date fără ca programul să se oprească cu eroare.

### Cum se utilizează

Scriptul se rulează din linia de comandă, oferind ca argumente repozitoarele pe care dorești să le analizezi, urmate de stadiul PR-urilor dorite (all, open sau closed).

### Sintaxa de bază
`python extragere.py <utilizator>/<proiect>:<stare>`


### Exemple de rulare

#### 1. Extragerea completă a unui singur repozitoriu
   
`python extragere.py <nume_utilizator>/<nume_repo>:all`

#### 2. Procesarea simultană a mai multor repozitoare
  
`python extragere.py <utilizator1>/<repo1>:open <utilizator2>/<repo2>:closed`
