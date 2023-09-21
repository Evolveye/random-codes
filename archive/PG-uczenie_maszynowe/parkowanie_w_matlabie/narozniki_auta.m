% Wyznaczanie polozenia naroznikow samochodu na podstawie srodka pomiedzy osiami
% oraz kata ustawienia

function [X,Y] = narozniki_auta(stan)

global dt szer_park gleb_park szer_uli dl_uli szer_auta dl_auta odl_osi_prz odl_osi_tyl;

x = stan(1); y = stan(2); alfa = stan(3);

xA = x - dl_auta/2*cos(alfa) - szer_auta/2*sin(alfa);
yA = y - dl_auta/2*sin(alfa) + szer_auta/2*cos(alfa);

xB = xA + szer_auta*sin(alfa);
yB = yA - szer_auta*cos(alfa);

xD = xA + dl_auta*cos(alfa);
yD = yA + dl_auta*sin(alfa);

xC = xB + dl_auta*cos(alfa);
yC = yB + dl_auta*sin(alfa);

X = [xA xB xC xD];
Y = [yA yB yC yD];

