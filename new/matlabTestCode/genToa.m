function saveValues = genToa(toa1, toa2)

% frequency values are read in at in hz
Fs = 1 * 10^6;

% number of values read in
M = 1000;

% period of read in values 
T = 1/(Fs);
% time axis 
t = (0:(2*M)-1) * T;
%% making the y axis, acoustic wave read in
% frequency of wave from ping in ohz
pf = 22* 10^3;
offset = round(toa1/T);
offset2 = round(toa2/T);
index = randi([M*.5, M]);
index2 = round(index + offset);
index3 = round(index + offset2);
t1 = t(index:(M+index));
t2 = t(index2:(M+index2));
t3 = t(index3:(M+index3));


% the input read in from the hydrophone, assuming 0 offset
signal = [cos(2 * pi * ( pf) * t1); cos(2 * pi * pf * t2); 
          cos(2 * pi * ( pf) * t1); cos(2 * pi * pf * t3)];




end