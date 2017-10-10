% all units are in meters
speedOfSound = 1484;
ylim = 10;
xlim = 10;
zlim = 10; 
fprintf('Welcome to URC acoustic simulator.\nAll values should be input in metric units\n');

% matrix for doing math, lenght of vector greater than axis because it gets
% moved
% location of each hydrophone in 3d space, essentially the locaiton of the
% robot
cd = [0, 0, 0; 0, -.025, 0; .025, -.025, 0; .025, 0, 0];
% plotting the hydrophone locations
x = 1;
while x == 1
    % puts all plots on same plot
    xLoc = input('distance left (-) or right (+) of the robot (x): ');
    yLoc = input('distance in front of robot (y): ');
    zLoc = input('distance below the robot (z): ');
    fprintf('\n');
    fprintf('\n');
    pingerLoc = [xLoc, yLoc, -zLoc];
    %the number of pinger to alocate to find distance and toa easier
    [r, c] = size(cd);
    dist = ones(r, 1);
    for i = 1:r
        dist(i)  = sqrt(sum((cd(i,:) - pingerLoc).^2));
    end
    toa = dist./speedOfSound;
    x = 1;
    y = 2;
    z = 3;
    
    Rik = (signalToa2(toa(1) - toa(3))) * speedOfSound;
    Rij = (signalToa2(toa(1) - toa(2))) * speedOfSound;
    Rkj = (signalToa2(toa(3) - toa(2))) * speedOfSound;
    Rkl = (signalToa2(toa(3) - toa(4))) * speedOfSound;
    
    ji = cd(2,:) - cd(1,:);
    ki = cd(3,:) - cd(1,:);
    jk = cd(2,:) - cd(3,:);
    lk = cd(4,:) - cd(3,:);
    
    A = (Rik*ji(x) - Rij*ki(x))/(Rij*ki(y) - Rik*ji(y));
    B = (Rik*ji(z) - Rij*ki(z))/(Rij*ki(y) - Rik*ji(y));
    C = (Rik*(Rij^2 + sum(cd(1,:).^2 - cd(2,:).^2)) - Rij*(Rik^2 + sum(cd(1,:).^2 - cd(3,:).^2)))/(2*(Rij*ki(y) - Rik*ji(y)));
    
    
    D = (Rkl*jk(x) - Rkj*lk(x))/(Rkj*lk(y) - Rkl*jk(y));
    E = (Rkl*jk(z) - Rkj*lk(z))/(Rkj*lk(y) - Rkl*jk(y));
    F = (Rkl*(Rkj^2 + sum(cd(3,:).^2 - cd(2,:).^2)) - Rkj*(Rkl^2 + sum(cd(3,:).^2 - cd(4,:).^2)))/(2*(Rkj*lk(y) - Rkl*jk(y)));
    
    G = (E - B) / (A - D);
    H = (F - C) / (A - D);
    
    I = A*G + B;
    J = A*H + C;
    
    K = Rik^2 + sum(cd(1,:).^2 - cd(3,:).^2) + 2*ki(x)*H + 2*ki(y)*J;
    L = 2 * (ki(x)*G + ki(y)*I + 2*ki(z));
    
    M = 4*Rik^2 * (G^2 + I^2 + 1) - L^2;
    N = 8*Rik^2 * (G*(cd(1,x) - H) + I*(cd(1,y)-J) + cd(1,x)) + 2*L*K;
    O = 4*Rik^2 * ((cd(1,x)-H)^2 + (cd(1,y) - J)^2) - K^2;
    
    OutZ = N/(2*M) - sqrt((N/(2*M))^2 - O/M);
    OutX = G*OutZ + H;
    OutY = A*(OutX) + B*OutZ + C;
    

    fprintf('IN:    x = %2.2f y = %2.2f z = %2.2f\n', xLoc, yLoc, zLoc);
    fprintf('OUT:   x = %2.2f y = %2.2f z = %2.2f\n', OutX, OutY, -1 * OutZ);
    x = input('enter 1 to insert a new pinger location, enter 0 to quit: ');
end
