K�dovanie: ISO-8859-2

Inform�cie k testovaciemu programu testOneMax
---------------------------------------------

Je pripraven� program testOneMax, ktor� implementuje rie�enie OneMax probl�mu so
zvolenou d�kou chromoz�mu.

Preklad programu:

make

Spustenie programu a n�poveda:

testOneMax -h

D�ku chromoz�mu je mo�n� nastavi� v zdrojovom programe testOneMax.cc,
nastaven�m premennej chrLength na po�adovan� hodnotu.

Popis vypracovania projektu pre predmet ARC/EVO
-----------------------------------------------

1. �vod

Pod�a �peci�lneho zadania bol implementovan� celul�rny model genetick�ho
algoritmu, ktor� pracuje paralelne. Bolo pou�it� rozhranie MPI, implementovan� v
MPICH.


2. Mapovanie na procesory

Pre mapovanie na procesory bolo pou�it� �achovnicov� mapovanie. Ka�d� procesor
vlastn� maticu jedincov. Napr�klad pre 9 procesorov dostaneme nasleduj�ce
rozdelenie:

         +--------------+
         | P0 | P1 | P2 |
         +----+----+----+
         | P3 | P4 | P5 |
         +----+----+----+
         | P6 | P7 | P8 |
         +----+----+----+

  Obr. 1: Mapovanie na procesory

Po�et procesorov je obmedzen� na mocninu 2, aby bolo mo�n� vytvori� rozumn�
mapovanie. Ve�kos� matice jedincov v genetickom algoritme v�ak nie je obmedzen�.
Ka�d� procesor takto vlastn� �as� glob�lnej mrie�ky jedincov.


3. Komunik�cia

V celul�rnom modele ka�d� jedinec komunikuje so svojimi susedmi z pevne
definovan�ho okolia. V paralelnej verzii je toto okolie obmedzen� na vzdialenos�
jedna (manhattan), t.j. jedinec si vyber� pre kr��enie v�dy svojich susedov
sprava, z�ava, zhora, alebo zdola. Prebiehaj� teda tieto typy komunik�cie:
 
 1. Vysladnie k �iadosti o chromoz�m k susedovi
 2. Pr�jem �iadosti o chromoz�m
 3. Reakcia na �iados� o chromoz�m od suseda -- preposlanie chromoz�mu
 4. Preposlanie v�sledkov evol�cie na lok�lnej mrie�ke hlavn�mu uzlu (rank 0),
    po skon�en� jednej gener�cie
 5. Preposlanie spr�vy z hlavn�ho uzlu v�etk�m ostatn�m procesorom s
    inform�ciou o �al�om pokra�ovan� evol�cie. S� tri mo�nosti: pokra�uj,
    koniec, po�li mi najlep�ieho jedinca.

Spr�vy 1. -- 3. prebiehaj� medzi susedn�mi uzlami a teda medzi susediacimi
procesormi. Spr�vy 4. a 5. prebiehaj� medzi hlavn�m procesorom a v�etk�mi
ostatn�mi procesormi.

Pre komunik�ciu boli pou�it� dve z�sady:
 
 1. Pr�jem spr�v je v�dy neblokuj�ci
 2. Vysielanie spr�v je blokuj�ce,

a to z toho d�vodu, �e ak by obidve varianty boli blokuj�ce mohlo by doch�dza� k
deadlocku. Napr�klad v pr�pade pod�a obr. 1 je mo�n�, �e procesory P1, P2, P4, a
P5 vytvoria cyklus �iadost� o jedinca: P1 --> P2 --> P5 --> P4 --> P1. Ak na
procesoroch nebol pred vyslan�m �iadosti o chromoz�m u� dopredu spusten�
neblokuj�ci pr�jem tejto �iadosti, do�lo by k deadlocku.

D�sledkom tohoto syst�mu s� dve veci:

 1. Ka�d� procesor mus� po�as vykon�vania genetick�ho algoritmu sledova� pr�jem
    �iadost� (pr�jem je za�at� pri �tarte lok�lnej verzie) od svojich
    susedov a v pr�pade po�iadavky na chromoz�m tento chromoz�m vysla� k
    susedovi.
 2. Procesor, ktor� po�aduje nejak� chromoz�m od svojho suseda, mus� pred
    vyslan�m po�iadavky za�a� neblokuj�ci pr�jem chromoz�mu a n�sledne v
    akt�vnej smy�ke testova� vybavenie �iadosti. V akt�vnej smy�ke �alej mus�
    procesor testova� aj �iadosti od ostatn�ch procesorov.

T�mto sp�sobom sa zabr�ni deadlocku pri komunik�cii medzi procesormi. Nev�hodou
je v�ak, �e pri spusten� paralelnej verzie na jednoprocesorovom syst�me
doch�dza k nadmern�mu za�a�eniu procesoru pri akt�vnom �akan�, �o brzd� ostatn�
procesy vo vykon�van� programu. Takto je mo�n� v celom syst�m pozorova�
spomalenie oproti sekven�nej verzii.

Pri spusten� na viacer�ch procesoroch v�ak doch�dza k zr�chleniu a pri testovan�
som ani raz nepozoroval spomalenie.


4. Nameran� v�sledky

V arch�ve je pripraven� skript ARCtest.sh, ktor� spust� nieko�kokr�t genetick�
algoritmus pod�a zadan�ch parametrov. V�sledkom je tabu�ka obsahuj�ca po�et
procesorov, �as v�po�tu, zr�chlenie a efektivitu v�po�tu. Pred spusten�m skriptu
je nutne spr�vne nastavi� pr�va a parametre skriptu mpi.

Algoritmus som testoval na dvoch variant�ch, s pou�it�m jednoduch�ho probl�mu
OneMax:

 1. 
   chromosomeLength=350 (d�ka chromoz�mu v bitoch)
   xsize=300 ysize=300 gen=100 NUM_PROCS="1 4 9 16 25 36" ./ARCtest.sh

   #Processors     Time [s]     Speedup         Effectivity
   1               815.156      1.00000         1.00000
   4               254.035      3.20883          .80220
   9               129.181      6.31018          .70113
   16              183.881      4.43306          .27706
   25              119.365      6.82910          .27316
   36              65.7563      12.39662         .34435

 2.
   chromosomeLength=500
   xsize=600 ysize=600 gen=50 NUM_PROCS="1 4 9 16 25 36" ./ARCtest.sh

   #Processors/cores       Time [s]        Speedup         Effectivity
   1                       2320.6         1.00000         1.00000
   4                       652.631        3.55576         .88894
   9                       366.246        6.33617         .70401
   16                      329.66         7.03937         .43996
   25                      184.991        12.54439        .50177
   36                      156.4          14.83759        .41215


Je vidie�, �e s rast�cim po�tom procesorov kles� efektivita paraleln�ho
spracovania k nule. Predpoklad�m, �e je to sp�soben� komunik�ciou medzi
procesormi a akt�vnym �akan�m pri neblokuj�com spracovan� spr�v.
