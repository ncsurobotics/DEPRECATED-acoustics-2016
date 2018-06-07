function result = toaSimulation(xLoc, yLoc, zLoc)

%constants
SpeedOfSound = 1484;
cd = [0, -.1, 0; 0, -.119, 0; .019/2, 0, 0; -.019/2, 0, 0];


pingerLoc = [xLoc, yLoc, zLoc];
%the number of pinger to alocate to find distance and toa easier
[r, c] = size(cd);
dist = ones(r, 1);
for i = 1:r
    dist(i)  = sqrt(sum((cd(i,:) - pingerLoc).^2));
end
toa = dist./SpeedOfSound;
toaAct = [toa(2) - toa(1); toa(3) - toa(4)];
toaCalc = [signalToa2(toaAct(1)); signalToa2(toaAct(2))];

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

%printing input x
%fprintf('X=%d Y=%d Z=%d\n', pingerLoc);
%yaw calculations
%modifying B to have correct forward and backward
front = inLineASig/abs(inLineASig);
yawCalcSig= atan2d(-1 * sideToSideASig, front * sideToSideBSig);
yawCalc =  atan2d(-1 * sideToSideA,  front * sideToSideB);
yawAct = atan2d(pingerLoc(1,1), pingerLoc(1,2));
%fprintf('expected Yaw: %3.2f\n', yawAct);
%fprintf('TOA Yaw 0 error: %3.2f\n', yawCalc);
%fprintf('TOA Yaw from signal: %3.2f\n', yawCalcSig);
%fprintf('\n');

% pitch calculations
%pitchCalc= atan2d(inLineA, inLineB);
%pitchCalcSig = atan2d(inLineASig, inLineBSig);
pitchActZY = atan2d(pingerLoc(2), -1 * pingerLoc(3));
%fprintf('expected Pitch: %3.2f\n', pitchActZY);
%fprintf('TOA Pitch 0 error: %3.2f\n', pitchCalc);
%fprintf('TOA Pitch from signal: %3.2f\n', pitchCalcSig);

result = struct();
result.yaw = yawCalcSig;
%result.pitch = pitchCalcSig;


end