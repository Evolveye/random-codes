% Wyznaczanie polozenia naroznikow samochodu na podstawie srodka pomiedzy osiami
% oraz kata ustawienia

function [X,Y] = narozniki_kol(hist)

global dt szer_park gleb_park szer_uli dl_uli szer_auta dl_auta odl_osi_prz odl_osi_tyl;

xs = hist(1); ys = hist(2); alfa = hist(3); beta = hist(4);

% roznica pomiedzy srodkiem geometrycznym a srodkiem pomiedzy osiami:
ds = (odl_osi_prz - odl_osi_tyl)/2;

% x,y - wspolrzedne srodka pomiedzy osiami auta wzgledem polozenia docelowego (x=0,y=0 w srodku miejsca parkingowego):
x = xs - ds*cos(alfa);
y = ys - ds*sin(alfa); 

d_osi = dl_auta - odl_osi_prz - odl_osi_tyl;           % odleglosc pomiedzy osiami

Rk = odl_osi_tyl*0.9;           % promien kola
szer_k = Rk*0.6;                % szerokosc kola 

% polozenie punktow A,B,C,D dla kola A:
xA = x - (d_osi/2 + Rk)*cos(alfa) - (szer_auta/2 - 1.2*szer_k/2)*sin(alfa);
yA = y + -(d_osi/2 + Rk)*sin(alfa) + (szer_auta/2 - 1.2*szer_k/2)*cos(alfa);

xB = xA + szer_k*sin(alfa);
yB = yA - szer_k*cos(alfa);

xD = xA + Rk*2*cos(alfa);
yD = yA + Rk*2*sin(alfa);

xC = xB + Rk*2*cos(alfa);
yC = yB + Rk*2*sin(alfa);

X(:,1) = [xA xB xC xD]';
Y(:,1) = [yA yB yC yD]';

% kolo B:
X(:,2) = X(:,1) + (szer_auta - szer_k - szer_k*1.2)*sin(alfa);
Y(:,2) = Y(:,1) - (szer_auta - szer_k - szer_k*1.2)*cos(alfa);

% kolo C:
XX = X(:,1) + d_osi*cos(alfa);
YY = Y(:,1) + d_osi*sin(alfa);

xr = (XX(1) + XX(3))/2;
yr = (YY(1) + YY(3))/2;

U = XX' - xr;
W = YY' - yr;

Z = [XX';YY'] + [cos(beta)-1  -sin(beta); sin(beta) cos(beta)-1] * [U;W];
X(:,3) = Z(1,:)';
Y(:,3) = Z(2,:)';


% kolo D:
X(:,4) = X(:,3) + (szer_auta - szer_k - szer_k*1.2)*sin(alfa);
Y(:,4) = Y(:,3) - (szer_auta - szer_k - szer_k*1.2)*cos(alfa);

