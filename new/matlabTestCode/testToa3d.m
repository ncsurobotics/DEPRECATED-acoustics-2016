function out = testToa3d(toa, Fs, pf, db)
% all units are in meters
SpeedOfSound = 1484;


% matrix for doing math, lenght of vector greater than axis because it gets
% moved
% location of each hydrophone in 3d space, essentially the locaiton of the
% robot
cd = [0, -.1, 0; 0, -.119, 0; .019/2, 0, 0; -.019/2, 0, 0];
% plotting the hydrophone locations

%the number of pinger to alocate to find distance and toa easier
toaCalc = [sigToa(toa(:, 2), toa(:, 1), '2', '1', Fs, pf, db) ; sigToa(toa(:, 3), toa(:, 4), '3', '4', Fs, pf, db) ];

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


%yaw calculations
out = {};
try
    front = 1; %inLineASig/abs(inLineASig);
    yawCalcSig= atan2d(-1 * sideToSideASig, front * sideToSideBSig);
    out{1} = sprintf('%d, %10.2e,%10.2e, %10.2e,%10.3f\n', length(toa), toaCalc(2), sideToSideASig, sideToSideBSig, yawCalcSig);
catch
    out{1} = sprintf('%d, %10.2e,%10.2e,%10.2e,%10.3f\n', length(toa), toaCalc(2), sideToSideASig, sideToSideBSig, 0);
end

% pitch calculations
try
    pitchCalcSig = atan2d(inLineASig, inLineBSig);
    out{2} = sprintf('%d, %10.2e,%10.2e,%10.2e,%10.3f\n', length(toa), toaCalc(1), inLineASig, inLineBSig, pitchCalcSig);
catch
    out{2} = sprintf('%d, %10.2e,%10.2e,%10.2e,%10.3f\n', length(toa), toaCalc(1), inLineASig, inLineBSig, 0);
end   
if db
    fprintf('length, toaCalc, a, b, yaw\n');
    fprintf(out{1});
    fprintf('length, toaCalc, a, b, pitch\n');
    fprintf(out{2});
end

end