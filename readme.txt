1. Ergänze Client Secret und Client ID von der Spotify for Developers Seite all nicht vorhanden. 
ID und Secret Account und der Account, der zum Anmelden genutzt wird, muss der selbe sein.

2. Öffne ein CMD Fenster und gib den Befehl "ssh -R technikag:80:127.0.0.1:5000 -i [Pfad] -o ServerAliveInterval=6000 serveo.net" ein. 
Ersetzte [Pfad] mit dem Pfad von deinem ssh rsa key oder so in der Art. (Maybe in /new ?)

3. Bei allen weiteren Aktionen wird sich der Browser öffnen und du musst dich womöglich bei Spotify anmelden, aber dann nicht mehr. 
Dann wirst du auf Google weitergeleitet. Du musst nun die gesamte URL mit STRG V oder STRG SHIFT V einfügen.

4. Öffne ein weiteres CMD Fenster in "/Flask Server" und starte den Server mit "py server.py".

5. Wenn du willst, kannst du auch das Admin Interface oder das User Interface mit "py interface.py" oder "py user_self.py" starten. 
Wenn dieses Program auf einem anderen Computer laufen soll, dann muss man die IPv4 Adresse mit "ipconfig" auf dem Server Computer ermitteln und "127.0.0.1" in dem Programm durch die IP ersetzten.