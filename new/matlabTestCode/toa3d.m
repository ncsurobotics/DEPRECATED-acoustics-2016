% all units are in meters
SpeedOfSound = 1484;
ylim = 10;
xlim = 10;
zlim = 10; 
fprintf('Welcome to URC acoustic simulator.\nAll values should be input in metric units\n');

% matrix for doing math, lenght of vector greater than axis because it gets
% moved
% location of each hydrophone in 3d space, essentially the locaiton of the
% robot
cd = [0, 0, -.3; 0, .019, -.3; .019/2, .1, -.3; -.019/2, .1, -.3];
% plotting the hydrophone locations
x = 1;

while x == 1
    % puts all plots on same plot
    hold on
    grid on
    plot3(cd(:, 1), cd(:, 2), cd(:, 3), 'b*');
    % setting the axis limits
    axis([-xlim, xlim, -ylim, ylim, -zlim, 2]);
    yLoc = input('distance in front of robot (y): ');
    xLoc = input('distance left (-) or right (+) of the robot (x): ');
    zLoc = input('distance below the robot (z): ');
    fprintf('\n');
    fprintf('\n');
    pingerLoc = [xLoc, yLoc, -zLoc];
    plot3(pingerLoc(:, 1), pingerLoc(:, 2), pingerLoc(:, 3), 'r*')
    hold off
    %the number of pinger to alocate to find distance and toa easier
    [r, c] = size(cd);
    dist = ones(r, 1);
    for i = 1:r
        dist(i)  = sqrt(sum((cd(i,:) - pingerLoc).^2));
    end
    toa = dist./SpeedOfSound;
    toaAct = [toa(2) - toa(1); toa(3) - toa(4)];
    toaCalc = [signalToa2(toaAct(1)); signalToa2(toaAct(2))];
        
    %calculating and printing percent error of toa
    toaErr = (abs(toaAct) - abs(toaCalc))./abs(toaAct) * 100;
    table = [toaAct'; toaCalc'; toaErr'];
    %fprintf('expected toa %10.9f\ncalculated toa %10.9f\n percent error %4.3f \n', table);
    fprintf('\n');
    %%
    % for actual acoustics D is hardcoded, this is the distance between the
    % hydrophones
    sideToSideD = sqrt(sum((cd(3,:) - cd(4,:)).^2))/2;
    inLineD = sqrt(sum((cd(1,:) - cd(2,:)).^2))/2;
    
    % side to side 
    sideToSideA = (toaAct(2)) * SpeedOfSound/2;
    sideToSideASig = toaCalc(2) * SpeedOfSound/2;
    sideToSideB = sqrt(sideToSideD^2 - sideToSideA^2);
    sideToSideBSig = sqrt(sideToSideD^2 - sideToSideASig^2);
    
    %in line 
    inLineA = (toaAct(1)) * SpeedOfSound/2;
    inLineASig = toaCalc(1) * SpeedOfSound/2;
    inLineB = sqrt(inLineD^2 - inLineA^2);
    inLineBSig = sqrt(inLineD^2 - inLineASig^2);
    
    %yaw calculations
    yawCalcSig= atand(sideToSideBSig/sideToSideASig);
    yawCalc = atand(sideToSideB/sideToSideA);
    yawAct = atand(pingerLoc(1,1)/pingerLoc(1,2));
    fprintf('expected Yaw: %3.2f\n', yawAct);
    %fprintf('TOA Yaw no signal: %3.2f\n', yawCalc + 90);
    fprintf('TOA Yaw from signal: %3.2f\n', yawCalcSig + 90);
    fprintf('\n');
    
    % pitch calculations
    pitchCalc= atand(inLineB/inLineA);
    pitchCalcSig = atand(inLineBSig/inLineASig);
    pitchActZY = atand(pingerLoc(1,3)/pingerLoc(1,2));
    pitchActR = atand(pingerLoc(1,3)/sqrt(sum(pingerLoc(1:2).^2)));
    fprintf('expected Pitch: %3.2f\n', 90 - abs(pitchActZY));
    %fprintf('TOA Pitch no signal: %3.2f\n', 90 + (pitchCalc)  );
    fprintf('TOA Pitch from signal: %3.2f\n', 90 + (pitchCalcSig) );
    x = input('enter 1 to insert a new pinger location, enter 0 to quit: ');
end
