function calcToa = signalToa(toa)
%% making the time axis

% frequency values are read in at in hz
Fs = 100 * 10^3;
% number of values read in
M = 100;
% period of read in values 
T = 1/(Fs);
% time axis 
t = (0:M-1) * T;
%% making the y axis, acoustic wave read in
% frequency of wave from ping in hz
pf = 22* 10^3;

% the input read in from the hydrophone, assuming 0 offset
signal = [cos(2 * pi * ( pf) * t); cos(2 * pi * pf * (t + toa))];
%% plotting the output wave
figure()

plot(t, signal(1,:), t, signal(2,:));
title('plot of signal')
ylabel('amplitude of sign')
xlabel('time in secconds')
%%
Y = [fft(signal(1,:));fft(signal(2,:))];
[~,i] = max(abs(Y'));
Y(2, i(2));
Y(1, i(1));
calcToa = (angle(Y(2, i(2))) - angle(Y(1, i(1))))/(pf * 2 * pi); 
end


