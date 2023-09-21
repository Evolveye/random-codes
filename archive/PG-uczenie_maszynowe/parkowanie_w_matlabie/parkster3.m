% SYMULACJA SAMOCHODU - sterowanie reczne lub rozmyte
clear;
park_glob;  % zmienne globalne
global dt szer_park gleb_park szer_uli dl_uli szer_auta dl_auta odl_osi_prz odl_osi_tyl max_kat;

% Parametry zadania:
max_liczba_krokow = 350;                 % liczba krokow, po przekroczeniu ktorej jazda jest przerywana
Vmod = 2;     % modul predkosci pojazdu (im wiekszy, tym wieksze odleglosci przejezdzane pomiedzy krokami sterowania: S = Vdt)

liczba_stanow_pocz = 10;
czy_rownolegle_do_x = 0;
  
% losowanie dowolnego polozenia pojazdu:
st = 0;
while st <  liczba_stanow_pocz
    gora = rand < 0.5;
    if gora
        stan_los = [-dl_uli/2,szer_auta/2, -pi] + rand(1,3).*[dl_uli,szer_uli,2*pi];
    else
        stan_los = [-szer_park/2,-(gleb_park-szer_auta)/2, -pi] + rand(1,3).*[szer_park,gleb_park,2*pi];
    end
    
    if czy_rownolegle_do_x
        stan_los(3) = (abs(stan_los(3)) > pi/2)*pi;
    end
    
    % 2. Wyznaczenie polozenia naroznikow samochodu oraz naroznikow parkingu 
    [X,Y] = narozniki_auta(stan_los);
    
    % Narozniki parkingu (wspolrzedne punktow w kolejnych kolumnach):
    Xp = [-szer_park/2, szer_park/2]; 
    Yp = [szer_auta/2, szer_auta/2]; 
    % W - Czy narozniki auta nie przekroczyly granic parkingu  
    W = (X >= -dl_uli/2)&(X <= dl_uli/2)&(Y <= szer_uli+szer_auta/2)& ...
        ((Y >= szer_auta/2)|((Y >= szer_auta/2-gleb_park)&(X >= -szer_park/2)&(X <= szer_park/2)));
    
    % Wp - Czy naroznik parkingu nie znajduje sie 'wewnatrz' auta    
    for i=1:length(Xp)
        v_kr = [X([2:end 1]) - X;Y([2:end 1]) - Y];               % wektory krawedzi auta ( w kolumnach)
        v_pkt = [Xp(i) - X;Yp(i) - Y];                            % wektory od wierzcholkow auta do punktu (xp,yp)
        ilo_weks = cross([v_kr;zeros(1,4)],[v_pkt;zeros(1,4)]);   % iloczyny wektorowe v_kr(j) x v_pkt(j)
        Wp(i) = (sum(ilo_weks(end,:) > 0) < 4);                   % jesli wszystkie dodatnie, to znaczy ze punkt lezy wewnatrz auta 
        suma(i) = sum(ilo_weks(end,:)); 
    end
    
    if (sum(~W) <= 0)&&(sum(~Wp) <= 0)           % nie ma przeszkod - akceptacja stanu
        st = st+1;
        stany_pocz(st,:) = stan_los;
    end
end

                     
          
czas_pauzy = 0.1;              % czas pauzy pomiedzy krokami sterowania. Jesli == dt, to symulacja w czasie rzeczywistym      
typ_ster = 'rozmyte';     % {'reczne'  'rozmyte'  'neuro' }
% kazdy stan opisany przez trojke [x,y, kat polozenia samoch wsg. osi ox]
liczba_stanow_pocz = length(stany_pocz(:,1))                         

%stany_pocz = stany_pocz + (2*rand(size(stany_pocz))-1).*repmat([0.1 0.1 0.02],liczba_stanow_pocz,1);  % szum 

if strcmp(typ_ster,'rozmyte')
    fis = readfis('moj.fis');                            % odczyt systemu rozmytego z pliku
elseif strcmp(typ_ster,'neuro')
    load net_max;                                   % wczytanie sieci neuronowej jako funkcji sterowania
    net = net_max;
end

V_konc = [];
ilosc_konc = [];
krok_konc = [];
historia = [];
zapis_historii = false;

% Wstepne ustawienia okna animacji:
f = figure;                                                  % stworzenie obiektu typu figure
prop = (gleb_park+szer_uli)/dl_uli;                          % proporcje wysokosci do szerokosci
ekran = get(0,'screensize');                                 % rozmiary ekranu
set(f,'Position',[1 100 ekran(3)*0.95 1.4*ekran(3)*prop*0.95]);     % ustawienie pozycji oraz rozmiarow okna rysunku
gca1 = axes('Position',[0.02 1-1/1.4+0.025 0.98 1/1.4-0.025]);                        % poczatek oraz wymiary okienka rysowania wewnatrz okna figure

set(f,'Resize','off');                                       % zablokowanie zmiany wymiarow okna figure 
set(f,'name','Sterowanie parkujacym pojazdem');
set(gca1,'Color',[0.3,0.7,0.9]);                              % kolor tla  
set(gcf, 'SelectionType','open');

axis([-dl_uli/2  dl_uli/2  szer_auta/2-gleb_park  szer_auta/2+szer_uli]*1.05);  % podzialka na osiach wspolrzednych
patch([-dl_uli/2 -szer_park/2, -szer_park/2, szer_park/2, szer_park/2, dl_uli/2, dl_uli/2, -dl_uli/2],... %kontur parkingu
    [szer_auta/2, szer_auta/2, szer_auta/2-gleb_park, szer_auta/2-gleb_park, ...
        szer_auta/2, szer_auta/2, szer_uli+szer_auta/2, szer_uli+szer_auta/2],[0.3 0.3 0.3], 'erasemode','xor');
patch([-dl_auta/2 dl_auta/2 dl_auta/2 -dl_auta/2],[szer_auta/2 szer_auta/2 -szer_auta/2 -szer_auta/2], ... % miejsce postoju
    [0.2 0.2 0.2], 'erasemode','xor');
patch([-dl_auta/2 dl_auta/2 dl_auta/2 -dl_auta/2],[szer_auta/2 szer_auta/2 -szer_auta/2 -szer_auta/2], ... % miejsce postoju
    [0.1 0.1 0.1], 'erasemode','xor');
text(szer_park/2 + 0.2,szer_auta/2 - 0.2,'Obsluga klawiszy w ster. recznym:');
text(szer_park/2 + 0.2,szer_auta/2 - 1.0,'Spacja: start symulacji');
text(szer_park/2 + 0.2,szer_auta/2 - 1.5,'Mysz - lewy: koniec parkowania');
text(szer_park/2 + 0.2,szer_auta/2 - 2.0,'Mysz - srodkowy: koniec parkowania + zapis jazdy');
text(szer_park/2 + 0.2,szer_auta/2 - 2.5,'Mysz - prawy: zatrzymanie pojazdu');

gca2 = axes('Position',[0.25 0 0.5 1-1/1.4]);
subplot(gca2);
%axis([0 0 1 1]);
patch([0 0.5 0.5 0],[1 1 0.5 0.5],[0.4 0.1 0.4],'erasemode','xor');
patch([0.5 1 1 0.5],[1 1 0.5 0.5],[0.6 0.1 0.6],'erasemode','xor');
patch([0 0.5 0.5 0],[0.5 0.5 0 0],[0.3 0.7 0],'erasemode','xor');
patch([0.5 1 1 0.5],[0.5 0.5 0 0],[0.4 0.8 0],'erasemode','xor');
text(0.45, 0.75, 'Do przodu');
text(0.45, 0.25, 'Do tylu');
text(0.25, 0.50, 'W lewo');
text(0.75, 0.50, 'W prawo');

subplot(gca1);
[X,Y] = narozniki_auta(stany_pocz(1,:));
id_auto = patch(X,Y, 'g', 'erasemode','xor');
[X,Y] = narozniki_kol([stany_pocz(1,:) 0]);
id_kola = patch(X,Y, 'black', 'erasemode','xor'); % rysowanie kol
for st=1:liczba_stanow_pocz                      % po stanach poczatkowych
   stan = stany_pocz(st,:)
   krok = 1;
   historia = [];
   koniec = false;
   
   x = stan(1); y = stan(2); alfa = stan(3);
   [X,Y] = narozniki_auta([x y alfa]);
   set(id_auto,'xdata', X, 'ydata', Y);           % poczatkowe polozenie karoserii
   [X,Y] = narozniki_kol([x y alfa 0]);
   set(id_kola,'xdata', X, 'ydata', Y);           % poczatkowe polozenie kol
   
   set(gcf, 'SelectionType','open');                 % ustawienie klawisza myszy 
   stop = false;                                     % zatrzymanie pojazdu
   disp('wcisnij spacje ...');          
   pause
   while (~koniec)     % po krokach czasowych 
      %x = stan(1);
      %y = stan(2);
      %alfa = stan(3);
      
      if strcmp(typ_ster,'reczne')
          Po = get(gcf, 'Position');              % pozycja i rozmiary biezacego okna na ekranie
          Pm = get(0,'PointerLocation');          % polozenie wskaznika myszy na calym ekranie
          Pog2 = get(gca2,'Position');              % pozycja i rozmiary okienka myszowego 
          % wspolrzedne wskaznika myszy jak proporcje wewnatrz okna figure:
          a = ((Pm(1) - Po(1))/Po(3)-Pog2(1))/Pog2(3);
          b = (Pm(2) - Po(2))/Po(4)/Pog2(4);
          if b > 0.5
              V = Vmod;
          else 
              V= -Vmod;
          end
          if stop
              V = 0;
          end
              
          kat = -max_kat*(a-0.5)*2;
          
          button = get(gcf, 'SelectionType');   % typ klawisza: 'normal', 'extend' lub 'alt', ('open' - podwojne szybkie klikniecie)      
          if strcmp(button,'alt')               % zatrzymanie pojazdu
              stop = 1-stop;
              set(gcf, 'SelectionType','open');
          end
          if strcmp(button,'normal')            % koniec symulacji
              koniec = true;
              set(gcf, 'SelectionType','open');
          end
          if strcmp(button,'extend')            % koniec symulacji + zapis do pliku
              koniec = true;
              zapis_historii = true;
              set(gcf, 'SelectionType','open');
          end
      elseif strcmp(typ_ster,'rozmyte')
          wynik = evalfis(stan,fis);    % wyznaczenie kata skretu oraz predkosci (do przodu lub do tylu) 
          kat = wynik(1);
          if (abs(wynik(2)) < 0.15)
              V = 0;
          else
              V = Vmod*sign(wynik(2));
          end
      elseif strcmp(typ_ster,'neuro')
          wy = sim(net,stan');
          kat = max_kat*wy(1);
          if (abs(wy(2)) < 0.15)
              V = 0;
          else
              V = Vmod*sign(wy(2));
          end          
      end
      
      if (abs(kat) > max_kat)
          kat = sign(kat)*max_kat;
      end
      
      stan_n = samochod(stan,kat,V);           % wyznaczenie nowego stanu po pewnym interwale czasowym                
      historia(krok,:) = [stan kat V];         % zapis biezacego stanu + proponowanej sily ciagu (nie musi taka byc)
      
      if (strcmp(typ_ster,'reczne')==0)&((V==0)|...
              (krok >= max_liczba_krokow)|...
              (sum(stan ~= stan_n)==0))      % koniec jesli zatrzymanie pojazdu lub przekr. max. liczba krokow
          koniec = true;                                               % lub nastepny stan taki sam jak poprzedni
      end
      
      [X,Y] = narozniki_auta(stan_n);
      set(id_auto,'xdata', X, 'ydata', Y);           % nowe polozenie konturu auta
      [X,Y] = narozniki_kol([stan_n kat]);
      set(id_kola,'xdata', X, 'ydata', Y);           % nowe polozenie kol
      drawnow;
      pause(czas_pauzy);
      
      stan = stan_n;
      krok = krok+1;    
   end  % while - po krokach czasowych 
      
   historia(krok,:) = [stan kat V];
   if zapis_historii
       bez_postojow = find(historia(:,5)~=0);
       historia = [historia(bez_postojow,:) ; historia(end,:)];        % usuniecie postojow
       licz_krok_histo = length(historia(:,1));
       f = fopen('historia.txt','a');
       fprintf(f,'\n%s x = %f   y = %f   kat = %f  kat_skretu=0 V=0\n','% stan poczatkowy:',stany_pocz(st,1),stany_pocz(st,2),stany_pocz(st,3));  
       for i=1:licz_krok_histo
          fprintf(f,'%s\n',num2str(historia(i,:)));
       end   
       fclose(f);
       zapis_historii = false;
   end
   
   % Ocena parkowania zalezy od polozenia srodka pojazdu wzgledem srodka
   % miejsca parkingowego, kata ustawienia pojazdu (jak najblizej 0 lub 180
   % stopni) oraz calkowitej drogi pokonanej przez pojazd w stosunku do
   % odleglosci w linii prostej
   ocena_miejsca = 1/(0.1 + sqrt(sum(historia(end,[1 2]).^2)^3)); 
   ocena_rown = 1/(0.1 + 50*min(abs(historia(end,3)), abs(abs(historia(end,3)) - pi) )^3);
   ocena_czasu = sqrt(sum(historia(1,[1 2]).^2))/(sum(abs(historia(:,5))*dt) + sqrt(sum(historia(1,[1 2]).^2)));
   ocena(st) = ocena_miejsca*ocena_rown;
   odleglosc = sqrt(sum(historia(end,[1 2]).^2));
   kat_ust_kol = historia(end,3);
   
   lan = sprintf('odl = %f, alfa = %f, ocena = %f',odleglosc,kat_ust_kol,ocena(st));
   disp(lan)
   subplot(gca1);
   t1 = text(-dl_uli/2,0,lan);
   t2 = text(-dl_uli/2,-1,'symulacja zakonczona, wcisnij spacje ...');
   pause
   delete(t1);delete(t2);
   
   %delete(id_auto);delete(id_kola); 
end    % po stanach poczatkowych 
ocena_konc = sum(ocena.^-0.5)^-2

delete(id_auto);delete(id_kola);
close
