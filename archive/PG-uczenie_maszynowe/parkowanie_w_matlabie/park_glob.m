function park_glob

global dt szer_park gleb_park szer_uli dl_uli szer_auta dl_auta odl_osi_prz odl_osi_tyl max_kat;

% wymiary w metrach
szer_park = 6.8;               % szerokosc miejsca do parkowania bocznego
gleb_park = 3.0;               % glebokosc miejsca parkowania bocznego
szer_uli = 8;
dl_uli = 26;                 % dlugosc odcinka ulicy 
szer_auta = 2.1;
dl_auta = 3.8;                  
odl_osi_prz = 1.2;           % odleglosc przedniej osi od zderzaka
odl_osi_tyl = 0.7;           % odleglosc tylniej osi od tylnego zderzaka 

dt = 0.1;                    % odstep czasu pomiedzy krokami w sekundach

max_kat = pi/4;              % maksymalny kat skretu kol w lewo lub w prawo

