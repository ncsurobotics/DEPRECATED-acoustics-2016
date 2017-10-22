function testToa3d(toa)
% all units are in meters
SpeedOfSound = 1484;


% matrix for doing math, lenght of vector greater than axis because it gets
% moved
% location of each hydrophone in 3d space, essentially the locaiton of the
% robot
cd = [0, -.1, 0; 0, -.119, 0; .019/2, 0, 0; -.019/2, 0, 0];
% plotting the hydrophone locations

%the number of pinger to alocate to find distance and toa easier
toaCalc = [sigToa(toa(:, 2), toa(:, 1), '2', '1') ; sigToa(toa(:, 3), toa(:, 4), '3', '4') ];

%%
% for actual acoustics D is hardcoded, this is the distance between the
% hydrophones
sideToSideD = sqrt(sum((cd(3,:) - cd(4,:)).^2))/2;
inLineD = sqrt(sum((cd(1,:) - cd(2,:)).^2))/2;

% side to side
sideToSideASig = toaCalc(2) * SpeedOfSound/2;
sideToSideBSig = sqrt(sideToSideD^2 - sideToSideASig^2);

%in line
inLineASig = toaCalc(1) * SpeedOfSound/2;
inLineBSig = sqrt(inLineD^2 - inLineASig^2);

clc

%yaw calculations
%modifying B to have correct forward and backward
fprintf('sideA: %10.8f\n', sideToSideASig)
fprintf('sideB: %10.8f\n', sideToSideBSig)
fprintf('sideT: %10.8f\n', toaCalc(2))

try
    front = 1; %inLineASig/abs(inLineASig);
    yawCalcSig= atan2d(-1 * sideToSideASig, front * sideToSideBSig);
    fprintf('TOA Yaw from signal: %3.2f\n', yawCalcSig);
    fprintf('\n');
catch
    fprintf('ERROR: could not cacluclate yaw\n\n')
    
end

% pitch calculations
fprintf('inLineT: %10.8f\n', toaCalc(1))
fprintf('inLineA: %10.8f\n', inLineASig)
fprintf('inLineB: %10.8f\n', inLineBSig)

try
    pitchCalcSig = atan2d(inLineASig, inLineBSig);
    fprintf('TOA Pitch from signal: %3.2f\n', pitchCalcSig);
catch
     fprintf('ERROR: could not cacluclate pitch\n')
 
end   
end