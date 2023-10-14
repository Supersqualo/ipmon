# ipmon
A Simple Multi IP Monitor.

## Descrizione
Software per monitorare uno o più host di rete, sia privati che pubblici, nel caso un IP cambia stato avvissa con un alert. Il tutto racchiuso in una pratica iconcina nella sistray.

## Come usare il software
1. pip install PyQt5
2. Modifica il file ipmon.ini che trovi nella stessa cartella 
3. python IPMon.py

## Come configurare ipmon.ini
1. IP=192.168.0.1;PC-DESK;www.google.it # Elenco IP da monitorare separati dal carattere ";" 
2. TIME=60000 # Tempo in millisecondi che deve trascorrere tra i check
3. PINGTIMEOUT=250 # Tempo massimo di attesa per la risposta del PING
4. NOTIFY=S # Se impostato a "S", nella sistray si avrà una notifica ad ogni cambio di stato di un IP monitorato

## Screenshot
![ipmon](Screenshot.png)

## Download
[Clicca qui](https://github.com/Supersqualo/ipmon/releases/latest) per scaricare l'ultima versione compilata!

## Author
Davide D'Amico - Pescara (https://www.novasoftonline.net)

## Grazie per aver provato il mio software
Riscontri qualche problema? Apri un [Caso](https://github.com/Supersqualo/ipmon/issues).
