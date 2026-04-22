% Beam deflection calculator
% Simply supported beam, point load at midspan
% Haripriya B, SSN College of Engineering

L = 5;        % beam length (m)
P = 10000;    % load (N)
E = 200e9;    % Young's modulus (Pa)
I = 100e-8;   % Second moment of area (m^4)

x = linspace(0, L, 500);
delta = (P.*x)./(48*E*I) .* (3*L^2 - 4*x.^2);