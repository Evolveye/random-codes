% model poruszania sie samochodu ze skreconymi przednimi kolami z mala
% predkoscia. Na wejsciu stan, kat skretu kol wzgledem osi pojazdu
% oraz predkosc (dodatnia do przodu, ujemna do tylu), na wyjsciu nowy stan po czasie dt 

function [stann, Sobr] = samochod(stan,kat,V)

global dt szer_park gleb_park szer_uli dl_uli szer_auta dl_auta odl_osi_prz odl_osi_tyl max_kat;

liczba_iteracji = 5;        % liczba przyblizen jesli pojazd trafi na przeszkode (im wiecej, tym dokladniej)
if (abs(kat) > max_kat)
    kat = sign(kat)*max_kat;
end

stan_pocz = stan;
koniec = false;
iter = 1;
while (~koniec)
    xs = stan_pocz(1);             % wspolrzedne srodka geometrycznego pojazdu
    ys = stan_pocz(2);
    alfa = stan_pocz(3);          % alfa - kat ustawienia auta, alfa = 0, gdy os auta || do osi x oraz przod w kierunku x.  
    
    % roznica pomiedzy srodkiem geometrycznym a srodkiem pomiedzy osiami:
    ds = (odl_osi_prz - odl_osi_tyl)/2;
    
    % x,y - wspolrzedne srodka pomiedzy osiami auta wzgledem polozenia docelowego (x=0,y=0 w srodku miejsca parkingowego):
    x = xs - ds*cos(alfa);
    y = ys - ds*sin(alfa); 
    
    % 1. Wyznaczenie nowego polozenia srodka prostokata pomiedzy osiami samochodu:                          
    d_osi = dl_auta - odl_osi_prz - odl_osi_tyl;           % odleglosc pomiedzy osiami
    if (abs(kat) < 1e-6)
        xn = x + V*dt*cos(alfa);  
        yn = y + V*dt*sin(alfa);  
        alfan = alfa;
    else
        a = d_osi/tan(kat);
        Ro = sqrt(d_osi*d_osi/4 + (abs(a) + szer_auta/2)^2);        % promien obrotu
        tau = sign(kat)*alfa + asin(d_osi/2/Ro);
        Sobr = [x-Ro*sin(tau) y+sign(kat)*Ro*cos(tau)] ;            % srodek obrotu
        gama = V*dt/Ro;                                             % kat obrotu
        xn = x + Ro*(sin(gama + tau) - sin(tau));              
        yn = y + sign(kat)*Ro*(cos(tau) - cos(gama+tau));
        alfan = alfa + sign(kat)*gama;
        if abs(alfan) > pi
            alfan = alfan - sign(alfan)*pi*2;
        end
    end
    xsn = xn + ds*cos(alfan);                            % nowe polozenie srodka geometrycznego 
    ysn = yn + ds*sin(alfan);
    stann = [xsn ysn alfan];                             % nowy stan 
    
    % 2. Wyznaczenie polozenia naroznikow samochodu oraz naroznikow parkingu 
    [X,Y] = narozniki_auta(stann);
    
    % Narozniki parkingu (wspolrzedne punktow w kolejnych kolumnach):
    %Xp = [-dl_uli/2 -szer_park/2, -szer_park/2, szer_park/2, szer_park/2, dl_uli/2, dl_uli/2, -dl_uli/2]; 
    %Yp = [szer_auta/2, szer_auta/2, szer_auta/2-gleb_park, szer_auta/2-gleb_park, ...
    %                 szer_auta/2, szer_auta/2, szer_uli+szer_auta/2, szer_uli+szer_auta/2];
    % tylko wystajace:
    Xp = [-szer_park/2, szer_park/2]; 
    Yp = [szer_auta/2, szer_auta/2]; 
    
    % 3. Sprawdzenie, czy samochod nie zahacza o przeszkode. Jesli tak, to
    %    cofniecie do momentu zahaczenia:
    
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
    
    if (sum(~W) > 0)|(sum(~Wp) > 0)           % wykryto przeszkode
        stann = stan_pocz;
        V = V/2;
    elseif iter > 1                           % nie ma przeszkody, ale byla po pokonaniu dluzszej drogi 
        stan_pocz = stann;
        V = V/2;
    else                                      % nie ma przeszkody
        koniec=true;
    end    
    
    if (iter >= liczba_iteracji)
        koniec = true;
    end
    iter = iter+1;
end % po iteracjach gdy pojazd trafi na przeszkode